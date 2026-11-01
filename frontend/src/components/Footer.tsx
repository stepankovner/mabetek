import Link from "next/link";
import { company, navigation } from "@/content/company";
import s from "./Site.module.css";
export default function Footer() {
  return (
    <footer className={s.footer}>
      <div>
        <p>Хабаровск</p>
        <p>{company.location}</p>
        {company.phone && (
          <a href={`tel:${company.phone.replace(/[^+\d]/g, "")}`}>
            {company.phone}
          </a>
        )}
        {company.email && (
          <a href={`mailto:${company.email}`}>{company.email}</a>
        )}
      </div>
      <Link href="/" className={s.wordmark}>
        МАБЕТЭК
      </Link>
      <nav aria-label="Навигация в подвале">
        {navigation.map((item) => (
          <Link key={item.href} href={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>
      <div className={s.footerBottom}>
        <span>© {new Date().getFullYear()} Мабетэк</span>
        <Link href="/privacy">Персональные данные</Link>
      </div>
    </footer>
  );
}
