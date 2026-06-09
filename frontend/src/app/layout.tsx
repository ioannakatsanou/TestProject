import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ask Greece for Business",
  description:
    "AI-powered public-sector digital transformation intelligence over Greek government decisions.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
