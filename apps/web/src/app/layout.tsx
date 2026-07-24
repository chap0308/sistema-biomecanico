import type { Metadata } from "next";
import "./globals.css";
import { Archivo, IBM_Plex_Mono } from "next/font/google";
import { cn } from "@/lib/utils";

const archivo = Archivo({
  subsets: ["latin"],
  variable: "--font-sans",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: {
    default: "Laboratorio de sentadilla bilateral",
    template: "%s | Laboratorio de sentadilla",
  },
  description:
    "Interfaz de investigación para el análisis interpretable de sentadilla bilateral.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={cn("font-sans", archivo.variable, ibmPlexMono.variable)}
    >
      <body className="min-h-dvh antialiased">{children}</body>
    </html>
  );
}
