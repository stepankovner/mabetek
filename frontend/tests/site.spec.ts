import { test, expect } from "@playwright/test";
for (const [url, heading] of [
  ["/", "Железнодорожные услуги"],
  ["/rail", "Железнодорожные услуги"],
  ["/rentals", "Аренда помещений"],
  ["/about", "О компании"],
  ["/contacts", "Контакты"],
]) {
  test(`page ${url}`, async ({ page }) => {
    await page.goto(url);
    await expect(page.locator("h1")).toContainText(heading);
    await expect(page).toHaveTitle(/Мабетэк/);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
  });
}
test("both services and mobile navigation", async ({ page, isMobile }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Два направления работы" }),
  ).toBeVisible();
  if (isMobile)
    await page.getByRole("button", { name: "Открыть меню" }).click();
  await page
    .getByRole("navigation", { name: "Основная навигация" })
    .getByRole("link", { name: "Аренда" })
    .click();
  await expect(page).toHaveURL(/rentals/);
});
test("lead success and server failure preserve form", async ({ page }) => {
  await page.route("**/api/config", (r) =>
    r.fulfill({ json: { leads_enabled: true, privacy_version: "test" } }),
  );
  await page.goto("/contacts");
  await page.getByLabel("Имя").fill("Степан");
  await page.getByLabel("Телефон или email").fill("test@example.com");
  await page.getByLabel("Сообщение").fill("Выгрузка вагона");
  await page.getByLabel(/согласие/).check();
  await page.route("**/api/leads", (r) =>
    r.fulfill({ status: 503, json: { detail: "Unavailable" } }),
  );
  await page.getByRole("button", { name: "Отправить заявку" }).click();
  await expect(page.getByRole("alert")).toContainText("Не удалось");
  await expect(page.getByLabel("Имя")).toHaveValue("Степан");
  await page.route("**/api/leads", (r) =>
    r.fulfill({ status: 201, json: { id: "example" } }),
  );
  await page.getByRole("button", { name: "Отправить заявку" }).click();
  await expect(page.getByRole("status")).toContainText("Заявка принята");
});
test("unconfigured form never pretends to send", async ({ page }) => {
  await page.route("**/api/config", (r) =>
    r.fulfill({ json: { leads_enabled: false } }),
  );
  await page.goto("/contacts");
  await expect(
    page.getByText("Приём заявок через сайт пока не открыт."),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Отправить заявку" }),
  ).toHaveCount(0);
});
test("unknown page returns 404", async ({ page }) => {
  const response = await page.goto("/does-not-exist");
  expect(response?.status()).toBe(404);
});
