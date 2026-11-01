import Link from "next/link";
import CTA from "@/components/CTA";
import s from "@/components/Site.module.css";
export default function Home() {
  return (
    <>
      <section className={s.hero}>
        <div className={s.heroContent}>
          <p className={s.eyebrow}>Мабетэк · Хабаровск</p>
          <h1>
            Железнодорожные услуги
            <br />и аренда помещений
          </h1>
          <p>
            Приём и обработка вагонов, офисные и складские помещения у станции
            Хабаровск-1.
          </p>
          <Link href="/contacts" className={s.lightButton}>
            Обсудить задачу ↗
          </Link>
        </div>
      </section>
      <section className={s.section}>
        <p className={s.eyebrow}>Своя территория</p>
        <h2>Два направления работы</h2>
        <div className={s.twoColumns}>
          <article>
            <h3>Железнодорожные услуги</h3>
            <p>
              Постановка вагонов на территорию и организация разгрузки. Состав
              работ, технику и график согласуем под вашу задачу.
            </p>
            <Link href="/rail" className={s.textLink}>
              Подробнее об услугах ↗
            </Link>
          </article>
          <article>
            <h3>Аренда помещений</h3>
            <p>
              Офисные и складские помещения для бизнеса. Поможем подобрать
              вариант и обсудить условия размещения.
            </p>
            <Link href="/rentals" className={s.textLink}>
              Посмотреть помещения ↗
            </Link>
          </article>
        </div>
        <figure className={s.offsetFigure}>
          <div
            className={s.referencePhoto}
            role="img"
            aria-label="Иллюстрация транспортной площадки"
          />
          <figcaption>Пространство для работы и логистики</figcaption>
        </figure>
      </section>
      <section className={s.section}>
        <p className={s.eyebrow}>Возможности площадки</p>
        <h2>Что предлагает Мабетэк</h2>
        <div className={s.cards}>
          <article>
            <h3>Пути на территории</h3>
            <p>Железнодорожная инфраструктура рядом со станцией Хабаровск-1.</p>
          </article>
          <article>
            <h3>Офисы и склад</h3>
            <p>Помещения для ежедневной работы и размещения бизнеса.</p>
          </article>
          <article>
            <h3>Организация работ</h3>
            <p>
              Согласование разгрузки, привлечение грузчиков и необходимой
              техники.
            </p>
          </article>
        </div>
      </section>
      <CTA />
    </>
  );
}
