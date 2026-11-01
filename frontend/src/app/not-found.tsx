import Link from "next/link";
import s from "@/components/Site.module.css";
export default function NotFound() {
  return (
    <section className={s.section}>
      <p>404</p>
      <h1>Страница не найдена</h1>
      <Link href="/" className={s.button}>
        На главную
      </Link>
    </section>
  );
}
