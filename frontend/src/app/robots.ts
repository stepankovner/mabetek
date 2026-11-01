import type { MetadataRoute } from "next";
export default function robots(): MetadataRoute.Robots {
  const indexable = process.env.SITE_INDEXABLE === "true";
  return {
    rules: {
      userAgent: "*",
      ...(indexable
        ? { allow: "/", disallow: ["/admin", "/api"] }
        : { disallow: "/" }),
    },
    ...(indexable ? { sitemap: `${process.env.SITE_URL}/sitemap.xml` } : {}),
  };
}
