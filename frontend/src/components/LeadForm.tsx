"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import s from "./Site.module.css";
type Config = { leads_enabled: boolean; privacy_version: string };
export default function LeadForm({
  service = "rail",
  message = "",
}: {
  service?: string;
  message?: string;
}) {
  const [config, setConfig] = useState<Config | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [status, setStatus] = useState<"idle" | "sending" | "success">("idle");
  const [error, setError] = useState("");
  const retry = useRef<{ body: string; key: string } | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/config", { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error();
        return r.json();
      })
      .then(setConfig)
      .catch((e) => {
        if (e.name !== "AbortError") setLoadError(true);
      });
    return () => controller.abort();
  }, []);
  if (loadError)
    return (
      <p role="alert">
        Форма временно недоступна. Попробуйте обновить страницу.
      </p>
    );
  if (!config) return <p role="status">Загрузка формы…</p>;
  if (!config.leads_enabled)
    return <p>Приём заявок через сайт пока не открыт.</p>;
  if (status === "success")
    return (
      <div role="status" className={s.notice}>
        <h3>Заявка принята</h3>
        <p>Спасибо. Мы получили ваше обращение.</p>
        <button
          className={s.button}
          onClick={() => {
            setStatus("idle");
            retry.current = null;
          }}
        >
          Новая заявка
        </button>
      </div>
    );
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (status === "sending") return;
    const data = new FormData(event.currentTarget);
    const body = JSON.stringify({
      name: data.get("name"),
      contact: data.get("contact"),
      service: data.get("service"),
      message: data.get("message"),
      consent: data.get("consent") === "on",
    });
    if (retry.current?.body !== body)
      retry.current = { body, key: crypto.randomUUID() };
    setStatus("sending");
    setError("");
    try {
      const response = await fetch("/api/leads", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": retry.current!.key,
        },
        body,
        signal: AbortSignal.timeout(15000),
      });
      if (!response.ok) {
        if (response.status === 429)
          throw new Error("Слишком много обращений. Попробуйте позже.");
        if (response.status === 422)
          throw new Error("Проверьте имя и контакт: нужен телефон или email.");
        throw new Error(
          "Не удалось отправить заявку. Ваши данные остались в форме — попробуйте ещё раз.",
        );
      }
      setStatus("success");
    } catch (e) {
      setStatus("idle");
      setError(
        e instanceof Error && !["TimeoutError", "TypeError"].includes(e.name)
          ? e.message
          : "Не удалось отправить заявку. Попробуйте ещё раз.",
      );
    }
  }
  return (
    <form onSubmit={submit} className={s.form}>
      <div className={s.formRow}>
        <label>
          Имя
          <input name="name" autoComplete="name" required maxLength={100} />
        </label>
        <label>
          Телефон или email
          <input name="contact" autoComplete="email" required maxLength={254} />
        </label>
      </div>
      <label>
        Направление
        <select name="service" defaultValue={service}>
          <option value="rail">Железнодорожные услуги</option>
          <option value="rent">Аренда помещений</option>
          <option value="other">Другой вопрос</option>
        </select>
      </label>
      <label>
        Сообщение
        <textarea
          name="message"
          rows={4}
          maxLength={4000}
          defaultValue={message}
        />
      </label>
      <label className={s.consent}>
        <input name="consent" type="checkbox" required />
        <span>
          Даю согласие на обработку персональных данных согласно{" "}
          <Link href="/privacy" target="_blank">
            условиям обработки
          </Link>
          .
        </span>
      </label>
      {error && (
        <p role="alert" className={s.error}>
          {error}
        </p>
      )}
      <button className={s.button} disabled={status === "sending"}>
        {status === "sending" ? "Отправляем…" : "Отправить заявку"}
      </button>
    </form>
  );
}
