"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { CircleArrowRight } from "lucide-react";
import { useKiosk } from "@/hooks/useKiosk";
import ChatBotAvatar from "@/components/ChatBoxAvatar";
import { useOrientation } from "@/hooks/useOrientation";

interface ServiceOption {
  id: number;
  name: string;
  is_bhyt_applicable: boolean;
}

export default function ServiceTypePage() {
  const router = useRouter();
  const {
    conversationId,
    registerStreamCallback,
    sendChatMessage,
    playTtsStream, // ✅ thêm dòng này để dùng TTS
  } = useKiosk();
  const { isLandscape } = useOrientation();

  const [prompt, setPrompt] = useState<string>("");
  const [options, setOptions] = useState<ServiceOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [botMessages, setBotMessages] = useState<string[]>([]);

  const latestTicket = useRef<any>(null);
  const userJustSelected = useRef(false);
  const hasSpokenRef = useRef(false); // ✅ tránh nói lặp lại

  // --- Restore session ---
  useEffect(() => {
    const storedPrompt = sessionStorage.getItem("servicePrompt");
    const storedOptions = sessionStorage.getItem("serviceOptions");

    if (storedPrompt && storedOptions) {
      try {
        const parsedOptions = JSON.parse(storedOptions);
        if (Array.isArray(parsedOptions) && parsedOptions.length > 0) {
          setPrompt(storedPrompt);
          setOptions(parsedOptions);
          setLoading(false);
          console.log("%c[restore from session]", "color: green;", {
            storedPrompt,
            parsedOptions,
          });
        }
      } catch (e) {
        console.error("❌ Lỗi đọc sessionStorage:", e);
      }
    }
  }, []);

  // --- bot.ask ---
  useEffect(() => {
    if (!conversationId) return;

    const handleAsk = (data: {
      prompt: string;
      slot: string;
      options?: ServiceOption[];
    }) => {
      console.log("%c[bot.ask]", "color: blue;", data);
      if (data?.options?.length) {
        setPrompt(data.prompt);
        setOptions(data.options);
        setLoading(false);
        sessionStorage.setItem("servicePrompt", data.prompt);
        sessionStorage.setItem("serviceOptions", JSON.stringify(data.options));
      }
    };

    const cleanup = registerStreamCallback("bot.ask", handleAsk);
    return () => cleanup();
  }, [conversationId, registerStreamCallback]);

  // --- bot.ticket ---
  useEffect(() => {
    if (!conversationId) return;

    const handleTicket = (data: { ticket: any }) => {
      console.log("%c[bot.ticket]", "color: teal;", data);
      if (data?.ticket?.ticket) {
        latestTicket.current = data.ticket.ticket;
        sessionStorage.setItem(
          "latestTicket",
          JSON.stringify(data.ticket.ticket)
        );
      }
    };

    const cleanup = registerStreamCallback("bot.ticket", handleTicket);
    return () => cleanup();
  }, [conversationId, registerStreamCallback]);

  // --- state.updated ---
  useEffect(() => {
    if (!conversationId) return;

    const handleStateUpdate = (parsed: { state: string }) => {
      console.log("%c[state.updated]", "color: magenta;", parsed);

      if (parsed.state === "FLOW_ISSUE_TICKET.GATHER.ASK_SERVICE_PACKAGE") {
        setLoading(false);
      }

      if (parsed.state === "FLOW_ISSUE_TICKET.CONFIRM") {
        const ticketData =
          latestTicket.current ||
          JSON.parse(sessionStorage.getItem("latestTicket") || "null");

        if (ticketData) {
          const encoded = encodeURIComponent(JSON.stringify(ticketData));
          setTimeout(() => {
            router.push(`/tu-van/xac-nhan-in-phieu?ticket=${encoded}`);
          }, 300);
        }
      }
    };

    const cleanup = registerStreamCallback("state.updated", handleStateUpdate);
    return () => cleanup();
  }, [conversationId, registerStreamCallback, router]);

  // --- bot.message ---
  useEffect(() => {
    if (!conversationId) return;

    const handleBotMessage = (data: any) => {
      const content =
        data?.content || data?.text || (typeof data === "string" ? data : null);
      if (!content) return;

      setBotMessages((prev) => [...prev, content]);
    };

    const cleanup = registerStreamCallback("bot.message", handleBotMessage);
    return () => cleanup();
  }, [conversationId, registerStreamCallback]);

  // --- Restore bot messages ---
  useEffect(() => {
    const storedBotMessages = sessionStorage.getItem("botMessages");
    if (storedBotMessages) {
      try {
        const parsedMessages = JSON.parse(storedBotMessages);
        if (Array.isArray(parsedMessages)) {
          setBotMessages(parsedMessages);
        }
      } catch (e) {
        console.error("❌ Lỗi đọc botMessages:", e);
      }
    }
  }, []);

  // ✅ Thêm TTS logic giống SuggestionPage
  useEffect(() => {
    if (!playTtsStream || hasSpokenRef.current) return;
    if (botMessages.length === 0) return;

    const latestMsg = botMessages[botMessages.length - 1];
    const textToSpeak = `${latestMsg}, bạn muốn chọn loại dịch vụ nào?`;

    playTtsStream(textToSpeak);
    hasSpokenRef.current = true;
  }, [botMessages, playTtsStream]);

  const handleSelect = (option: ServiceOption) => {
    userJustSelected.current = true;
    sendChatMessage(`tôi chọn ${option.name}`);
  };

  const getColorByName = (name: string) => {
    const upper = name.toUpperCase();
    if (upper.includes("CÓ BHYT")) return "#1A7595";
    if (upper.includes("KHÔNG BHYT") || upper.includes("THƯỜNG"))
      return "#1C5F78";
    if (upper.includes("DỊCH VỤ")) return "#1A9578";
    if (upper.includes("V.I.P") || upper.includes("VIP")) return "#1D7861";
    return "#1A7595";
  };

  if (loading) {
    return (
      <div className="w-full flex items-center justify-center py-20">
        <p className="text-2xl text-gray-600 animate-pulse">
          Đang tải gợi ý dịch vụ...
        </p>
      </div>
    );
  }

  return (
    <div
      className={`w-full flex flex-col ${
        isLandscape
          ? "items-center justify-center"
          : "items-center justify-start"
      } px-6`}
      style={{ height: "calc(100vh - 300px)" }}
    >
      <div
        className={`w-full max-w-[1600px] flex ${
          isLandscape ? "flex-row gap-16" : "flex-col gap-10"
        } items-center justify-center`}
      >
        {/* Avatar + Bot Message */}
        <div
          className={`flex flex-col items-center text-center ${
            isLandscape ? "flex-[3] mt-30" : "flex-1"
          } ${isLandscape ? "justify-center" : "justify-start"}`}
          style={{ position: isLandscape ? "relative" : "static" }}
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
            {botMessages.map((msg, index) => (
              <p
                key={index}
                className="text-gray-500 text-2xl md:text-3xl font-semibold leading-relaxed line-clamp-3"
              >
                {msg}, bạn muốn chọn loại dịch vụ nào?
              </p>
            ))}
          </div>
        </div>

        {/* Dịch vụ */}
        <div
          className={`flex flex-col items-center ${
            isLandscape ? "flex-[7]" : "flex-1"
          } space-y-8 ${isLandscape ? "justify-center" : "justify-start"} w-full`}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-[#053345] text-center">
            LỰA CHỌN GÓI DỊCH VỤ
          </h1>
          <div className="w-full flex flex-col gap-6 md:gap-8 flex-1 overflow-y-auto">
            {options.map((option) => (
              <button
                key={option.id}
                onClick={() => handleSelect(option)}
                style={{ backgroundColor: getColorByName(option.name) }}
                className="w-full text-white font-bold flex justify-between items-center rounded-[10px] py-8 px-8 text-2xl md:text-3xl hover:opacity-90 transition shadow-md"
                disabled={!conversationId}
              >
                <span className="flex-1 text-left">{option.name}</span>
                <CircleArrowRight className="w-10 h-10 md:w-14 md:h-14 flex-shrink-0" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
