import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cramify - AI Cheat Sheet Generator",
  description: "Generate dense 2-page cheat sheets from lecture PDFs using AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        {/* You could add a navbar here that appears on all pages */}
        <main>{children}</main>
        {/* You could add a footer here that appears on all pages */}
      </body>
    </html>
  );
}
