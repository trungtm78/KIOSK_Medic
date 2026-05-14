"use client";

import { useState, useRef, useEffect, FC } from "react";

// ====== Cấu hình ======
const STT_API_URL = "https://27.74.243.55:7443/stt-zipformer/transcribe";
const SAMPLE_RATE = 16000;
const CHUNK_SIZE = 512;

// ====== Thông số VAD & thời gian (quan trọng để tinh chỉnh) ======
const FIXED_THRESHOLD = 0.02; // <<< HÃY THỬ GIẢM GIÁ TRỊ NÀY NẾU KHÔNG PHÁT HIỆN GIỌNG NÓI (ví dụ: 0.01)
const SILENCE_HOLD_SEC = 1.5; // Giữ im lặng trong 1.5 giây để kết thúc câu nói
const MAX_IDLE_SEC = 5.0; // Bỏ qua phiên nếu không có ai nói gì sau 5 giây
const MIN_RECORD_SEC = 0.5; // Thời gian ghi âm tối thiểu

// ====== Kiểu dữ liệu ======
type LoopState = "STOPPED" | "RUNNING" | "INITIALIZING";
type VadState = "LISTENING" | "RECORDING" | "SENDING" | "DONE";

const SpeechToTextTestPage: FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loopState, setLoopState] = useState<LoopState>("STOPPED");

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  const loopStateRef = useRef(loopState);
  useEffect(() => {
    loopStateRef.current = loopState;
  }, [loopState]);

  const addLog = (msg: string) => {
    console.log(msg);
    setLogs((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);
  };

  const initAudio = async () => {
    if (audioContextRef.current) return;
    try {
      const AudioContext =
        window.AudioContext || (window as any).webkitAudioContext;
      const ctx = new AudioContext({ sampleRate: SAMPLE_RATE });
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: SAMPLE_RATE, channelCount: 1 },
      });
      const source = ctx.createMediaStreamSource(stream);
      audioContextRef.current = ctx;
      streamRef.current = stream;
      sourceRef.current = source;
      addLog("✅ Đã khởi tạo micro.");
    } catch (err) {
      addLog(`❌ Lỗi khởi tạo micro: ${(err as Error).message}`);
      throw err;
    }
  };

  const cleanup = () => {
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
    addLog("🛑 Đã dừng và giải phóng tài nguyên.");
  };

  const runOneSession = (threshold: number): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!audioContextRef.current || !sourceRef.current) {
        return reject("Audio chưa được khởi tạo");
      }
      if (processorRef.current) {
        processorRef.current.disconnect();
      }

      let vadState: VadState = "LISTENING";
      const audioBuf: number[] = [];
      let silentFrames = 0;
      let idleFrames = 0;
      let speechStart: number | null = null;

      addLog(`\n🎬 Bắt đầu phiên mới... Đang chờ giọng nói.`);
      processorRef.current = audioContextRef.current.createScriptProcessor(
        CHUNK_SIZE,
        1,
        1
      );

      processorRef.current.onaudioprocess = (event: AudioProcessingEvent) => {
        if (loopStateRef.current !== "RUNNING") {
          processorRef.current?.disconnect();
          return resolve();
        }

        const data = event.inputBuffer.getChannelData(0);
        const rms = calcRMS(data);
        const isSpeaking = rms >= threshold;

        switch (vadState) {
          case "LISTENING":
            idleFrames++;
            if ((idleFrames * CHUNK_SIZE) / SAMPLE_RATE > MAX_IDLE_SEC) {
              addLog("⏹️ Không phát hiện giọng nói, bỏ qua phiên.");
              vadState = "DONE";
              processorRef.current?.disconnect();
              return resolve();
            }
            if (isSpeaking) {
              vadState = "RECORDING";
              audioBuf.push(...Array.from(data));
              silentFrames = 0;
              speechStart = Date.now();
              addLog("🎙️ Phát hiện giọng nói, bắt đầu ghi...");
            }
            break;

          case "RECORDING":
            audioBuf.push(...Array.from(data));
            if (!isSpeaking) silentFrames++;
            else silentFrames = 0;

            const silenceHoldFrames = Math.round(
              (SILENCE_HOLD_SEC * SAMPLE_RATE) / CHUNK_SIZE
            );
            const recordDuration = speechStart
              ? (Date.now() - speechStart) / 1000
              : 0;

            if (
              silentFrames >= silenceHoldFrames &&
              recordDuration >= MIN_RECORD_SEC
            ) {
              vadState = "SENDING";
              addLog(
                `🤫 Kết thúc ghi (thời gian: ${recordDuration.toFixed(2)}s).`
              );
              processorRef.current?.disconnect();
              sendToAPI(new Float32Array(audioBuf)).then(resolve).catch(reject);
            }
            break;
        }
      };

      sourceRef.current.connect(processorRef.current);
      processorRef.current.connect(audioContextRef.current.destination);
    });
  };

  const sendToAPI = async (float32Array: Float32Array) => {
    const wavBlob = createWavBlob(float32Array);
    const formData = new FormData();
    formData.append("file", wavBlob, "speech.wav");

    addLog(`📤 Gửi ${Math.round(wavBlob.size / 1024)}KB tới API Zipformer...`);
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
      addLog(`✅ Kết quả STT: "${sttData.text}"`);
    } catch (err: any) {
      addLog(`❌ Lỗi gửi API: ${err.message}`);
    }
  };

  // ====== Các hàm tiện ích Audio ======
  const calcRMS = (buf: Float32Array): number => {
    let sum = 0;
    for (let i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
    return Math.sqrt(sum / buf.length);
  };

  const createWavBlob = (float32Array: Float32Array): Blob => {
    const buffer = floatTo16BitPCM(float32Array);
    const header = wavHeader(buffer.byteLength, SAMPLE_RATE, 1, 16);
    return new Blob([header, buffer], { type: "audio/wav" });
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

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    const mainLoop = async () => {
      if (loopStateRef.current !== "RUNNING") return;
      try {
        await runOneSession(FIXED_THRESHOLD);
      } catch (err) {
        addLog(`❌ Lỗi nghiêm trọng trong phiên: ${err}`);
        setLoopState("STOPPED");
        return;
      }
      if (loopStateRef.current === "RUNNING") {
        timeoutId = setTimeout(mainLoop, 500);
      }
    };

    if (loopState === "RUNNING") {
      mainLoop();
    } else if (loopState === "STOPPED") {
      cleanup();
    }
    return () => clearTimeout(timeoutId);
  }, [loopState]);

  const handleStart = async () => {
    setLogs([]);
    addLog("Đang khởi tạo...");
    setLoopState("INITIALIZING");
    try {
      await initAudio();
      addLog(`⚙️ Dùng ngưỡng cố định: ${FIXED_THRESHOLD}`);
      setLoopState("RUNNING");
    } catch (err) {
      setLoopState("STOPPED");
    }
  };

  const handleStop = () => setLoopState("STOPPED");

  return (
    <div style={{ padding: 20, fontFamily: "monospace", color: "#333" }}>
      <h1>🎙️ Trang test STT (API Zipformer)</h1>
      <p>
        Mở Console (F12) để xem chi tiết RMS. Ngưỡng phát hiện:{" "}
        <b>{FIXED_THRESHOLD}</b>
      </p>
      <div>
        <button
          onClick={handleStart}
          disabled={loopState !== "STOPPED"}
          style={{
            marginRight: 10,
            padding: "10px 18px",
            fontSize: "16px",
            cursor: "pointer",
          }}
        >
          Bắt đầu
        </button>
        <button
          onClick={handleStop}
          disabled={loopState === "STOPPED"}
          style={{ padding: "10px 18px", fontSize: "16px", cursor: "pointer" }}
        >
          Dừng
        </button>
      </div>
      <div
        style={{
          marginTop: 20,
          border: "1px solid #ccc",
          background: "#f8f8f8",
          padding: 10,
          height: "65vh",
          overflowY: "auto",
          whiteSpace: "pre-wrap",
          display: "flex",
          flexDirection: "column-reverse",
        }}
      >
        <div>
          {logs.map((log, i) => (
            <div
              key={i}
              style={{
                borderBottom: "1px solid #eee",
                padding: "4px 0",
              }}
            >
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SpeechToTextTestPage;
