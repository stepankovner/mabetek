import type { Metadata } from "next";
import LeadForm from "@/components/LeadForm";
import { company } from "@/content/company";
import s from "@/components/Site.module.css";
export const metadata: Metadata = { title: "Контакты" };
export default async function Contacts({
  searchParams,
}: {
  searchParams: Promise<{ service?: string; room?: string }>;
}) {
  const query = await searchParams;
  const service =
    query.service === "rent"
      ? "rent"
      : query.service === "other"
        ? "other"
        : "rail";
  return (
    <>
      <section className={s.pageHead}>
        <p className={s.eyebrow}>На связи</p>
        <h1>Контакты</h1>
        <p>Обсудим выгрузку вагонов или подберём помещение для бизнеса.</p>
      </section>
      <section className={`${s.section} ${s.contactGrid}`}>
        <div>
          <h2>Мабетэк</h2>
          <p>Хабаровск · {company.location}</p>
          {company.address && <p>{company.address}</p>}
          {company.phone && (
            <p>
              <a href={`tel:${company.phone.replace(/[^+\d]/g, "")}`}>
                {company.phone}
              </a>
            </p>
          )}
          {company.email && (
            <p>
              <a href={`mailto:${company.email}`}>{company.email}</a>
            </p>
          )}
          {company.hours && <p>{company.hours}</p>}
          {!company.phone && !company.email && (
            <p>Контактные данные готовятся к публикации.</p>
          )}
        </div>
        <div>
          <h2>Расскажите о задаче</h2>
          <LeadForm
            service={service}
            message={
              query.room
                ? `Интересует помещение: ${query.room.slice(0, 150)}`
                : ""
            }
          />
        </div>
      </section>
    </>
  );
}
