// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { cn } from "@/lib/utils";
import Image from "next/image";
import "@/app/globals.css";
import { Globe, Phone } from "lucide-react";
import { KioskProvider } from "@/context/KioskProvider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Medical Kiosk App",
  description:
    "Ứng dụng Next.js cho kiosk y tế tương tác, tối ưu hóa trải nghiệm chăm sóc sức khỏe.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body
        // chuyển h-screen -> min-h-screen và bỏ overflow-hidden
        className={cn(
          inter.variable,
          "antialiased min-h-screen w-screen flex flex-col"
        )}
      >
        <KioskProvider>
          {/* HEADER */}
          <header className="h-24 flex items-center justify-between px-6 shadow-md bg-white shrink-0">
            <div className="flex items-center gap-3">
              <Image src="/logo.svg" alt="Logo" width={56} height={56} />
              <h1 className="text-2xl font-bold font-[Inter] text-[#053345]">
                HỆ THỐNG ĐĂNG KÝ KHÁM CHỮA BỆNH
              </h1>
            </div>
            <div className="flex items-center">
              <Image
                src="/logo.png"
                alt="Logo Cybertech"
                width={100}
                height={100}
              />
            </div>
          </header>

          {/* MAIN */}
          {/* important: min-h-0 để flex child có thể scroll; overflow-auto cho scroll khi nội dung vượt */}
          <main className="flex-1 flex items-center bg-[#ECFEFF] px-12 overflow-auto min-h-0">
            {children}
          </main>

          {/* FOOTER */}
          <footer className="h-48 bg-white shadow-inner px-6 flex flex-col items-center justify-center text-[#053345] text-base shrink-0">
            <div className="flex items-center gap-4 mb-4">
              <Phone className="w-7 h-7 text-[#053345]" />
              <span className="text-2xl">
                Số điện thoại: <strong className="font-bold">1900 0909</strong>
              </span>
            </div>
            <div className="flex items-center gap-4 mb-4">
              <Globe className="w-7 h-7 text-[#053345]" />
              <span className="text-2xl text-[#053345]">
                Website:
                <strong className="font-bold">benhvien@kiosk.com.vn</strong>
              </span>
            </div>
            <div className="flex items-center gap-4">
              <p className="text-2xl text-gray-500 mt-2">
                © {new Date().getFullYear()} Bệnh viện Nhân dân 115 — Phát
                triển bởi
                <span className="font-semibold text-[#1A7595]"> Cybertech</span>
              </p>
            </div>
          </footer>

          <Toaster
            position="top-right"
            richColors
            duration={5000}
            closeButton
          />
        </KioskProvider>
      </body>
    </html>
  );
}
