import "server-only";
export type Rental = {
  slug: string;
  title: string;
  kind: "office" | "warehouse";
  building: string;
  description: string;
  area: number | null;
  floor: number | null;
  monthly_price: number | null;
  image_path: string;
  available: boolean;
};
const base = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
export async function fetchRentals(kind?: string): Promise<Rental[]> {
  const query =
    kind === "office" || kind === "warehouse" ? `?kind=${kind}` : "";
  const response = await fetch(`${base}/api/rentals${query}`, {
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok) throw new Error("Rental service unavailable");
  return response.json();
}
export async function fetchRental(slug: string): Promise<Rental | null> {
  const response = await fetch(
    `${base}/api/rentals/${encodeURIComponent(slug)}`,
    { cache: "no-store", signal: AbortSignal.timeout(5000) },
  );
  if (response.status === 404) return null;
  if (!response.ok) throw new Error("Rental service unavailable");
  return response.json();
}
export function safeMedia(path: string): string | undefined {
  return /^\/media\/[a-zA-Z0-9_-]+\.(jpg|jpeg|png|webp)$/.test(path)
    ? path
    : undefined;
}
