import type { Metadata } from "next";
import Link from "next/link";
import { fetchRentals, safeMedia, type Rental } from "@/lib/api";
import s from "@/components/Site.module.css";
export const metadata: Metadata = { title: "Аренда помещений" };
export const dynamic = "force-dynamic";
export default async function Rentals({
  searchParams,
}: {
  searchParams: Promise<{ kind?: string }>;
}) {
  const { kind } = await searchParams;
  let items: Rental[] = [];
  let failed = false;
  try {
    items = await fetchRentals(kind);
  } catch {
    failed = true;
  }
  return (
    <>
      <section className={s.pageHead}>
        <p className={s.eyebrow}>Для вашего бизнеса</p>
        <h1>Аренда помещений</h1>
        <p>Офисы и складские помещения на территории Мабетэк в Хабаровске.</p>
      </section>
      <section className={s.section}>
        <nav className={s.filters} aria-label="Тип помещения">
          {[
            ["", "Все помещения"],
            ["office", "Офисы"],
            ["warehouse", "Склады"],
          ].map(([value, label]) => (
            <Link
              key={value}
              href={value ? `/rentals?kind=${value}` : "/rentals"}
              aria-current={(kind || "") === value ? "page" : undefined}
            >
              {label}
            </Link>
          ))}
        </nav>
        {failed ? (
          <p role="alert">
            Каталог временно недоступен. Попробуйте зайти позже или свяжитесь с
            нами.
          </p>
        ) : items.length === 0 ? (
          <div className={s.notice}>
            <h2>Подберём помещение под вашу задачу</h2>
            <p>
              Карточки помещений готовятся к публикации. Свяжитесь с нами, чтобы
              уточнить наличие и условия аренды.
            </p>
          </div>
        ) : (
          <div className={s.rentalGrid}>
            {items.map((item) => (
              <article key={item.slug} className={s.rentalCard}>
                {safeMedia(item.image_path) && (
                  <img
                    src={safeMedia(item.image_path)}
                    alt={item.title}
                    width={640}
                    height={420}
                  />
                )}
                <p className={s.eyebrow}>
                  {item.kind === "office" ? "Офис" : "Склад"} ·{" "}
                  {item.available ? "Свободно" : "Занято"}
                </p>
                <h2>
                  <Link href={`/rentals/${item.slug}`}>{item.title}</Link>
                </h2>
                <p>
                  {item.building}
                  {item.area != null && ` · ${item.area} м²`}
                </p>
                <p>
                  {item.monthly_price == null
                    ? "Стоимость по запросу"
                    : `${item.monthly_price.toLocaleString("ru-RU")} ₽ / месяц`}
                </p>
              </article>
            ))}
          </div>
        )}
        <Link href="/contacts?service=rent" className={s.button}>
          Обсудить аренду ↗
        </Link>
      </section>
    </>
  );
}
