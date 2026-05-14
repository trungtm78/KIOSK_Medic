"use client";

import React, { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useKiosk } from "@/hooks/useKiosk";
import ChatBotAvatar from "@/components/ChatBoxAvatar";
import { useOrientation } from "@/hooks/useOrientation";

export default function SymptomQuestionPage() {
  const router = useRouter();
  const { botPrompt, conversationId, registerStreamCallback, isBotSpeaking } =
    useKiosk();
  const { isLandscape } = useOrientation();
  const serviceOptionsRef = useRef<any[] | null>(null);
  const botMessagesRef = useRef<string[]>([]);

  useEffect(() => {
    if (!conversationId) return;

    const handleBotAsk = (data: { options?: any[] }) => {
      if (data?.options) {
        serviceOptionsRef.current = data.options;
      }
    };

    const cleanup = registerStreamCallback("bot.ask", handleBotAsk);
    return cleanup;
  }, [conversationId, registerStreamCallback]);

  useEffect(() => {
    if (!conversationId) return;

    const handleStateUpdate = (parsed: { state: string }) => {
      if (parsed.state === "FLOW_ISSUE_TICKET.GATHER.ASK_SERVICE_PACKAGE") {
        if (botPrompt) sessionStorage.setItem("servicePrompt", botPrompt);
        if (serviceOptionsRef.current)
          sessionStorage.setItem(
            "serviceOptions",
            JSON.stringify(serviceOptionsRef.current)
          );

        // botMessages đã được lưu ở bước trước

        setTimeout(() => {
          router.push(`/tu-van/loai-kham-benh`);
        }, 200);
      }
    };

    const cleanup = registerStreamCallback("state.updated", handleStateUpdate);
    return cleanup;
  }, [conversationId, registerStreamCallback, router, botPrompt]);

  useEffect(() => {
    if (!conversationId) return;

    const handleBotMessage = (data: any) => {
      const content =
        data?.content || data?.text || (typeof data === "string" ? data : null);
      if (!content) return;

      // push vào ref
      botMessagesRef.current.push(content);

      // lưu sessionStorage ngay lập tức
      sessionStorage.setItem(
        "botMessages",
        JSON.stringify(botMessagesRef.current)
      );
    };

    const cleanup = registerStreamCallback("bot.message", handleBotMessage);
    return () => cleanup();
  }, [conversationId, registerStreamCallback]);

  return (
    <div
      className={`w-full flex flex-col ${
        isLandscape
          ? "items-center justify-center"
          : "items-center justify-start"
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
            className={`bg-white p-6 rounded-3xl rounded-tl-none max-w-2xl z-20 h-[200px] flex items-center justify-center ${
              isLandscape ? "mt-[200px]" : "mt-0"
            }`}
          >
            <p className="text-gray-500 text-2xl md:text-3xl font-semibold leading-relaxed line-clamp-2">
              {botPrompt ||
                "Tôi là trợ lý giọng nói tại kiosk Bệnh viện 115, tôi sẽ hỗ trợ bạn!"}
            </p>
          </div>
        </div>
        <div
          className={`flex flex-col items-center bg-white rounded-3xl pt-20 pb-20 ${
            isLandscape ? "flex-[7]" : "flex-1"
          } space-y-8 ${isLandscape ? "justify-center" : "justify-start"} w-full`}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-[#053345] text-center">
            QUÝ KHÁCH ĐANG GẶP
          </h1>
          <h1 className="text-4xl md:text-5xl font-bold text-[#053345] text-center">
            TRIỆU CHỨNG GÌ?
          </h1>
        </div>
      </div>
    </div>
  );
}
