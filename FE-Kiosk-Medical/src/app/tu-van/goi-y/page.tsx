"use client";

import React, { useEffect, useState, useRef, Suspense } from "react";
import { Building2, ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useKiosk } from "@/hooks/useKiosk";
import ChatBotAvatar from "@/components/ChatBoxAvatar";
import { useOrientation } from "@/hooks/useOrientation";

function SuggestionPageContent() {
  const router = useRouter();
  const {
    conversationId,
    voiceStatus,
    displayText,
    registerStreamCallback,
    sendChatMessage,
    playTtsStream,
    botPrompt,
  } = useKiosk();

  const { isLandscape } = useOrientation();
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const userJustSelected = useRef(false);
  const hasSpokenRef = useRef(false);

  useEffect(() => {
    const stored = sessionStorage.getItem("suggestedItems");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setSuggestions(parsed);
        }
      } catch (e) {
        console.error("❌ Lỗi đọc suggestedItems:", e);
      }
    }
  }, []);

  useEffect(() => {
    if (!conversationId) return;

    const handleSuggest = (data: { items: string[] }) => {
      if (data?.items?.length) {
        setSuggestions(data.items);
        sessionStorage.setItem("suggestedItems", JSON.stringify(data.items));
      }
    };

    const handleBotAsk = (data: {
      prompt: string;
      options?: { id: number; name: string; is_bhyt_applicable: boolean }[];
    }) => {
      if (data?.prompt && Array.isArray(data.options)) {
        sessionStorage.setItem("servicePrompt", data.prompt);
        sessionStorage.setItem("serviceOptions", JSON.stringify(data.options));
      }
    };

    const handleStateUpdate = (parsed: { state: string }) => {
      if (parsed.state === "FLOW_ISSUE_TICKET.GATHER.ASK_SERVICE_PACKAGE") {
        setTimeout(() => router.push("/tu-van/loai-kham-benh"), 200);
      }
    };

    const cleanupSuggest = registerStreamCallback("bot.suggest", handleSuggest);
    const cleanupAsk = registerStreamCallback("bot.ask", handleBotAsk);
    const cleanupState = registerStreamCallback(
      "state.updated",
      handleStateUpdate
    );

    return () => {
      cleanupSuggest();
      cleanupAsk();
      cleanupState();
    };
  }, [conversationId, registerStreamCallback, router]);

  useEffect(() => {
    if (suggestions.length > 0 && !hasSpokenRef.current && playTtsStream) {
      let departmentList = "";
      if (suggestions.length === 1) {
        departmentList = suggestions[0];
      } else if (suggestions.length > 1) {
        const last = suggestions[suggestions.length - 1];
        const allButLast = suggestions.slice(0, -1);
        departmentList = `${allButLast.join(", ")} hoặc ${last}`;
      }

      const textToSpeak = `Dựa trên các triệu chứng của bạn, tôi đề xuất bạn nên đến ${departmentList}. Xin mời bạn lựa chọn một chuyên khoa.`;

      playTtsStream(textToSpeak);
      hasSpokenRef.current = true;
    }
  }, [suggestions, playTtsStream]);

  const handleSelect = (depName: string) => {
    userJustSelected.current = true;
    sendChatMessage(`tôi khám ${depName} đi`);
  };

  return (
    <div
      className={`w-full flex ${
        isLandscape
          ? "items-center justify-center"
          : "items-start justify-start overflow-hidden"
      } px-6`}
      style={{
        height: "calc(100vh - 300px)",
      }}
    >
      <div
        className={`w-full max-w-[1600px] flex ${
          isLandscape ? "flex-row gap-16" : "flex-col gap-10"
        } h-full`}
      >
        {/* --- Bên trái / Trên: Avatar + lời chào --- */}
        <div
          className={`flex flex-col items-center text-center ${
            isLandscape ? "flex-[3] mt-30" : ""
          } ${isLandscape ? "justify-center" : "justify-start"}`}
          style={{
            position: isLandscape ? "relative" : "static",
          }}
        >
          <div
            className={`${
              isLandscape ? "absolute top-1/2 -translate-y-1/2" : ""
            }`}
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
            }`}
          >
            {botPrompt ? (
              <p className="text-gray-700 text-2xl md:text-3xl font-semibold leading-relaxed">
                {botPrompt}
              </p>
            ) : (
              <>
                <h2 className="font-bold text-2xl md:text-3xl text-[#053345]">
                  Xin chào! Mình là tư vấn viên của Bệnh viện 115
                </h2>
                <p className="text-gray-500 mt-3 text-xl leading-relaxed  line-clamp-2">
                  Tôi là trợ lý giọng nói tại kiosk. Bạn chỉ cần nói triệu
                  chứng, tôi sẽ giúp bạn chọn chuyên khoa phù hợp.
                </p>
              </>
            )}
          </div>
        </div>

        {/* --- Bên phải / Dưới: Danh sách gợi ý --- */}
        <div
          className={`flex flex-col items-center flex-1 bg-transparent ${
            isLandscape ? "flex-[7] h-full mt-10" : "flex-1 max-h-[60vh]"
          } space-y-8 ${isLandscape ? "justify-center" : "justify-start"} w-full`}
        >
          <h1 className="text-2xl md:text-4xl font-bold text-[#053345] text-center mb-4">
            QUÝ KHÁCH MUỐN KHÁM CHUYÊN KHOA NÀO?
          </h1>

          {/* ✅ Nút full-width thật sự */}
          <div className="flex-1 min-h-0 overflow-y-auto pr-2 w-full">
            {suggestions.length === 0 ? (
              <p className="text-2xl text-gray-500 italic text-center mt-10">
                Đang chờ hệ thống gợi ý chuyên khoa...
              </p>
            ) : (
              suggestions.map((item, idx) => {
                const isLast = idx === suggestions.length - 1;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSelect(item)}
                    className={`w-full bg-[#1A7595] text-white rounded-2xl px-8 py-8 text-2xl flex justify-between items-center hover:bg-[#145E76] transition-all text-left ${
                      isLast ? "mb-20" : "mb-5"
                    } shadow-md`}
                  >
                    <div className="flex items-center gap-4">
                      <div className="bg-[#0B556E] p-3 rounded-full flex-shrink-0">
                        <Building2 size={32} color="#fff" />
                      </div>
                      <span className="font-semibold text-3xl text-left">
                        {item}
                      </span>
                    </div>
                    <ChevronRight size={36} className="flex-shrink-0 ml-4" />
                  </button>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SuggestionPage() {
  return (
    <Suspense fallback={<div className="text-center p-10">Đang tải...</div>}>
      <SuggestionPageContent />
    </Suspense>
  );
}
