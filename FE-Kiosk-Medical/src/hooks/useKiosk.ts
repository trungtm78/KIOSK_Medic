"use client";

import { useContext } from "react";
import { KioskContext } from "@/context/KioskProvider";

export const useKiosk = () => {
  const context = useContext(KioskContext);
  if (context === undefined) {
    throw new Error("useKiosk must be used within a KioskProvider");
  }
  return context;
};
