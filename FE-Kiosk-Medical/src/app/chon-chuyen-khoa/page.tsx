"use client";

import React, { useEffect, useState, Suspense, useRef } from "react";
import { Search, Building2, ChevronRight } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useKiosk } from "@/hooks/useKiosk";
import ChatBotAvatar from "@/components/ChatBoxAvatar";
import { useOrientation } from "@/hooks/useOrientation";
import WelcomeModal from "@/components/WelcomeModal";

interface DepartmentOption {
  id: number | string;
  name: string;
}

interface Ticket {
  registration_id: number;
  department_id: number;
  room_id: number;
  queue_date: string;
  queue_number: number;
  status: string;
  registration_time: string;
  hospital_name: string;
  department_name: string;
  room_name: string;
  service_package_name: string;
  kiosk_location: string;
}

function DepartmentSelectContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isLandscape } = useOrientation();
  const [showWelcomeModal, setShowWelcomeModal] = useState(true);

  const {
    conversationId,
    botPrompt,
    sendChatMessage,
    registerStreamCallback,
    displayText,
  } = useKiosk();

  const [prompt, setPrompt] = useState("LỰA CHỌN CHUYÊN KHOA");
  const [departments, setDepartments] = useState<DepartmentOption[]>([]);
  const [filteredDepartments, setFilteredDepartments] = useState<
    DepartmentOption[]
  >([]);
  const [search, setSearch] = useState("");
  const ticketRef = useRef<Ticket | null>(null);

  // --- Lấy options từ URL ---
  useEffect(() => {
    if (!conversationId) {
      router.replace("/");
      return;
    }

    const promptFromUrl = searchParams.get("prompt");
    if (promptFromUrl) setPrompt(decodeURIComponent(promptFromUrl));

    const optionsFromUrl = searchParams.get("options");
    if (optionsFromUrl) {
      try {
        const parsed = JSON.parse(decodeURIComponent(optionsFromUrl));
        if (Array.isArray(parsed)) {
          setDepartments(parsed);
          setFilteredDepartments(parsed);
        }
      } catch (err) {
        console.error("❌ Lỗi khi parse options:", err);
      }
    }
  }, [conversationId, router, searchParams]);

  // --- Nhận vé và điều hướng ---
  useEffect(() => {
    if (!conversationId) return;

    const handleBotTicket = (data: { ticket?: { ticket?: Ticket } }) => {
      if (data.ticket?.ticket) ticketRef.current = data.ticket.ticket;
    };

    const handleStateUpdate = (parsed: { state: string }) => {
      if (parsed.state === "FLOW_ISSUE_TICKET.CONFIRM") {
        if (ticketRef.current) {
          const params = new URLSearchParams();
          params.append("ticket", JSON.stringify(ticketRef.current));
          router.push(`/xac-nhan-in-phieu?${params.toString()}`);
        }
      }
    };

    const cleanup1 = registerStreamCallback("bot.ticket", handleBotTicket);
    const cleanup2 = registerStreamCallback("state.updated", handleStateUpdate);
    return () => {
      cleanup1();
      cleanup2();
    };
  }, [conversationId, registerStreamCallback, router]);

  // --- Tìm kiếm ---
  useEffect(() => {
    if (search.trim() === "") setFilteredDepartments(departments);
    else
      setFilteredDepartments(
        departments.filter((d) =>
          d.name.toLowerCase().includes(search.toLowerCase())
        )
      );
  }, [search, departments]);

  const handleSelectDepartment = (dep: DepartmentOption) => {
    sendChatMessage(`tôi muốn khám ${dep.name}`);
  };

  // --- Giao diện ---
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
          className={`flex flex-col items-center text-center   ${
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
            className={`bg-white p-6 rounded-3xl rounded-tl-none max-w-2xl z-20 h-[200px]  flex items-center justify-center ${
              isLandscape ? "mt-[200px]" : "mt-0"
            }`}
          >
            {botPrompt ? (
              <p className="text-gray-500 text-2xl md:text-3xl font-semibold leading-relaxed line-clamp-2">
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

        {/* --- Bên phải / Dưới: Danh sách khoa --- */}
        <div
          className={`flex flex-col items-center flex-1 bg-transparent ${
            isLandscape ? "flex-[7] h-full" : "flex-1 max-h-[60vh]"
          } space-y-8 ${isLandscape ? "justify-center" : "justify-start"} w-full`}
        >
          {/* Ô tìm kiếm */}
          <div className="relative mb-6 shrink-0 mt-4 w-full">
            <Search
              className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500"
              size={28}
            />
            <input
              type="text"
              placeholder="Nhập tên chuyên khoa cần tìm..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full h-24 bg-white text-3xl border border-gray-300 rounded-xl pl-14 pr-4 py-4 focus:ring-2 focus:ring-blue-400 focus:outline-none"
            />
          </div>

          {/* Danh sách scrollable */}
          <div className="flex-1 min-h-0 overflow-y-auto pr-2 w-full">
            {filteredDepartments.length === 0 ? (
              <p className="text-gray-500 text-center text-3xl mt-6">
                Không tìm thấy chuyên khoa phù hợp
              </p>
            ) : (
              filteredDepartments.map((dep, index) => {
                const isLast = index === filteredDepartments.length - 1;
                return (
                  <button
                    key={dep.id}
                    onClick={() => handleSelectDepartment(dep)}
                    className={`w-full h-30 bg-[#1A7595] text-white rounded-2xl px-6 py-6 text-2xl flex justify-between items-center hover:bg-[#145E76] transition-all text-left ${
                      isLast ? "mb-20" : "mb-5"
                    }`}
                    disabled={!conversationId}
                  >
                    <div className="flex items-center gap-4">
                      <div className="bg-[#0B556E] p-3 rounded-full flex-shrink-0">
                        <Building2 size={28} color="#fff" />
                      </div>
                      <span className="font-semibold text-3xl text-left">
                        {dep.name}
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

export default function DepartmentSelectPage() {
  return (
    <Suspense fallback={<div className="text-center p-10">Đang tải...</div>}>
      <DepartmentSelectContent />
    </Suspense>
  );
}
