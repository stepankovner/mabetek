import { company } from "@/content/company";
import s from "@/components/Site.module.css";
export const metadata = { title: "Обработка персональных данных" };
export default function Privacy() {
  return (
    <section className={s.section}>
      <h1>Обработка персональных данных</h1>
      <div className={s.prose}>
        {company.privacyText ||
          "Условия обработки персональных данных готовятся к публикации. До их утверждения приём заявок через сайт отключён."}
      </div>
    </section>
  );
}
