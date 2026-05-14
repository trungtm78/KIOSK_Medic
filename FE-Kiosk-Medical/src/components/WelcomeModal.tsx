"use client";

import React from "react";

interface WelcomeModalProps {
  onStart: () => void;
}

export default function WelcomeModal({ onStart }: WelcomeModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 max-w-lg w-full text-center flex flex-col items-center gap-6">
        <h1 className="text-3xl md:text-4xl font-bold text-[#053345]">
          BỆNH VIỆN KIOSK
        </h1>
        <p className="text-gray-700 text-lg md:text-xl">
          Xin kính chào Quý khách. Vui lòng nhấn &quot;Bắt đầu&quot; để hệ thống
          có thể lắng nghe và hỗ trợ bạn.
        </p>
        <button
          onClick={onStart}
          className="mt-4 w-full max-w-xs bg-[#1A7595] hover:bg-[#145E76] text-white font-bold rounded-lg py-4 text-xl md:text-2xl shadow-lg transition-transform transform hover:scale-105"
        >
          Bắt đầu
        </button>
      </div>
    </div>
  );
}
