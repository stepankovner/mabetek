import type { MetadataRoute } from "next";
export default function sitemap(): MetadataRoute.Sitemap {
  if (process.env.SITE_INDEXABLE !== "true") return [];
  const origin = process.env.SITE_URL;
  return ["", "/rail", "/rentals", "/about", "/contacts"].map((path) => ({
    url: `${origin}${path}`,
  }));
}
