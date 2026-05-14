"use client";

import React, { useEffect, useState, Suspense, useCallback } from "react";
import { CircleAlert, Printer } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useKiosk } from "@/hooks/useKiosk";
import ChatBotAvatar from "@/components/ChatBoxAvatar";
import { useOrientation } from "@/hooks/useOrientation";

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

const AUTO_REDIRECT_TIMEOUT = 300000;

function ConfirmPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { stopSession, playTtsStream } = useKiosk();
  const { isLandscape } = useOrientation();

  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [aiResponseText, setAiResponseText] = useState("");

  // --- Lấy ticket ---
  useEffect(() => {
    const ticketParam = searchParams.get("ticket");
    console.log("🔍 Dữ liệu ticket từ URL:", ticketParam);
    if (ticketParam) {
      try {
        const parsedData: Ticket = JSON.parse(decodeURIComponent(ticketParam));
        if (parsedData && typeof parsedData.queue_number !== "undefined") {
          setTicket(parsedData);
        } else {
          throw new Error("Dữ liệu ticket không hợp lệ.");
        }
      } catch (err) {
        console.error("❌ Lỗi khi phân tích dữ liệu ticket:", err);
        setErrorMessage("Không thể đọc thông tin phiếu. Vui lòng thử lại.");
      }
    } else {
      setErrorMessage("Không tìm thấy thông tin phiếu.");
    }
  }, [searchParams]);

  // --- Phát giọng nói ---
  useEffect(() => {
    if (ticket) {
      const ttsText = `Đăng ký thành công. Bạn vui lòng đến phòng ${ticket.room_name}, ${ticket.department_name} để được hướng dẫn thêm. Bạn vui lòng xác nhận thông tin và in phiếu.`;
      const displayText = `Đăng ký thành công.\n Bạn vui lòng xác nhận thông tin và in phiếu.`;
      setAiResponseText(displayText);
      playTtsStream(ttsText);
    }
  }, [ticket, playTtsStream]);

  // --- Tự động quay lại ---
  useEffect(() => {
    const timer = setTimeout(() => {
      stopSession();
      router.push("/");
    }, AUTO_REDIRECT_TIMEOUT);
    return () => {
      clearTimeout(timer);
      stopSession();
    };
  }, [router, stopSession]);

  const handlePrintAndFinish = useCallback(() => {
    console.log("[print] click");
    window.print();
  }, []);

  useEffect(() => {
    const handleAfterPrint = () => {
      stopSession();
      router.push("/");
    };
    window.addEventListener("afterprint", handleAfterPrint);
    return () => {
      window.removeEventListener("afterprint", handleAfterPrint);
    };
  }, [router, stopSession]);

  if (!ticket && !errorMessage) {
    return (
      <div className="w-full flex items-center justify-center py-20">
        <p className="text-2xl text-gray-600 animate-pulse">
          Đang tải thông tin phiếu...
        </p>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-6">
        <CircleAlert className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-3xl font-bold text-red-600 mb-4">Đã xảy ra lỗi</h2>
        <p className="text-xl mb-8">{errorMessage}</p>
        <button
          onClick={() => router.push("/")}
          className="bg-[#1A7595] text-white px-8 py-4 rounded-lg text-xl font-semibold hover:bg-[#145c77] transition"
        >
          Quay lại trang chính
        </button>
      </div>
    );
  }

  return (
    <div
      className={`confirm-page w-full flex ${
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
        {/* --- Cột trái: AI nói --- */}
        {/* --- Cột trái: Avatar + lời chào (đồng bộ với trang chuẩn) --- */}
        <div
          className={`print-hide flex flex-col items-center text-center ${
            isLandscape ? "flex-[3] mt-30" : "mb-10"
          } ${isLandscape ? "justify-center" : "justify-start"}`}
          style={{
            position: isLandscape ? "relative" : "static",
          }}
        >
          {/* Avatar */}
          <div
            className={`${isLandscape ? "absolute top-1/2 -translate-y-1/2" : ""}`}
            style={{
              left: isLandscape ? "50%" : "auto",
              transform: isLandscape ? "translate(-50%, -50%)" : "none",
            }}
          >
            <ChatBotAvatar />
          </div>

          {/* Lời chào */}
          <div
            className={`bg-white p-6 rounded-3xl rounded-tl-none max-w-2xl z-20  max-h-[243px] ${
              isLandscape ? "mt-[200px]" : "mt-0"
            }`}
          >
            {aiResponseText ? (
              <p className="text-gray-500 text-2xl md:text-3xl font-semibold leading-relaxe d">
                {aiResponseText}
              </p>
            ) : (
              <p className="text-gray-500 mt-3 text-3xl leading-relaxed font-[Inter]  line-clamp-2">
                Tôi là AI, trợ lý giọng nói tại kiosk Bệnh viện 115, tôi sẽ hỗ
                trợ bạn!
              </p>
            )}
          </div>
        </div>

        {/* --- Cột phải: Phiếu in --- */}
        <div
          id="print-area"
          className={`flex flex-col items-center bg-white rounded-3xl p-10 ${
            isLandscape ? "flex-[7]" : "w-full"
          } w-full overflow-y-auto`}
          style={{
            height: isLandscape ? "90%" : "55%",
            justifyContent: "flex-start",
            alignSelf: "center",
          }}
        >
          {/* Tiêu đề */}
          <div className="text-center mb-6">
            <h1 className="text-3xl md:text-4xl font-bold text-[#053345] mb-2">
              XÁC NHẬN THÔNG TIN & IN PHIẾU
            </h1>
            <p className="text-xl md:text-2xl text-gray-700">
              Vui lòng kiểm tra lại thông tin trước khi in
            </p>
          </div>

          {/* Nội dung chính */}
          <div className="flex-1 overflow-y-auto pr-2">
            {isLandscape ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full items-start">
                {/* Cột 1 */}
                <div>
                  <p className="text-lg text-gray-600">Họ tên bệnh nhân</p>
                  <b className="text-2xl text-[#053345]">Nguyễn Văn A</b>
                </div>

                {/* Cột 2 */}
                <div>
                  <p className="text-lg text-gray-600">Loại dịch vụ</p>
                  <b className="text-2xl text-[#053345]">
                    {ticket?.service_package_name}
                  </b>
                </div>

                {/* Cột 3 (Số thứ tự) */}
                <div className="flex flex-col items-center justify-center">
                  <div className="w-[160px] h-[160px] border-4 border-[#053345] rounded-xl flex flex-col items-center justify-center bg-cyan-50">
                    <p className="text-lg text-[#053345] font-semibold">
                      SỐ THỨ TỰ
                    </p>
                    <b className="queue-number text-6xl text-[#053345] mt-1 font-mono">
                      {ticket?.queue_number.toString().padStart(3, "0")}
                    </b>
                  </div>
                </div>

                {/* Dòng 2 */}
                <div>
                  <p className="text-lg text-gray-600">Chuyên khoa</p>
                  <b className="text-2xl text-[#053345]">
                    {ticket?.department_name}
                  </b>
                </div>

                <div>
                  <p className="text-lg text-gray-600">Phòng khám</p>
                  <b className="text-2xl text-[#053345]">{ticket?.room_name}</b>
                </div>
              </div>
            ) : (
              <>
                {/* Thông tin bệnh nhân */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6 w-full mt-4">
                  <div>
                    <p className="text-lg text-gray-600">Họ tên bệnh nhân</p>
                    <b className="text-2xl text-[#053345]">Nguyễn Văn A</b>
                  </div>
                  <div>
                    <p className="text-lg text-gray-600">Loại dịch vụ</p>
                    <b className="text-2xl text-[#053345]">
                      {ticket?.service_package_name}
                    </b>
                  </div>
                  <div>
                    <p className="text-lg text-gray-600">Chuyên khoa</p>
                    <b className="text-2xl text-[#053345]">
                      {ticket?.department_name}
                    </b>
                  </div>
                  <div>
                    <p className="text-lg text-gray-600">Phòng khám</p>
                    <b className="text-2xl text-[#053345]">
                      {ticket?.room_name}
                    </b>
                  </div>
                </div>

                {/* Số thứ tự */}
                <div className="flex flex-col items-center justify-center mt-10">
                  <div className="w-[180px] h-[180px] border-4 border-[#053345] rounded-xl flex flex-col items-center justify-center bg-cyan-50">
                    <p className="text-xl text-[#053345] font-semibold">
                      SỐ THỨ TỰ
                    </p>
                    <b className="queue-number text-7xl text-[#053345] mt-2 font-mono">
                      {ticket?.queue_number.toString().padStart(3, "0")}
                    </b>
                  </div>
                </div>
              </>
            )}

            {/* Lưu ý */}
            <div className="print-hide mt-6 rounded-2xl bg-cyan-50 p-5 flex items-start gap-4 border border-[#1A7595]">
              <CircleAlert
                className="text-[#1A7595] mt-1 flex-shrink-0"
                size={32}
              />
              <div className="flex flex-col text-[#1A7595]">
                <b className="text-lg md:text-2xl">Lưu ý</b>
                <p className="mt-1 text-base md:text-xl leading-relaxed">
                  Nhấn <b>&quot;Xác nhận và In phiếu&quot;</b> để nhận số thứ
                  tự. Vui lòng mang theo phiếu này khi đến lượt khám.
                </p>
              </div>
            </div>

            {/* Nút in */}
            <div className="print-hide flex justify-center mt-8">
              <button
                type="button"
                className="relative z-10 pointer-events-auto flex items-center gap-4 bg-[#1A7595] text-white text-2xl font-bold px-20 py-5 rounded-2xl hover:bg-[#145E76] transition shadow-lg"
                onClick={handlePrintAndFinish}
              >
                <Printer size={36} />
                Xác nhận và In phiếu
              </button>
            </div>
          </div>
        </div>
      </div>
      <style jsx global>{`
        @media print {
          @page {
            size: 80mm auto;
            margin: 0;
          }
          body {
            margin: 0 !important;
            padding: 0 !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
            position: relative !important;
          }
          body * {
            visibility: hidden !important;
          }
          #print-area,
          #print-area * {
            visibility: visible !important;
          }
          #print-area {
            position: absolute !important;
            left: 50% !important;
            top: 0 !important;
            transform: translateX(-50%) !important;
            margin: 0 !important;
            width: 74mm !important;
            height: auto !important;
            max-height: none !important;
            align-self: flex-start !important;
          }
          .confirm-page {
            height: auto !important;
          }
          .print-hide {
            display: none !important;
          }
          #print-area {
            width: 74mm !important;
            padding: 2mm !important;
            margin: 0 !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            overflow: visible !important;
          }
          #print-area h1 {
            font-size: 15px !important;
            margin-bottom: 4px !important;
          }
          #print-area p {
            font-size: 12px !important;
          }
          #print-area b {
            font-size: 13px !important;
          }
          #print-area .queue-number {
            font-size: 34px !important;
          }
        }
      `}</style>
    </div>
  );
}

export default function ConfirmPage() {
  return (
    <Suspense fallback={<div className="text-center p-10">Đang tải...</div>}>
      <ConfirmPageContent />
    </Suspense>
  );
}
