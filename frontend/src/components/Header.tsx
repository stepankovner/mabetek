"use client";
import Link from "next/link";
import { useState } from "react";
import { usePathname } from "next/navigation";
import { navigation } from "@/content/company";
import s from "./Site.module.css";
export default function Header() {
  const [open, setOpen] = useState(false);
  const path = usePathname();
  return (
    <header className={s.header}>
      <Link
        href="/"
        className={s.logo}
        aria-label="Мабетэк — главная"
        onClick={() => setOpen(false)}
      >
        МАБЕТЭК
      </Link>
      <button
        className={s.menuButton}
        aria-expanded={open}
        aria-controls="main-nav"
        aria-label={open ? "Закрыть меню" : "Открыть меню"}
        onClick={() => setOpen(!open)}
      >
        {open ? "Закрыть" : "Меню"}{" "}
        <span aria-hidden="true">{open ? "×" : "+"}</span>
      </button>
      <nav
        id="main-nav"
        aria-label="Основная навигация"
        className={`${s.nav} ${open ? s.navOpen : ""}`}
      >
        {navigation.map((item) => (
          <Link
            href={item.href}
            key={item.href}
            aria-current={path.startsWith(item.href) ? "page" : undefined}
            onClick={() => setOpen(false)}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
