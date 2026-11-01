import Link from "next/link";
import s from "./Site.module.css";
export default function CTA() {
  return (
    <section className={s.cta}>
      <div className={s.glass}>
        <h2>Обсудим вашу задачу</h2>
        <p>
          Железнодорожные услуги или помещение для бизнеса — расскажите, что вам
          нужно.
        </p>
        <Link href="/contacts" className={s.outlineButton}>
          Связаться с нами ↗
        </Link>
      </div>
    </section>
  );
}
