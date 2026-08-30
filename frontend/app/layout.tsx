import "./globals.css";
import React from "react";

export const metadata = {
  title: "SENTINEL-RAG",
  description: "Self-Evaluating Evidence-Navigating, Trust-Calibrated RAG System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
