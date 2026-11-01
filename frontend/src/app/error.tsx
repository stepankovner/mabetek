"use client";
import s from "@/components/Site.module.css";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <section className={s.section}>
      <h1>Не удалось загрузить страницу</h1>
      <p>Попробуйте ещё раз немного позже.</p>
      <button className={s.button} onClick={reset}>
        Повторить
      </button>
    </section>
  );
}
