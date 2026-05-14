"use client";

import React, {
  createContext,
  useState,
  useRef,
  useCallback,
  ReactNode,
  useEffect,
} from "react";
import { useKioskVoice } from "@/hooks/useKioskVoice";

interface Ticket {
  registration_id: number;
  queue_number: number;
  department_name: string;
  room_name: string;
  service_package_name: string;
  queue_date: string;
  registration_time: string;
  hospital_name: string;
}

const NEXT_PUBLIC_API_PATH = process.env.NEXT_PUBLIC_API_PATH || "";
const CHAT_API_BASE = `${NEXT_PUBLIC_API_PATH}/v1/chat`;
const TENANT_ID = "1";
const TTS_API_URL =
  process.env.TTS_API_URL || "https://medicagent.cybertech.com.vn/tts";

interface KioskContextType {
  voiceStatus: string;
  conversationId: string | null;
  displayText: string;
  botPrompt: string;
  ticket: Ticket | null;
  startSession: () => Promise<void>;
  stopSession: () => void;
  sendChatMessage: (text: string) => Promise<void>;
  registerStreamCallback: <T>(
    eventName: string,
    callback: (data: T) => void
  ) => () => void;
  playTtsStream: (text: string) => Promise<void>;
  playAudioFile: (fileName: string) => Promise<void>;
  isBotSpeaking: boolean;
}

export const KioskContext = createContext<KioskContextType | undefined>(
  undefined
);

const waitForUpdateEnd = (sourceBuffer: SourceBuffer): Promise<void> => {
  return new Promise((resolve) => {
    if (!sourceBuffer.updating) {
      resolve();
      return;
    }
    const onUpdateEnd = () => {
      sourceBuffer.removeEventListener("updateend", onUpdateEnd);
      resolve();
    };
    sourceBuffer.addEventListener("updateend", onUpdateEnd);
  });
};

const appendBuffer = async (
  sourceBuffer: SourceBuffer,
  chunk: BufferSource
): Promise<void> => {
  if (sourceBuffer.updating) {
    await waitForUpdateEnd(sourceBuffer);
  }
  sourceBuffer.appendBuffer(chunk);
  await waitForUpdateEnd(sourceBuffer);
};

export const KioskProvider = ({ children }: { children: ReactNode }) => {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [voiceStatus, setVoiceStatus] = useState("Sẵn sàng");
  const [displayText, setDisplayText] = useState("");
  const [botPrompt, setBotPrompt] = useState("");
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);
  const evtSourceRef = useRef<EventSource | null>(null);
  const streamCallbacksRef =
    useRef<Map<string, Array<(data: unknown) => void>>>(new Map());
  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaSourceRef = useRef<MediaSource | null>(null);
  const isTtsPlayingRef = useRef(false);

  const sendChatMessage = useCallback(
    async (text: string) => {
      // ⛔ BOT ĐANG NÓI → KHÔNG GỬI MESSAGE
      if (isBotSpeaking) {
        console.log(
          "⛔ Bot đang nói — KHÔNG gửi message lên chat-service:",
          text
        );
        return;
      }

      if (!conversationId) return;

      setDisplayText(text);

      try {
        await fetch(`${CHAT_API_BASE}/${conversationId}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Tenant-Id": TENANT_ID,
            "Idempotency-Key": crypto.randomUUID(),
          },
          body: JSON.stringify({
            role: "user",
            content: text,
            attachments: [{}],
            stream: true,
            options: {},
          }),
        });
      } catch (err) {
        console.error("❌ [Context] Lỗi Chat Service:", err);
      }
    },
    [conversationId, isBotSpeaking]
  );

  const playTtsStream = useCallback(async (text: string) => {
    if (!text || isTtsPlayingRef.current || !audioRef.current) return;
    isTtsPlayingRef.current = true;
    setIsBotSpeaking(true);
    const audioPlayer = audioRef.current;
    if (audioPlayer.src) {
      URL.revokeObjectURL(audioPlayer.src);
      audioPlayer.src = "";
    }
    mediaSourceRef.current = new MediaSource();
    audioPlayer.src = URL.createObjectURL(mediaSourceRef.current);
    const onSourceOpen = async () => {
      if (!mediaSourceRef.current) return;
      mediaSourceRef.current.removeEventListener("sourceopen", onSourceOpen);
      const sourceBuffer = mediaSourceRef.current.addSourceBuffer("audio/mpeg");
      try {
        const response = await fetch(TTS_API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        if (!response.ok || !response.body)
          throw new Error(`Lỗi từ server TTS: ${response.status}`);
        const reader = response.body.getReader();
        audioPlayer
          .play()
          .catch((e) => console.error("Lỗi khi tự động play audio:", e));
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          await appendBuffer(sourceBuffer, value);
          await new Promise((r) => setTimeout(r, 30));
        }
        await waitForUpdateEnd(sourceBuffer);
        if (mediaSourceRef.current.readyState === "open")
          mediaSourceRef.current.endOfStream();
      } catch (error) {
        console.error("❌ Lỗi trong quá trình streaming TTS:", error);
        if (mediaSourceRef.current?.readyState === "open")
          mediaSourceRef.current.endOfStream();
        isTtsPlayingRef.current = false;
      }
    };
    mediaSourceRef.current.addEventListener("sourceopen", onSourceOpen);
  }, []);

  const playAudioFile = useCallback(async (fileName: string) => {
    if (!fileName || isTtsPlayingRef.current || !audioRef.current) return;
    const sanitizedName = encodeURIComponent(fileName.trim());
    if (!sanitizedName) return;

    try {
      isTtsPlayingRef.current = true;
      setIsBotSpeaking(true);
      const audioPlayer = audioRef.current;
      const currentSrc = audioPlayer.src;
      if (currentSrc && currentSrc.startsWith("blob:")) {
        URL.revokeObjectURL(currentSrc);
      }
      audioPlayer.pause();
      audioPlayer.src = "";
      audioPlayer.load();
      audioPlayer.src = `/voice_tts/${sanitizedName}`;
      await audioPlayer.play();
    } catch (error) {
      console.error("❌ Lỗi phát audio file có sẵn:", error);
      isTtsPlayingRef.current = false;
      setIsBotSpeaking(false);
    }
  }, []);

  const handleSttResult = useCallback(
    (text: string) => {
      if (!conversationId) return;
      if (text.includes("Không có nội dung nhận diện")) {
        playTtsStream("Tôi không nghe rõ, bạn có thể nói lại được không?");
      } else {
        sendChatMessage(text);
      }
    },
    [conversationId, sendChatMessage, playTtsStream]
  );

  const { status, startListening, stopListening } =
    useKioskVoice(handleSttResult);

  useEffect(() => {
    setVoiceStatus(status);
  }, [status]);

  const registerStreamCallback = useCallback(
    <T,>(eventName: string, callback: (data: T) => void): (() => void) => {
      const wrappedCallback = (data: unknown) => {
        callback(data as T);
      };
      if (!streamCallbacksRef.current.has(eventName)) {
        streamCallbacksRef.current.set(eventName, []);
      }
      streamCallbacksRef.current.get(eventName)!.push(wrappedCallback);
      return () => {
        const callbacks = streamCallbacksRef.current.get(eventName);
        if (callbacks) {
          const index = callbacks.indexOf(wrappedCallback);
          if (index > -1) {
            callbacks.splice(index, 1);
          }
        }
      };
    },
    []
  );

  useEffect(() => {
    const audioPlayer = audioRef.current;
    const onEnded = () => {
      isTtsPlayingRef.current = false;
      setIsBotSpeaking(false);
    };
    audioPlayer?.addEventListener("ended", onEnded);
    return () => audioPlayer?.removeEventListener("ended", onEnded);
  }, []);

  const setupEventSource = useCallback((convId: string) => {
    if (evtSourceRef.current) evtSourceRef.current.close();
    const streamUrl = `${CHAT_API_BASE}/${convId}/stream`;
    console.log("🚀 Mở SSE tới:", streamUrl);
    const es = new EventSource(streamUrl);
    evtSourceRef.current = es;
    const addGenericListener = (eventName: string) => {
      es.addEventListener(eventName, (event: MessageEvent) => {
        console.log(`📡 Nhận event ${eventName}:`, event.data);
        try {
          const parsedData = JSON.parse(event.data) as unknown;
          const callbacks = streamCallbacksRef.current.get(eventName);
          if (callbacks && callbacks.length > 0) {
            callbacks.forEach((cb) => cb(parsedData));
          }
        } catch (e) {
          console.error(`[Context] Lỗi parse JSON cho event ${eventName}:`, e);
        }
      });
    };
    addGenericListener("bot.ask");
    addGenericListener("bot.message");
    addGenericListener("message.completed");
    addGenericListener("state.updated");
    addGenericListener("bot.ticket");
    addGenericListener("bot.suggest");
    addGenericListener("bot.info");
  }, []);

  const startSession = useCallback(async () => {
    const newConvId = crypto.randomUUID();
    setConversationId(newConvId);
    setDisplayText("");
    setBotPrompt("");
    setTicket(null);
    setupEventSource(newConvId);
    startListening();
    // P2.3 / Codex #16 fix: previously called sendChatMessage("xin chào")
    // which closed over stale conversationId (still null from useState init).
    // Now POST directly with newConvId.
    setTimeout(() => {
      void fetch(`${CHAT_API_BASE}/${newConvId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-Id": TENANT_ID,
          "Idempotency-Key": crypto.randomUUID(),
        },
        body: JSON.stringify({
          role: "user",
          content: "xin chào",
          attachments: [{}],
          stream: true,
          options: {},
        }),
      }).catch((err) => {
        console.error("[KioskProvider] startSession initial message failed:", err);
      });
    }, 500);
  }, [setupEventSource, startListening]);

  const stopSession = useCallback(() => {
    stopListening();
    evtSourceRef.current?.close();
    setConversationId(null);
    setTicket(null);
  }, [stopListening]);

  // --- ĐỌC GHÉP bot.message + bot.ask ---
  useEffect(() => {
    let lastBotMessage = ""; // nhớ lại message trước khi bot.ask đến

    // Khi bot gửi message
    const handleBotMessage = (data: { role?: string; content?: string }) => {
      if (data?.role === "assistant" && data?.content) {
        console.log("💬 [bot.message]", data.content);
        lastBotMessage = data.content; // lưu lại
      }
    };

    // Khi bot hỏi tiếp
    const handleBotAsk = (data: { prompt?: string; audio_file?: string }) => {
      if (data?.prompt) {
        setBotPrompt(data.prompt);

        let textToSpeak = data.prompt;
        if (lastBotMessage) {
          textToSpeak = `${lastBotMessage}. ${data.prompt}`;
          console.log("🗣️ [TTS speak]:", textToSpeak);
          lastBotMessage = ""; // reset tránh đọc lại
        }

        if (data.audio_file) {
          playAudioFile(data.audio_file);
        } else {
          playTtsStream(textToSpeak);
        }
      }
    };

    const cleanupMsg = registerStreamCallback("bot.message", handleBotMessage);
    const cleanupAsk = registerStreamCallback("bot.ask", handleBotAsk);

    return () => {
      cleanupMsg();
      cleanupAsk();
    };
  }, [registerStreamCallback, playTtsStream, playAudioFile, setBotPrompt]);

  const value = {
    voiceStatus,
    conversationId,
    displayText,
    botPrompt,
    ticket,
    startSession,
    stopSession,
    sendChatMessage,
    registerStreamCallback,
    playTtsStream,
    playAudioFile,
    isBotSpeaking,
  };

  return (
    <KioskContext.Provider value={value}>
      <audio ref={audioRef} style={{ display: "none" }} />
      {children}
    </KioskContext.Provider>
  );
};
