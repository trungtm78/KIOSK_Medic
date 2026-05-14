"use client";

import React, { useEffect, useRef, Suspense } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { X, Check } from "lucide-react";
import { useKiosk } from "@/hooks/useKiosk";
import { useOrientation } from "@/hooks/useOrientation";
import ChatBotAvatar from "@/components/ChatBoxAvatar";

interface ServiceOption {
  id: number | string;
  name: string;
}

type BotAskPayload = {
  options?: ServiceOption[];
};

function HealthBookPageContent() {
  const router = useRouter();
  const { isLandscape } = useOrientation();

  const {
    voiceStatus,
    conversationId,
    displayText,
    botPrompt,
    sendChatMessage,
    registerStreamCallback,
  } = useKiosk();

  const serviceOptionsRef = useRef<ServiceOption[] | null>(null);

  useEffect(() => {
    if (!conversationId) {
      router.replace("/");
      return;
    }

    const handleBotAsk = (parsed: BotAskPayload) => {
      if (parsed.options) {
        serviceOptionsRef.current = parsed.options;
      }
    };

    const handleStateUpdate = (parsed: { state: string }) => {
      console.log(
        `%c[Sổ Khám Bệnh] State Update: ${parsed.state}`,
        "color: magenta; font-weight: bold;"
      );

      const state = parsed.state || "";
      const matchState = (target: string) =>
        state === target || state.endsWith(`.${target}`);

      if (matchState("FLOW_ISSUE_TICKET.GATHER.ASK_SERVICE_PACKAGE")) {
        setTimeout(() => {
          const basePath = `/chon-loai-kham-benh`;
          const params = new URLSearchParams();
          if (serviceOptionsRef.current) {
            params.append("options", JSON.stringify(serviceOptionsRef.current));
          }
          router.push(`${basePath}?${params.toString()}`);
        }, 200);
        return;
      }

      if (matchState("WARN_NO_HEALTH_BOOK")) {
        setTimeout(() => router.push(`/kham-benh-lan-dau`), 200);
      }
    };

    const cleanupBotAsk = registerStreamCallback("bot.ask", handleBotAsk);
    const cleanupStateUpdate = registerStreamCallback(
      "state.updated",
      handleStateUpdate
    );

    return () => {
      cleanupBotAsk();
      cleanupStateUpdate();
    };
  }, [conversationId, registerStreamCallback, router]);

  return (
    <div
      className={`w-full flex flex-col ${
        isLandscape
          ? "items-center justify-center" // ngang: giữa cả hai trục
          : "items-center justify-start" // dọc: giữa ngang, dồn lên trên
      } px-6`}
      style={{
        height: "calc(100vh - 300px)",
      }}
    >
      <div
        className={`w-full max-w-[1600px] flex ${
          isLandscape ? "flex-row gap-16" : "flex-col gap-10"
        } items-center justify-center`}
      >
        {/* --- Bên trái / Trên: Avatar + lời chào --- */}
        <div
          className={`flex flex-col items-center text-center ${
            isLandscape ? "flex-[3] mt-30" : "flex-1"
          } ${isLandscape ? "justify-center" : "justify-start"}`}
          style={{
            position: isLandscape ? "relative" : "static",
          }}
        >
          <div
            className={`${isLandscape ? "absolute top-1/2 -translate-y-1/2" : ""}`}
            style={{
              left: isLandscape ? "50%" : "auto",
              transform: isLandscape ? "translate(-50%, -50%)" : "none",
            }}
          >
            <ChatBotAvatar />
          </div>

          <div
            className={`bg-white p-6 rounded-3xl rounded-tl-none max-w-2xl z-20 h-[200px]  flex items-center justify-center ${
              isLandscape ? "mt-[200px]" : "mt-0"
            } `}
          >
            {botPrompt ? (
              <p className="text-gray-500 text-2xl md:text-3xl font-semibold leading-relaxed">
                {botPrompt}
              </p>
            ) : (
              <p className="text-gray-500 mt-3 text-3xl leading-relaxed font-[Inter]  line-clamp-2">
                Tôi là AI, trợ lý giọng nói tại kiosk Bệnh viện 115, tôi sẽ hỗ
                trợ bạn!
              </p>
            )}
          </div>
        </div>

        {/* --- Bên phải / Dưới: Câu hỏi + nút chọn --- */}
        <div
          className={`flex flex-col items-center bg-white rounded-3xl pt-20 pb-20 ${
            isLandscape ? "flex-[7]" : "flex-1"
          } space-y-8 ${isLandscape ? "justify-center" : "justify-start"} w-full`}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-[#053345] text-center">
            QUÝ KHÁCH ĐÃ CÓ
          </h1>
          <h1 className="text-4xl md:text-5xl font-bold text-[#053345] text-center">
            SỔ KHÁM BỆNH CHƯA?
          </h1>

          <div className="flex flex-col md:flex-row gap-6 mt-4 w-full justify-center max-w-md">
            <Button
              className="flex items-center gap-4 w-full md:w-80 h-20 text-3xl font-bold justify-center bg-[#1A7595] hover:bg-[#145E76]"
              onClick={() => sendChatMessage("có sổ rồi")}
              disabled={!conversationId}
            >
              <Check size={32} strokeWidth={3} /> Đã có
            </Button>
            <Button
              variant="destructive"
              className="flex items-center gap-4 w-full md:w-80 h-20 text-3xl font-bold justify-center"
              onClick={() => sendChatMessage("không có sổ")}
              disabled={!conversationId}
            >
              <X size={32} strokeWidth={3} /> Chưa có
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <Suspense fallback={<div className="text-center p-10">Đang tải...</div>}>
      <HealthBookPageContent />
    </Suspense>
  );
}
