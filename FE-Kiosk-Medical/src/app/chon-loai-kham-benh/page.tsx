"use client";

import React, { useEffect, useState, Suspense, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { CircleArrowRight } from "lucide-react";
import { useKiosk } from "@/hooks/useKiosk";
import ChatBotAvatar from "@/components/ChatBoxAvatar";
import { useOrientation } from "@/hooks/useOrientation";

interface ServiceOption {
  id: number | string;
  name: string;
}

type DepartmentData = {
  prompt: string;
  options: ServiceOption[];
};

type BotAskPayload = {
  prompt?: string;
  options?: ServiceOption[];
};

function SelectServicePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isLandscape } = useOrientation();

  const {
    botPrompt,
    voiceStatus,
    conversationId,
    displayText,
    sendChatMessage,
    registerStreamCallback,
  } = useKiosk();

  const [serviceOptions, setServiceOptions] = useState<ServiceOption[]>([]);
  const departmentDataRef = useRef<DepartmentData | null>(null);

  const parseOptionsParam = (raw: string): ServiceOption[] => {
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        return parsed
          .filter(
            (option): option is ServiceOption =>
              typeof option === "object" &&
              option !== null &&
              "id" in option &&
              "name" in option
          )
          .map((option) => ({
            id:
              typeof option.id === "string" || typeof option.id === "number"
                ? option.id
                : String(option.id),
            name: String(option.name),
          }));
      }
    } catch (error) {
      console.error("❌ Lỗi khi phân tích 'options' từ URL:", error);
    }
    return [];
  };

  useEffect(() => {
    if (!conversationId) {
      router.replace("/");
      return;
    }

    const optionsParam = searchParams.get("options");
    if (optionsParam) {
      const parsedOptions = parseOptionsParam(optionsParam);
      setServiceOptions(parsedOptions);
    }

    const handleBotAsk = (parsed: BotAskPayload) => {
      if (parsed.prompt && parsed.options) {
        departmentDataRef.current = {
          prompt: parsed.prompt,
          options: parsed.options,
        };
      }
    };

    const handleStateUpdate = (parsed: { state: string }) => {
      console.log(
        `%c[Chọn Loại Khám] State Update: ${parsed.state}`,
        "color: magenta; font-weight: bold;"
      );
      if (parsed.state === "FLOW_ISSUE_TICKET.GATHER.ASK_DEPARTMENT") {
        setTimeout(() => {
          if (departmentDataRef.current) {
            const params = new URLSearchParams();
            params.append("prompt", departmentDataRef.current.prompt);
            params.append(
              "options",
              JSON.stringify(departmentDataRef.current.options)
            );
            router.push(`/chon-chuyen-khoa?${params.toString()}`);
          } else {
            router.push("/chon-chuyen-khoa");
          }
        }, 200);
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
  }, [conversationId, router, searchParams, registerStreamCallback]);

  const getColorByName = (name: string) => {
    const upper = name.toUpperCase();
    if (upper.includes("CÓ BHYT")) return "#1A7595";
    if (upper.includes("KHÔNG BHYT") || upper.includes("THƯỜNG"))
      return "#1C5F78";
    if (upper.includes("DỊCH VỤ")) return "#1A9578";
    if (upper.includes("V.I.P") || upper.includes("VIP")) return "#1D7861";
    return "#1A7595";
  };

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
        {/* --- Cột trái: Avatar + lời chào --- */}
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
            className={`bg-white p-6 rounded-3xl rounded-tl-none max-w-2xl z-20  h-[200px]  flex items-center justify-center ${
              isLandscape ? "mt-[200px]" : "mt-0"
            }`}
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

        {/* --- Cột phải: Câu hỏi + các nút --- */}
        <div
          className={`flex flex-col items-center ${
            isLandscape ? "flex-[7]" : "flex-1"
          } space-y-8 ${isLandscape ? "justify-center" : "justify-start"} w-full`}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-[#053345] text-center">
            LỰA CHỌN GÓI DỊCH VỤ
          </h1>

          <div className="w-full flex flex-col gap-6 md:gap-8 flex-1">
            {serviceOptions.map((pkg) => (
              <button
                key={pkg.id}
                onClick={() =>
                  sendChatMessage(`Tôi chọn ${pkg.name.replace(/\./g, "")}`)
                }
                style={{ backgroundColor: getColorByName(pkg.name) }}
                className="w-full text-white font-bold flex justify-between items-center rounded-[10px] py-8 px-8 text-2xl md:text-3xl hover:opacity-90 transition"
                disabled={!conversationId}
              >
                <span className="text-left flex-1">{pkg.name}</span>
                <CircleArrowRight className="w-10 h-10 md:w-14 md:h-14 flex-shrink-0" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <Suspense fallback={<div className="text-center p-10">Đang tải...</div>}>
      <SelectServicePageContent />
    </Suspense>
  );
}
