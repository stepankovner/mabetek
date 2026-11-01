import type { Metadata } from "next";
import Link from "next/link";
import CTA from "@/components/CTA";
import s from "@/components/Site.module.css";
export const metadata: Metadata = { title: "Железнодорожные услуги" };
export default function Rail() {
  return (
    <>
      <section className={s.pageHead}>
        <p className={s.eyebrow}>Хабаровск-1</p>
        <h1>Железнодорожные услуги</h1>
        <p>
          Площадка для работы с вагонами и перегрузки отправлений на
          автомобильный транспорт.
        </p>
        <Link href="/contacts?service=rail" className={s.button}>
          Обсудить выгрузку ↗
        </Link>
      </section>
      <section className={s.section}>
        <h2>Состав работ под вашу задачу</h2>
        <div className={s.twoColumns}>
          <article>
            <h3>Приём и размещение</h3>
            <p>
              Согласуем возможность постановки вагонов на пути территории,
              график и порядок взаимодействия.
            </p>
          </article>
          <article>
            <h3>Разгрузка и перегрузка</h3>
            <p>
              Организуем грузчиков и привлечение техники. Согласуем передачу
              отправлений на автотранспорт заказчика.
            </p>
          </article>
        </div>
      </section>
      <section className={s.mutedSection}>
        <h2>Что нужно для расчёта</h2>
        <ol className={s.steps}>
          <li>
            <b>Вагоны и груз</b>
            <p>
              Тип и количество вагонов, характер груза, вес, упаковка и
              особенности обработки.
            </p>
          </li>
          <li>
            <b>График</b>
            <p>
              Плановая дата прибытия, разовая или регулярная работа, время
              подачи автомобилей.
            </p>
          </li>
          <li>
            <b>Состав услуг</b>
            <p>
              Разгрузка, техника, временное размещение груза и необходимые
              документы.
            </p>
          </li>
        </ol>
        <p>
          Возможность приёма конкретного типа вагонов и условия работ
          подтверждаем до заключения договора.
        </p>
      </section>
      <CTA />
    </>
  );
}
