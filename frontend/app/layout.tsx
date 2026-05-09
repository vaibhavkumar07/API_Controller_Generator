import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "API Controller Generator",
  description: "Generate controller code from API endpoint definitions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
