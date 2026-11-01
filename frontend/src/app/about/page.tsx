import type { Metadata } from "next";
import CTA from "@/components/CTA";
import s from "@/components/Site.module.css";
export const metadata: Metadata = { title: "О компании" };
export default function About() {
  return (
    <>
      <section className={s.pageHead}>
        <p className={s.eyebrow}>Мабетэк</p>
        <h1>О компании</h1>
        <p>Территория для бизнеса и железнодорожной логистики в Хабаровске.</p>
      </section>
      <section className={s.section}>
        <h2>Площадка рядом с Хабаровском-1</h2>
        <div className={s.twoColumns}>
          <p>
            Работаем в двух направлениях: предоставление офисных и складских
            помещений и организация обработки вагонов на территории компании.
          </p>
          <p>
            Обсуждаем задачу напрямую: какие помещения нужны, какой груз
            предстоит принять и какие работы необходимо организовать.
          </p>
        </div>
        <p>
          Характеристики площадки и документы предоставляем при согласовании
          сотрудничества.
        </p>
      </section>
      <CTA />
    </>
  );
}
