import { notFound } from "next/navigation";
import Link from "next/link";
import { fetchRental, safeMedia } from "@/lib/api";
import s from "@/components/Site.module.css";
export const dynamic = "force-dynamic";
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const item = await fetchRental((await params).slug);
  return { title: item?.title || "Помещение не найдено" };
}
export default async function RentalDetail({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const item = await fetchRental((await params).slug);
  if (!item) notFound();
  return (
    <section className={s.section}>
      <Link href="/rentals">← Все помещения</Link>
      <h1>{item.title}</h1>
      <p>{item.available ? "Доступно для аренды" : "Сейчас занято"}</p>
      {safeMedia(item.image_path) && (
        <img
          className={s.detailImage}
          src={safeMedia(item.image_path)}
          alt={item.title}
          width={1200}
          height={800}
        />
      )}
      <p className={s.prose}>{item.description}</p>
      <dl className={s.specs}>
        {item.building && (
          <>
            <dt>Здание</dt>
            <dd>{item.building}</dd>
          </>
        )}
        {item.area != null && (
          <>
            <dt>Площадь</dt>
            <dd>{item.area} м²</dd>
          </>
        )}
        {item.floor != null && (
          <>
            <dt>Этаж</dt>
            <dd>{item.floor}</dd>
          </>
        )}
        <dt>Стоимость</dt>
        <dd>
          {item.monthly_price == null
            ? "По запросу"
            : `${item.monthly_price.toLocaleString("ru-RU")} ₽ / месяц`}
        </dd>
      </dl>
      <Link
        className={s.button}
        href={`/contacts?service=rent&room=${encodeURIComponent(item.title)}`}
      >
        Уточнить условия ↗
      </Link>
    </section>
  );
}
