import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stock Dashboard",
  description: "Real-time stock quote dashboard powered by Finnhub"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
