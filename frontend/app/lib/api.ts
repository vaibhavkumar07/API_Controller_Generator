const DEFAULT_API_BASE = "http://localhost:5002";

export const API_BASE =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_BASE) ||
  DEFAULT_API_BASE;

export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE.replace(/\/$/, "")}${normalized}`;
}

export const DOCS_URL = apiUrl("/api/docs");
export const GENERATE_URL = apiUrl("/api/v1/generate");
export const XML_TO_HTML_URL = apiUrl("/api/v1/xml-to-html");
