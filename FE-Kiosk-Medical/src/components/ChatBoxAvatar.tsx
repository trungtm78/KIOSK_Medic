"use client";

import React from "react";
import Image from "next/image";
import { useKiosk } from "@/hooks/useKiosk";

export default function ChatBotAvatar() {
  const { isBotSpeaking } = useKiosk();

  return (
    <div className="flex flex-col items-center justify-center">
      <Image
        src={
          isBotSpeaking
            ? "/Nhep_mieng.gif" // Bot đang nói
            : "/Nhay_mat.gif" // Bot im lặng
        }
        alt="Chatbot Avatar"
        width={250}
        height={250}
        unoptimized
        priority
        className="object-cover"
      />
    </div>
  );
}
