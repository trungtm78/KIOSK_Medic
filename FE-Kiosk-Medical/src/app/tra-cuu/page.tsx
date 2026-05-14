"use client";

import React, { Suspense, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import ChatBotAvatar from "@/components/ChatBoxAvatar";
import { useOrientation } from "@/hooks/useOrientation";
import { useKiosk } from "@/hooks/useKiosk";
import NavigationMap from "@/components/NavigationMap";

function TraCuuPageContent() {
  const router = useRouter();
  const { isLandscape } = useOrientation();

  const {
    conversationId,
    sendChatMessage,
    registerStreamCallback,
    playTtsStream,
    playAudioFile,
    isBotSpeaking,
  } = useKiosk();

  const [botMessage, setBotMessage] = useState<string>("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const initialMessageSent = useRef(false);
  const isLockedRef = useRef(false);
  const pendingEventsRef = useRef<{ type: string; data: any }[]>([]);
  const prevIsBotSpeaking = useRef(isBotSpeaking);

  const [navigationMap, setNavigationMap] = useState<{
    nodes: any;
    edges: any;
    path: string[];
    imageUrl: string;
  } | null>(null);
  const [workflowFlowchart, setWorkflowFlowchart] = useState<{
    title?: string;
    description?: string;
    imageUrl?: string | null;
  } | null>(null);

  // -----------------------------------------------
  // SAFE SEND MESSAGE (KHÔNG GỬI KHI BOT ĐANG NÓI)
  // -----------------------------------------------
  const safeSendChatMessage = (text: string) => {
    if (isBotSpeaking) {
      console.log("⛔ Bot đang phát âm thanh → KHÔNG gửi message:", text);
      return;
    }

    console.log("➡️ Gửi message lên chat service:", text);
    sendChatMessage(text);
  };

  // -----------------------------------------------
  // APPEND / REPLACE UTILS
  // -----------------------------------------------
  const safeAppend = (text: string) => {
    if (!text) return;

    setBotMessage((prev) => {
      if (!prev) return text;
      if (prev.trim() === text.trim()) return prev;
      if (prev.includes(text.trim())) return prev;
      return prev + "\n\n" + text;
    });
  };

  const safeReplace = (text: string) => {
    if (!text) return;
    setBotMessage(text);
  };

  // -----------------------------------------------
  // PROCESS EVENTS
  // -----------------------------------------------
  const processEvent = (type: string, data: any) => {

    // ⚡ Navigation
    const topic = data.info?.topic || data.info?.payload?.topic;
    const routePayload = data.info?.route || data.info?.payload?.route;

    if (type === "bot.info" && topic === "kiosk_navigation") {
      const direction = routePayload?.direction_text?.trim() || "";
      const map = routePayload?.map;

      safeReplace(direction);

      if (map) {
        setNavigationMap({
          nodes: map.nodes || {},
          edges: map.edges || [],
          path: routePayload?.path || [],
          imageUrl: map.image_url || null,
        });
      }
      setWorkflowFlowchart(null);

      isLockedRef.current = true;
      pendingEventsRef.current = [];

      playTtsStream(direction);
      return;
    }

    // ⚡ Hospital workflow (flowchart + summary)
    if (type === "bot.info" && topic === "hospital_workflow") {
      const text =
        String(data.info?.all_results || data.info?.flowchart?.description || "")
          .trim();
      const flowchart = data.info?.flowchart || {};
      const imageUrl = flowchart.image_url || data.info?.image_url || null;

      if (text) {
        safeReplace(text);
      }
      setNavigationMap(null);
      if (flowchart.title || flowchart.description || imageUrl) {
        setWorkflowFlowchart({
          title: flowchart.title,
          description: flowchart.description,
          imageUrl,
        });
      } else {
        setWorkflowFlowchart(null);
      }

      isLockedRef.current = true;
      pendingEventsRef.current = [];

      if (text) {
        playTtsStream(text);
      }
      return;
    }

    // ⚡ ALL_RESULTS → REPLACE UI
    if (type === "bot.info" && data.info?.all_results) {
      setNavigationMap(null);
      setWorkflowFlowchart(null);
      const text = String(data.info.all_results).trim();

      isLockedRef.current = true;
      pendingEventsRef.current = [];

      safeReplace(text);
      playTtsStream(text);
      return;
    }

    // ⚡ bot.info thường → append
    if (type === "bot.info") {
      setNavigationMap(null);
      setWorkflowFlowchart(null);
      const infoText =
        data.info?.message ||
        data.info?.text ||
        data.info?.display_text ||
        null;

      if (infoText) {
        const clean = String(infoText).trim();
        safeAppend(clean);
        playTtsStream(clean);
      }
      return;
    }

    // ⚡ bot.ask → append
    if (type === "bot.ask") {
        if (data.prompt) {
            const askMsg = data.prompt.trim();
            safeAppend(askMsg);
            playTtsStream(askMsg);
        }
        console.log("🔊 play audio file from bot.ask event:", data.audio_file);
        if (data.audio_file) {playAudioFile(data.audio_file);}
        console.log("📝 message_no_stt from bot.ask event:", data.message_no_stt);
        if (data.message_no_stt) {safeAppend(data.message_no_stt.trim());}
        return;
    }

    // ⚡ State DONE
    if (type === "state.updated" && data.state === "FLOW_INFO_LOOKUP.DONE") {
      setNavigationMap(null);
      setWorkflowFlowchart(null);
      const farewell = "Cảm ơn bạn. Hẹn bạn lần sau";
      safeAppend(farewell);
      playTtsStream(farewell);
      setTimeout(() => router.push("/"), 2500);
      return;
    }
  };

  // -----------------------------------------------
  // LISTEN FOR EVENTS
  // -----------------------------------------------
  useEffect(() => {
    if (!conversationId) return;

    const handle = (type: string, data: any) => {
      if (isLockedRef.current) {
        pendingEventsRef.current.push({ type, data });
      } else {
        processEvent(type, data);
      }
    };

    const c1 = registerStreamCallback("bot.info", (d) => handle("bot.info", d));
    const c2 = registerStreamCallback("bot.ask", (d) => handle("bot.ask", d));
    const c3 = registerStreamCallback("state.updated", (d) =>
      handle("state.updated", d)
    );

    return () => {
      c1();
      c2();
      c3();
    };
  }, [conversationId, registerStreamCallback]);

  // -----------------------------------------------
  // WHEN BOT FINISHES SPEAKING → PROCESS PENDING
  // -----------------------------------------------
  useEffect(() => {
    if (prevIsBotSpeaking.current && !isBotSpeaking) {
      if (isLockedRef.current) {
        isLockedRef.current = false;

        for (const ev of pendingEventsRef.current) {
          const { type, data } = ev;

          if (
            type === "bot.info" &&
            data.info?.all_results &&
            data.info?.topic !== "hospital_workflow"
          ) {
            const nextText = String(data.info.all_results).trim();
            safeReplace(nextText);
            playTtsStream(nextText);
          } else {
            processEvent(type, data);
          }
        }

        pendingEventsRef.current = [];
      }
    }

    prevIsBotSpeaking.current = isBotSpeaking;
  }, [isBotSpeaking]);

  // -----------------------------------------------
  // INITIAL GREETING
  // -----------------------------------------------
  useEffect(() => {
    if (!conversationId) {
      router.replace("/");
      return;
    }

    if (!initialMessageSent.current) {
      const msg = "Xin chào! Tôi có thể giúp bạn tra cứu thông tin gì?";
      safeReplace(msg);
      safeSendChatMessage("tôi muốn tra cứu thông tin");
      initialMessageSent.current = true;
    }
  }, [conversationId, router]);

  // -----------------------------------------------
  // SCROLL TO BOTTOM
  // -----------------------------------------------
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [botMessage]);

  return (
    <div
      className={`w-full flex flex-col ${isLandscape
        ? "items-center justify-center"
        : "items-center justify-start"
        } px-6`}
      style={{ height: "calc(100vh - 300px)" }}
    >
      <div
        className={`w-full max-w-[1600px] flex ${isLandscape ? "flex-row gap-16" : "flex-col gap-10"
          } items-center`}
      >
        <div
          className={`flex flex-col items-center ${isLandscape ? "flex-[3]" : "flex-1"
            } justify-center`}
        >
          <ChatBotAvatar />
        </div>

        <div
          className={`flex flex-col items-center ${isLandscape ? "flex-[7]" : "flex-1"
            } w-full`}
        >
          <h1 className="text-4xl md:text-5xl font-bold text-[#053345] text-center mb-6">
            TƯ VẤN - TRA CỨU
          </h1>

          <div
            ref={scrollRef}
            className="bg-white shadow-lg rounded-3xl p-8 border border-gray-200 w-full overflow-y-auto transition-all duration-700 ease-out text-3xl leading-relaxed"
            style={{
              height: isLandscape
                ? "calc(100vh - 500px)"
                : "calc(100vh - 600px)",
            }}
          >
            <pre className="whitespace-pre-wrap">{botMessage}</pre>
            {navigationMap && (
              <NavigationMap
                nodes={navigationMap.nodes}
                edges={navigationMap.edges}
                path={navigationMap.path}
                imageUrl={navigationMap.imageUrl}
              />
            )}
            {workflowFlowchart?.imageUrl && (
              <div className="mt-6 rounded-3xl overflow-hidden border border-gray-200 shadow">
                <img
                  src={workflowFlowchart.imageUrl}
                  alt={workflowFlowchart.title || "Sơ đồ quy trình bệnh viện"}
                  className="w-full object-cover"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <Suspense fallback={<div className="text-center p-10">Đang tải...</div>}>
      <TraCuuPageContent />
    </Suspense>
  );
}
