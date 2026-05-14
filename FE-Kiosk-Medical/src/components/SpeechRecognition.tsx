"use client";
import { useState, useRef, useEffect, FC } from "react";

// --- Cấu hình ---
const WS_URI = "wss://medical-kiosk.cybertech.com.vn/";
const SAMPLE_RATE = 16000;
const FRAME_MS = 30;
const CHUNK_SIZE = Math.round((SAMPLE_RATE * FRAME_MS) / 1000);

// --- Tham số phát hiện giọng nói (VAD) ---
const CALIBRATE_SEC = 0.5;
const SILENCE_HOLD_SEC = 0.7;
const THRESH_MULTIPLIER = 2.0;
const MIN_THRESHOLD = 0.6;

// --- Định nghĩa Types ---
type VadState = "IDLE" | "CALIBRATING" | "LISTENING" | "RECORDING" | "SENDING";

interface ServerMessage {
  type?: "status";
  stage?: string;
  text?: string;
}

const SpeechRecognitionComponent: FC = () => {
  const [transcribedText, setTranscribedText] = useState<string>("");
  const [status, setStatus] = useState<string>("Chưa kết nối");

  const socketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const vadState = useRef<VadState>("IDLE");
  const audioBuffer = useRef<number[]>([]);
  const calibrationBuffer = useRef<number[]>([]);
  const rmsThreshold = useRef<number>(MIN_THRESHOLD);
  const silentFramesCount = useRef<number>(0);

  const cleanup = (): void => {
    processorRef.current?.disconnect();
    if (audioContextRef.current?.state !== "closed") {
      audioContextRef.current?.close();
    }
    streamRef.current?.getTracks().forEach((track) => track.stop());
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current?.close();
    }
    vadState.current = "IDLE";
    audioBuffer.current = [];
    calibrationBuffer.current = [];
    setStatus("Đã ngắt kết nối");
  };

  const startListening = async (): Promise<void> => {
    if (vadState.current !== "IDLE") return;

    setTranscribedText("");
    setStatus("Đang kết nối...");

    socketRef.current = new WebSocket(WS_URI);

    socketRef.current.onopen = async () => {
      setStatus("Đang xin quyền mic...");
      try {
        // Use a typed fallback for older WebKit browsers without using `any`
        const AudioContextCtor =
          window.AudioContext ??
          (window as unknown as { webkitAudioContext?: typeof AudioContext })
            .webkitAudioContext;

        if (!AudioContextCtor) {
          throw new Error("AudioContext is not supported in this browser");
        }

        audioContextRef.current = new AudioContextCtor({
          sampleRate: SAMPLE_RATE,
        });

        streamRef.current = await navigator.mediaDevices.getUserMedia({
          audio: { sampleRate: SAMPLE_RATE, channelCount: 1 },
        });

        const source = audioContextRef.current.createMediaStreamSource(
          streamRef.current
        );
        processorRef.current = audioContextRef.current.createScriptProcessor(
          CHUNK_SIZE,
          1,
          1
        );

        processorRef.current.onaudioprocess = handleAudioProcess;
        source.connect(processorRef.current);
        processorRef.current.connect(audioContextRef.current.destination);

        vadState.current = "CALIBRATING";
        setStatus("Đang hiệu chỉnh nhiễu nền...");
      } catch (error) {
        console.error("Lỗi khi truy cập microphone:", error);
        setStatus("Lỗi: Không truy cập được micro");
        cleanup();
      }
    };

    socketRef.current.onmessage = (event: MessageEvent) => {
      const data: ServerMessage = JSON.parse(event.data);
      console.log("Server response:", data);
      if (data.type === "status") {
        setStatus(`Server: ${data.stage}`);
      } else if (data.text) {
        setTranscribedText((prev) => prev + data.text + " ");
      }
    };

    socketRef.current.onclose = () => {
      console.log("WebSocket closed.");
      if (vadState.current !== "IDLE") cleanup();
    };

    socketRef.current.onerror = (error: Event) => {
      console.error("WebSocket error:", error);
      setStatus("Lỗi kết nối WebSocket");
      cleanup();
    };
  };

  const handleAudioProcess = (event: AudioProcessingEvent): void => {
    const float32Data = event.inputBuffer.getChannelData(0);
    const rms = calculateRMS(float32Data);

    switch (vadState.current) {
      case "CALIBRATING":
        calibrationBuffer.current.push(...float32Data);
        if (calibrationBuffer.current.length >= SAMPLE_RATE * CALIBRATE_SEC) {
          const noiseRms = calculateRMS(
            new Float32Array(calibrationBuffer.current)
          );
          rmsThreshold.current = Math.max(
            noiseRms * THRESH_MULTIPLIER,
            MIN_THRESHOLD
          );
          console.log(
            `Hiệu chỉnh xong. Ngưỡng RMS: ${rmsThreshold.current.toFixed(4)}`
          );
          vadState.current = "LISTENING";
          setStatus("Sẵn sàng, mời nói...");
        }
        break;

      case "LISTENING":
        if (rms >= rmsThreshold.current) {
          vadState.current = "RECORDING";
          setStatus("Đang ghi âm...");
          audioBuffer.current.push(...float32Data);
          silentFramesCount.current = 0;
        }
        break;

      case "RECORDING":
        audioBuffer.current.push(...float32Data);
        if (rms < rmsThreshold.current) {
          silentFramesCount.current++;
        } else {
          silentFramesCount.current = 0;
        }

        const silenceHoldFrames = Math.round(
          (SILENCE_HOLD_SEC * SAMPLE_RATE) / CHUNK_SIZE
        );
        if (silentFramesCount.current >= silenceHoldFrames) {
          sendAudioData();
        }
        break;
    }
  };

  const sendAudioData = (): void => {
    if (
      socketRef.current?.readyState !== WebSocket.OPEN ||
      audioBuffer.current.length === 0
    ) {
      cleanup();
      return;
    }

    processorRef.current?.disconnect();
    vadState.current = "SENDING";
    setStatus("Đang gửi dữ liệu...");

    const data = new Float32Array(audioBuffer.current);
    const int16Data = float32ToInt16(data);
    socketRef.current.send(int16Data.buffer);
    socketRef.current.send(JSON.stringify({ event: "end" }));

    console.log("Đã gửi audio và tín hiệu kết thúc.");
    setStatus("Đang chờ kết quả...");

    audioBuffer.current = [];
  };

  const float32ToInt16 = (buffer: Float32Array): Int16Array => {
    let l = buffer.length;
    const buf = new Int16Array(l);
    while (l--) {
      buf[l] = Math.min(1, buffer[l]) * 32767;
    }
    return buf;
  };

  const calculateRMS = (buffer: Float32Array): number => {
    let sum = 0;
    for (let i = 0; i < buffer.length; i++) {
      sum += buffer[i] * buffer[i];
    }
    return Math.sqrt(sum / buffer.length);
  };

  useEffect(() => {
    return () => cleanup();
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h2>WebSocket Speech-to-Text Demo</h2>
      <div>
        <button onClick={startListening} disabled={vadState.current !== "IDLE"}>
          Bắt đầu Ghi âm
        </button>
        <button onClick={cleanup} disabled={vadState.current === "IDLE"}>
          Dừng
        </button>
      </div>
      <p>
        <strong>Trạng thái:</strong> {status}
      </p>
      <div>
        <strong>Kết quả:</strong>
        <p
          style={{
            border: "1px solid #ccc",
            padding: "10px",
            minHeight: "50px",
          }}
        >
          {transcribedText}
        </p>
      </div>
    </div>
  );
};

export default SpeechRecognitionComponent;
