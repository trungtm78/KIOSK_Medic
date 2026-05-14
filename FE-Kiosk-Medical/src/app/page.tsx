"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, PlusCircle, MessageCircle } from "lucide-react";
import WelcomeModal from "@/components/WelcomeModal";
import { useKiosk } from "@/hooks/useKiosk";
import { useOrientation } from "@/hooks/useOrientation";
import ChatBotAvatar from "@/components/ChatBoxAvatar";

export default function WelcomePage() {
  const router = useRouter();
  const { isLandscape } = useOrientation();
  const [showWelcomeModal, setShowWelcomeModal] = useState(true);

  const {
    voiceStatus,
    conversationId,
    displayText,
    startSession,
    sendChatMessage,
    registerStreamCallback,
  } = useKiosk();

  const handleStart = () => {
    setShowWelcomeModal(false);
    startSession();
  };

  useEffect(() => {
    if (!conversationId) return;
    const handleStateUpdate = (parsed: { state: string }) => {
      console.log(
        "%c[Trang Chủ] State Update:",
        "color: magenta; font-weight: bold;",
        parsed
      );

      switch (parsed.state) {
        case "FLOW_ISSUE_TICKET.ASK_HEALTH_BOOK":
          setTimeout(() => router.push("/so-kham-benh"), 200);
          break;
        case "FLOW_TRIAGE.ASK_SYMPTOM":
          setTimeout(() => router.push("/tu-van"), 200);
          break;

        case "FLOW_INFO_LOOKUP.ASK_TOPIC":
          setTimeout(() => router.push("/tra-cuu"), 200);
          break;
        default:
          break;
      }
    };
    const cleanup = registerStreamCallback("state.updated", handleStateUpdate);
    return cleanup;
  }, [conversationId, registerStreamCallback, router]);

  return (
    <>
      {showWelcomeModal && <WelcomeModal onStart={handleStart} />}

      {/* Layout chính */}
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
          } ${isLandscape ? "items-center justify-center" : "items-center justify-start"}`}
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
              className={`bg-white p-6 rounded-3xl rounded-tl-none max-w-2xl z-20 h-[200px]  ${
                isLandscape ? "mt-[200px]" : "mt-0"
              }`}
            >
              {displayText ? (
                <p className="text-gray-500 text-2xl md:text-3xl font-semibold leading-relaxed">
                  Tôi là AI, trợ lý giọng nói tại kiosk Bệnh viện 115, tôi sẽ hỗ
                  trợ bạn!
                </p>
              ) : (
                <p className="text-gray-500 text-2xl md:text-3xl font-semibold leading-relaxed ">
                  Tôi là AI, trợ lý giọng nói tại kiosk Bệnh viện 115, tôi sẽ hỗ
                  trợ bạn!
                </p>
              )}
            </div>
          </div>

          {/* --- Bên phải / Dưới: Các nút --- */}
          <div
            className={`flex flex-col items-center ${
              isLandscape ? "flex-[7]" : "flex-1"
            } space-y-8 ${isLandscape ? "justify-center" : "justify-start"} w-full`}
          >
            <div className="text-center space-y-3">
              <h1 className="text-4xl md:text-5xl font-bold text-[#053345]">
                BỆNH VIỆN KIOSK
              </h1>
              <h2 className="text-4xl md:text-5xl font-bold text-[#053345]">
                XIN KÍNH CHÀO QUÝ KHÁCH
              </h2>
            </div>

            <div
              className={`flex flex-col gap-6 w-full ${
                isLandscape ? "max-w-5xl" : "max-w-2xl"
              }`}
            >
              <button
                onClick={() => sendChatMessage("tôi muốn bốc số khám bệnh")}
                className="w-full text-white font-bold flex justify-between items-center rounded-[10px] py-8 px-8 text-2xl md:text-4xl hover:opacity-90 transition"
                style={{ backgroundColor: "#1A7595" }}
                disabled={!conversationId}
              >
                <PlusCircle className="w-10 h-10 md:w-14 md:h-14 flex-shrink-0 mr-10" />
                <span className="text-left flex-1">Lấy số khám bệnh</span>
              </button>

              <button
                onClick={() => router.push("/tra-cuu")}
                className="w-full text-white font-bold flex justify-between items-center rounded-[10px] py-8 px-8 text-2xl md:text-4xl hover:opacity-90 transition"
                style={{ backgroundColor: "#1A7595" }}
              >
                <Search className="w-10 h-10 md:w-14 md:h-14 flex-shrink-0  mr-10" />
                <span className="text-left flex-1">Tra cứu thông tin</span>
              </button>

              <button
                onClick={() => sendChatMessage("tôi muốn tư vấn khám bệnh")}
                className="w-full text-white font-bold flex justify-between items-center rounded-[10px] py-8 px-8 text-2xl md:text-4xl hover:opacity-90 transition"
                style={{ backgroundColor: "#1A7595" }}
              >
                <MessageCircle className="w-10 h-10 md:w-14 md:h-14 flex-shrink-0  mr-10" />
                <span className="text-left flex-1">Tư vấn khám bệnh</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
