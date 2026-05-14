"use client";

import React, { useEffect } from "react";

export type PopupType = "success" | "error" | "info";

interface ConfirmPopupProps {
    visible: boolean;
    mode: "alert" | "confirm";
    type?: PopupType;
    message: string;
    onConfirm?: () => void;
    onCancel?: () => void;
    autoClose?: boolean; // chỉ dùng cho alert
}

export default function ConfirmPopup({
    visible,
    mode,
    type = "info",
    message,
    onConfirm,
    onCancel,
    autoClose = false,
}: ConfirmPopupProps) {

    // Auto close for alert
    useEffect(() => {
        if (visible && mode === "alert" && autoClose) {
            const t = setTimeout(() => {
                onCancel?.();
            }, 2200);
            return () => clearTimeout(t);
        }
    }, [visible]);

    if (!visible) return null;

    const typeColor = {
        success: "#2ecc71",
        error: "#e74c3c",
        info: "#3498db",
    }[type];

    const typeIcon = {
        success: "✔",
        error: "⚠",
        info: "ℹ",
    }[type];

    return (
        <div
            style={{
                position: "fixed",
                inset: 0,
                background: "rgba(0,0,0,0.45)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 99999,
                animation: "fadeIn 0.2s ease",
            }}
        >
            <div
                style={{
                    width: "360px",
                    background: "white",
                    borderRadius: "12px",
                    padding: "20px",
                    boxShadow: "0 4px 15px rgba(0,0,0,0.15)",
                    animation: "zoomIn 0.22s ease",
                }}
            >
                {/* Icon */}
                <div
                    style={{
                        width: "55px",
                        height: "55px",
                        borderRadius: "50%",
                        background: typeColor,
                        color: "white",
                        fontSize: "28px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        margin: "0 auto 15px",
                    }}
                >
                    {typeIcon}
                </div>

                {/* Message */}
                <p
                    style={{
                        textAlign: "center",
                        fontSize: "16px",
                        padding: "0 10px",
                        color: "#333",
                        whiteSpace: "pre-line",
                    }}
                >
                    {message}
                </p>

                {/* Buttons */}
                <div
                    style={{
                        marginTop: "18px",
                        display: "flex",
                        justifyContent: "center",
                        gap: "12px",
                    }}
                >
                    {mode === "confirm" && (
                        <button
                            onClick={onCancel}
                            style={{
                                padding: "8px 18px",
                                borderRadius: "8px",
                                border: "1px solid #ccc",
                                background: "white",
                                cursor: "pointer",
                                fontWeight: 600,
                            }}
                        >
                            Hủy
                        </button>
                    )}

                    <button
                        onClick={onConfirm}
                        style={{
                            padding: "8px 18px",
                            borderRadius: "8px",
                            background: typeColor,
                            border: "none",
                            color: "white",
                            cursor: "pointer",
                            fontWeight: 600,
                        }}
                    >
                        OK
                    </button>
                </div>
            </div>

            {/* Animations */}
            <style>
                {`
                @keyframes fadeIn {
                    from { opacity: 0 }
                    to { opacity: 1 }
                }
                @keyframes zoomIn {
                    from { transform: scale(0.8); opacity: 0 }
                    to { transform: scale(1); opacity: 1 }
                }
            `}
            </style>
        </div>
    );
}
