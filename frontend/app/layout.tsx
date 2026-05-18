import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "RecruitAI — AI-Powered Recruitment Optimization",
  description:
    "Dynamically personalize resumes, score ATS compatibility, match jobs, and optimize application strategies with AI.",
  keywords: ["recruitment", "AI", "resume", "ATS", "job matching", "career"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <body style={{ fontFamily: "var(--font-inter), sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
