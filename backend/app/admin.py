import re
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from sqladmin import Admin, ModelView
from wtforms import DecimalField
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import Response
from .models import Lead, Notification, Rental
from .security import rate_allowed

class RentalAdmin(ModelView, model=Rental):
    name = "Помещение"
    name_plural = "Помещения"
    column_list = [Rental.title, Rental.kind, Rental.building, Rental.available, Rental.published]
    column_searchable_list = [Rental.title, Rental.building]
    column_labels = {"title":"Название", "kind":"Тип", "building":"Здание", "description":"Описание",
        "area":"Площадь, м²", "floor":"Этаж", "monthly_price":"Цена в месяц, ₽", "image_path":"Путь к фото (/media/…)",
        "available":"Свободно", "published":"Опубликовано"}
    form_overrides = {"area": DecimalField}
    form_choices = {"kind": [("office", "Офис"), ("warehouse", "Склад")]}
    async def on_model_change(self, data, model, is_created, request):
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["slug"]):
            raise ValueError("Slug: латинские буквы, цифры и дефис")
        path = data.get("image_path", "") or ""
        if path and not re.fullmatch(r"/media/[a-zA-Z0-9_-]+\.(jpg|jpeg|png|webp)", path):
            raise ValueError("Фото: /media/имя.jpg (также png/webp)")
        if data.get("area") is not None and data["area"] <= 0:
            raise ValueError("Площадь должна быть положительной")
        if data.get("monthly_price") is not None and data["monthly_price"] < 0:
            raise ValueError("Цена не может быть отрицательной")

class LeadAdmin(ModelView, model=Lead):
    name = "Заявка"
    name_plural = "Заявки"
    can_create = False
    can_delete = True
    can_view_details = True
    column_list = [Lead.created_at, Lead.name, Lead.contact, Lead.service, Lead.status]
    column_searchable_list = [Lead.name, Lead.contact]
    form_columns = [Lead.status, Lead.internal_note]
    form_choices = {"status": [("new", "Новая"), ("in_progress", "В работе"), ("closed", "Закрыта")]}
    column_default_sort = (Lead.created_at, True)

class NotificationAdmin(ModelView, model=Notification):
    name_plural = "Уведомления"
    can_create = can_edit = can_delete = False
    column_list = [Notification.lead_id, Notification.attempts, Notification.next_attempt_at, Notification.sent_at, Notification.last_error]

def attach_admin(app, engine, sessions, settings):
    class Auth(AuthenticationBackend):
        async def login(self, request):
            # SQLAdmin invokes this asynchronously; CPU-heavy verification goes off the event loop.
            from starlette.concurrency import run_in_threadpool
            address = request.client.host if request.client else "unknown"
            allowed = await run_in_threadpool(rate_allowed, sessions, settings.secret_key, "login", address, 10, 900)
            if not allowed:
                return Response("Too many attempts", status_code=429, headers={"Retry-After":"900"})
            form = await request.form()
            password = str(form.get("password", ""))
            if len(password) > 1024:
                return False
            try:
                valid = await run_in_threadpool(PasswordHasher().verify, settings.admin_password_hash, password)
            except (VerificationError, InvalidHashError):
                valid = False
            if valid and secrets.compare_digest(str(form.get("username", "")), settings.admin_username):
                request.session.clear()
                request.session["admin"] = settings.admin_username
                # A password change invalidates existing sessions as well.
                request.session["credential"] = settings.admin_password_hash[-20:]
                return True
            return False

        async def logout(self, request):
            request.session.clear()
            return True

        async def authenticate(self, request):
            return request.session.get("admin") == settings.admin_username and request.session.get("credential") == settings.admin_password_hash[-20:]

    auth = Auth(secret_key=settings.secret_key)
    # Explicit cookie settings rather than SQLAdmin's default SessionMiddleware.
    from starlette.middleware import Middleware
    from starlette.middleware.sessions import SessionMiddleware
    auth.middlewares = [Middleware(SessionMiddleware, secret_key=settings.secret_key,
        session_cookie="mabetek_admin", max_age=8*3600, same_site="strict", https_only=settings.secure_cookies)]
    admin = Admin(app, engine, title="Мабетэк", authentication_backend=auth)
    for view in [RentalAdmin, LeadAdmin, NotificationAdmin]:
        admin.add_view(view)
