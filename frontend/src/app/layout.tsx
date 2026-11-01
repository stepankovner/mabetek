import type { Metadata } from "next";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import "./globals.css";
export const metadata: Metadata = {
  metadataBase: new URL(process.env.SITE_URL || "http://localhost:3000"),
  title: {
    default: "Мабетэк — железнодорожные услуги и аренда в Хабаровске",
    template: "%s — Мабетэк",
  },
  description:
    "Железнодорожные услуги, офисные и складские помещения рядом со станцией Хабаровск-1.",
  robots:
    process.env.SITE_INDEXABLE === "true"
      ? { index: true, follow: true }
      : { index: false, follow: false },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>
        <a href="#main" className="skip-link">
          Перейти к содержимому
        </a>
        <Header />
        <main id="main">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
