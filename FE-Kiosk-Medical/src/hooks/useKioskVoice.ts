"use client";

import { useState, useRef, useEffect, useCallback } from "react";

const STT_API_URL = "https://27.74.243.55:7443/stt-zipformer/transcribe";
const SAMPLE_RATE = 16000;
const CHUNK_SIZE = 512;

const ENERGY_THRESHOLD = 0.02;
const SILENCE_DURATION_SEC = 1.5;
const MAX_IDLE_SEC = 5.0;
const MIN_RECORD_SEC = 0.4;

type LoopState = "STOPPED" | "RUNNING" | "INITIALIZING";
type VadState = "LISTENING" | "RECORDING" | "SENDING";

type ExtendedWindow = Window & {
  AudioContext?: typeof AudioContext;
  webkitAudioContext?: typeof AudioContext;
};

export const useKioskVoice = (onResult: (text: string) => void) => {
  const [status, setStatus] = useState("Sẵn sàng");
  const [loopState, setLoopState] = useState<LoopState>("STOPPED");

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  const loopStateRef = useRef(loopState);
  useEffect(() => {
    loopStateRef.current = loopState;
  }, [loopState]);

  const log = useCallback((msg: string, state?: string) => {
    console.log(`[useKioskVoice] ${msg}`);
    if (state) setStatus(state);
  }, []);

  const initAudio = useCallback(async () => {
    if (audioContextRef.current) return;
    try {
      const extendedWindow = window as ExtendedWindow;
      const AudioContextClass =
        extendedWindow.AudioContext ?? extendedWindow.webkitAudioContext;
      if (!AudioContextClass) {
        throw new Error("AudioContext is not supported in this browser");
      }
      const ctx = new AudioContextClass({ sampleRate: SAMPLE_RATE });
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: SAMPLE_RATE, channelCount: 1 },
      });
      const source = ctx.createMediaStreamSource(stream);
      audioContextRef.current = ctx;
      streamRef.current = stream;
      sourceRef.current = source;
      log("✅ Đã khởi tạo micro.", "Sẵn sàng");
    } catch (err) {
      log(`❌ Lỗi khởi tạo micro: ${(err as Error).message}`, "Lỗi micro");
      throw err;
    }
  }, [log]);

  const cleanup = useCallback(() => {
    log("🧹 Dọn dẹp tài nguyên audio...");
    processorRef.current?.disconnect();
    processorRef.current = null;
    sourceRef.current?.disconnect();
    sourceRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close();
    }
    audioContextRef.current = null;
    log("✅ Dọn dẹp hoàn tất.", "Đã dừng");
  }, [log]);

  const calcRMS = (buf: Float32Array): number => {
    let sum = 0;
    for (let i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
    return Math.sqrt(sum / buf.length);
  };

  const floatTo16BitPCM = (input: Float32Array): ArrayBuffer => {
    const buffer = new ArrayBuffer(input.length * 2);
    const view = new DataView(buffer);
    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]));
      view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }
    return buffer;
  };

  const wavHeader = (
    dataLength: number,
    sampleRate: number,
    channels: number,
    bits: number
  ): ArrayBuffer => {
    const header = new ArrayBuffer(44);
    const view = new DataView(header);
    const writeString = (s: string, offset: number) => {
      for (let i = 0; i < s.length; i++) {
        view.setUint8(offset + i, s.charCodeAt(i));
      }
    };
    writeString("RIFF", 0);
    view.setUint32(4, 36 + dataLength, true);
    writeString("WAVE", 8);
    writeString("fmt ", 12);
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, channels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, (sampleRate * channels * bits) / 8, true);
    view.setUint16(32, (channels * bits) / 8, true);
    view.setUint16(34, bits, true);
    writeString("data", 36);
    view.setUint32(40, dataLength, true);
    return header;
  };

  const createWavBlob = (float32Array: Float32Array): Blob => {
    const buffer = floatTo16BitPCM(float32Array);
    const header = wavHeader(buffer.byteLength, SAMPLE_RATE, 1, 16);
    return new Blob([header, buffer], { type: "audio/wav" });
  };

  const sendToAPI = useCallback(
    async (float32Array: Float32Array) => {
      const wavBlob = createWavBlob(float32Array);
      log(
        `📤 Gửi ${Math.round(wavBlob.size / 1024)}KB tới API...`,
        "Đang xử lý"
      );
      const formData = new FormData();
      formData.append("file", wavBlob, "speech.wav");
      try {
        const sttRes = await fetch(STT_API_URL, {
          method: "POST",
          body: formData,
        });
        if (!sttRes.ok) {
          const errText = await sttRes.text();
          throw new Error(`HTTP ${sttRes.status}: ${errText}`);
        }
        const sttData = await sttRes.json();
        log(`✅ Kết quả: "${sttData.text}"`);
        if (sttData.text) {
          onResult(sttData.text);
        } else {
          onResult("Không có nội dung nhận diện");
        }
      } catch (err: any) {
        log(`❌ Lỗi API: ${err.message}`, "Lỗi xử lý");
        onResult("Không có nội dung nhận diện");
      }
    },
    [log, onResult]
  );

  const runOneSession = useCallback((): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!audioContextRef.current || !sourceRef.current) {
        return reject("Audio context chưa sẵn sàng.");
      }
      if (processorRef.current) {
        processorRef.current.disconnect();
      }

      let vadState: VadState = "LISTENING";
      const audioBuf: number[] = [];
      let silentFrames = 0;
      let idleFrames = 0;
      let speechStart: number | null = null;

      processorRef.current = audioContextRef.current.createScriptProcessor(
        CHUNK_SIZE,
        1,
        1
      );
      log("🎧 Bắt đầu lắng nghe...", "Đang lắng nghe...");

      processorRef.current.onaudioprocess = (event: AudioProcessingEvent) => {
        if (loopStateRef.current !== "RUNNING") {
          processorRef.current?.disconnect();
          return resolve();
        }

        const data = event.inputBuffer.getChannelData(0);
        const rms = calcRMS(data);
        const isSpeaking = rms >= ENERGY_THRESHOLD;

        switch (vadState) {
          case "LISTENING":
            idleFrames++;
            if ((idleFrames * CHUNK_SIZE) / SAMPLE_RATE > MAX_IDLE_SEC) {
              vadState = "SENDING"; // Prevent loop from hanging
              processorRef.current?.disconnect();
              return resolve();
            }
            if (isSpeaking) {
              vadState = "RECORDING";
              audioBuf.push(...Array.from(data));
              speechStart = Date.now();
              log("🎙️ Phát hiện giọng nói...", "Đang ghi âm...");
            }
            break;

          case "RECORDING":
            audioBuf.push(...Array.from(data));
            if (!isSpeaking) silentFrames++;
            else silentFrames = 0;

            const silenceHoldFrames = Math.round(
              (SILENCE_DURATION_SEC * SAMPLE_RATE) / CHUNK_SIZE
            );
            const recordDuration = speechStart
              ? (Date.now() - speechStart) / 1000
              : 0;

            if (
              silentFrames >= silenceHoldFrames &&
              recordDuration >= MIN_RECORD_SEC
            ) {
              vadState = "SENDING";
              processorRef.current?.disconnect();
              sendToAPI(new Float32Array(audioBuf)).then(resolve).catch(reject);
            }
            break;
        }
      };
      sourceRef.current.connect(processorRef.current);
      processorRef.current.connect(audioContextRef.current.destination);
    });
  }, [log, sendToAPI]);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    const mainLoop = async () => {
      if (loopStateRef.current !== "RUNNING") return;
      try {
        await runOneSession();
      } catch (err) {
        log(`❌ Lỗi trong phiên: ${err}`);
        setLoopState("STOPPED");
        return;
      }
      if (loopStateRef.current === "RUNNING") {
        timeoutId = setTimeout(mainLoop, 500);
      }
    };

    if (loopState === "RUNNING") {
      mainLoop();
    }
    return () => clearTimeout(timeoutId);
  }, [loopState, runOneSession, log]);

  const startListening = useCallback(async () => {
    if (loopStateRef.current !== "STOPPED") return;
    setLoopState("INITIALIZING");
    setStatus("Đang khởi tạo...");
    try {
      await initAudio();
      setLoopState("RUNNING");
    } catch (error) {
      setLoopState("STOPPED");
    }
  }, [initAudio]);

  const stopListening = useCallback(() => {
    if (loopStateRef.current !== "STOPPED") {
      log("🛑 Yêu cầu dừng...");
      setLoopState("STOPPED");
      cleanup();
    }
  }, [cleanup, log]);

  useEffect(() => {
    return () => {
      if (loopStateRef.current !== "STOPPED") {
        setLoopState("STOPPED");
        cleanup();
      }
    };
  }, [cleanup]);

  return { status, startListening, stopListening };
};
