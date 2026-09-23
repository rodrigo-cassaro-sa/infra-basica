// DESTINO: src/utils/format.ts
// Formatação para a UI. API e banco usam ISO 8601; a conversão acontece só aqui.
// Formatadores criados uma vez (instanciar Intl a cada render é caro em listas).
// Projeto multi-idioma: troque LOCALE pelo idioma atual (skill ux-ui, i18n.md §5).
const LOCALE = "pt-BR";

const currency = new Intl.NumberFormat(LOCALE, { style: "currency", currency: "BRL" });
const number = new Intl.NumberFormat(LOCALE);
const percent = new Intl.NumberFormat(LOCALE, { style: "percent", maximumFractionDigits: 1 });
const date = new Intl.DateTimeFormat(LOCALE, { dateStyle: "short" });
const dateTime = new Intl.DateTimeFormat(LOCALE, { dateStyle: "short", timeStyle: "short" });
const relative = new Intl.RelativeTimeFormat(LOCALE, { numeric: "auto" });

const toDate = (value: Date | string) => (typeof value === "string" ? new Date(value) : value);
const isValid = (d: Date) => !Number.isNaN(d.getTime());

/** 1250 → "R$ 1.250,00". Moeda é do negócio, não do idioma. */
export const formatMoney = (value: number) => currency.format(value);
export const formatNumber = (value: number) => number.format(value);
/** 0.105 → "10,5%" */
export const formatPercent = (ratio: number) => percent.format(ratio);

export function formatDate(value: Date | string) {
  const d = toDate(value);
  return isValid(d) ? date.format(d) : "";
}

export function formatDateTime(value: Date | string) {
  const d = toDate(value);
  return isValid(d) ? dateTime.format(d) : "";
}

/** "há 5 minutos", "ontem", "em 2 dias". Mostre a data completa em accessibilityLabel/tooltip. */
export function formatRelative(value: Date | string, now = new Date()) {
  const d = toDate(value);
  if (!isValid(d)) return "";
  const minutes = Math.round((d.getTime() - now.getTime()) / 60_000);
  if (Math.abs(minutes) < 60) return relative.format(minutes, "minute");
  if (Math.abs(minutes) < 1_440) return relative.format(Math.round(minutes / 60), "hour");
  return relative.format(Math.round(minutes / 1_440), "day");
}
