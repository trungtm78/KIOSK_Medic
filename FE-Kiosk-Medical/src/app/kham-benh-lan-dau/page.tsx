"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useKiosk } from "@/hooks/useKiosk";

export default function Page() {
  const router = useRouter();
  const { conversationId, registerStreamCallback } = useKiosk();

  useEffect(() => {
    if (!conversationId) {
      router.replace("/");
      return;
    }

    const handleStateUpdate = (parsed: { state: string }) => {
      console.log(
        "%c[Kham Benh Lan Dau] State Update:",
        "color: magenta; font-weight: bold;",
        parsed.state
      );

      const state = parsed.state || "";
      const matchState = (target: string) =>
        state === target || state.endsWith(`.${target}`);

      if (matchState("ORCHESTRATING")) {
        setTimeout(() => router.replace("/"), 200);
      }
    };

    const cleanup = registerStreamCallback("state.updated", handleStateUpdate);
    return cleanup;
  }, [conversationId, registerStreamCallback, router]);

  const handleBackHome = () => {
    router.push("/");
  };

  return (
    <div className="flex-col">
      <div className="w-full flex-col inline-flex bg-white rounded-[10px] px-30 py-20 mt-13 self-stretch justify-center items-center">
        <h1 className="text-4xl font-[Inter] font-extrabold text-[#1A7595] mb-8">THÔNG BÁO</h1>
        <h2 className="text-3xl font-[Inter] font-bold text-[#1A7595]">Vui lòng đến Quầy Đăng ký Thông tin</h2>
        <h3 className="text-3xl font-[Inter] font-bold text-[#1A7595]">(Quầy số 1, 2) để làm Sổ khám bệnh lần đầu</h3>
        <h4 className="text-3xl font-bold text-[#1A7595]">Xin cảm ơn!</h4>

        <div className="flex gap-6 mt-8">
          <Button
            className="flex items-center gap-2 w-80 h-20 text-3xl font-bold justify-center bg-[#1A7595]"
            onClick={handleBackHome}
          >
            Đã hiểu
          </Button>
        </div>
      </div>
    </div>
  );
}
