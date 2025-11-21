import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "./auth/AuthContext";

export const metadata: Metadata = {
  title: "Cramify",
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
        {/* AuthProvider wraps entire app so any component can access user state */}
        <AuthProvider>
          <main>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
