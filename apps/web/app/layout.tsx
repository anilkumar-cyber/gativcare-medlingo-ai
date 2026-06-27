import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GativCare MedLingo AI",
  description: "AI Medical Communication Intelligence Platform",
};

// data-theme/data-contrast/data-font-scale are read from user_preferences at shell mount
// (docs/UX_ARCHITECTURE.md#personalization), defaulted here for unauthenticated routes.
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="light">
      <body>{children}</body>
    </html>
  );
}
