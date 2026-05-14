"use client";

import React, { useRef, useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_MAP_API_BASE || "http://localhost:8000";

type NodeType = { x: number; y: number };
type EdgeType = [string, string, number];

export default function PathFinderPage() {
    const canvasRef = useRef<HTMLCanvasElement | null>(null);

    const [mapName, setMapName] = useState("");
    const [startNode, setStartNode] = useState("");
    const [endNode, setEndNode] = useState("");
    const [hospitalId, setHospitalId] = useState<string>("");

    const [nodes, setNodes] = useState<Record<string, NodeType>>({});
    const [edges, setEdges] = useState<EdgeType[]>([]);
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [img, setImg] = useState<HTMLImageElement | null>(null);

    const [path, setPath] = useState<string[]>([]);
    const [directionText, setDirectionText] = useState("");

    // ============================= DRAW CANVAS =============================
    const draw = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d")!;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw background image
        if (img) {
            const scale = (img as any).scale || 1;
            ctx.drawImage(img, 0, 0, img.width * scale, img.height * scale);
        }

        // Highlight edges on path
        const pathEdges = new Set<string>();
        for (let i = 0; i < path.length - 1; i++) {
            pathEdges.add(`${path[i]}-${path[i + 1]}`);
            pathEdges.add(`${path[i + 1]}-${path[i]}`);
        }

        edges.forEach(([a, b, dist]) => {
            const key = `${a}-${b}`;
            if (!pathEdges.has(key)) return;

            const n1 = nodes[a];
            const n2 = nodes[b];
            if (!n1 || !n2) return;

            ctx.strokeStyle = "red";
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.stroke();

            // dist label
            const mx = (n1.x + n2.x) / 2;
            const my = (n1.y + n2.y) / 2;

            ctx.fillStyle = "yellow";
            ctx.fillRect(mx - 18, my - 14, 40, 22);

            ctx.fillStyle = "black";
            ctx.font = "14px Arial";
            ctx.fillText(`${dist}m`, mx - 10, my + 5);
        });

        // Draw nodes on path
        path.forEach((p) => {
            const n = nodes[p];
            if (!n) return;

            ctx.font = "14px Arial";
            const textWidth = ctx.measureText(p).width;

            const paddingX = 10;
            const paddingY = 6;
            const boxWidth = textWidth + paddingX * 2;
            const boxHeight = 26 + paddingY;
            const radius = 8;
            const x = n.x - boxWidth / 2;
            const y = n.y - boxHeight / 2;

            ctx.fillStyle = "#d9534f";
            ctx.beginPath();
            ctx.moveTo(x + radius, y);
            ctx.lineTo(x + boxWidth - radius, y);
            ctx.quadraticCurveTo(x + boxWidth, y, x + boxWidth, y + radius);
            ctx.lineTo(x + boxWidth, y + boxHeight - radius);
            ctx.quadraticCurveTo(x + boxWidth, y + boxHeight, x + boxWidth - radius, y + boxHeight);
            ctx.lineTo(x + radius, y + boxHeight);
            ctx.quadraticCurveTo(x, y + boxHeight, x, y + boxHeight - radius);
            ctx.lineTo(x, y + radius);
            ctx.quadraticCurveTo(x, y, x + radius, y);
            ctx.fill();

            ctx.fillStyle = "white";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(p, n.x, n.y);
        });
    };

    useEffect(() => {
        draw();
    }, [nodes, edges, img, path]);

    // ============================= LOAD IMAGE =============================
    const loadImageOnCanvas = (url: string) => {
        const image = new Image();
        image.crossOrigin = "anonymous";
        image.src = url;

        image.onload = () => {
            let scale = 1;
            const maxW = 800;
            if (image.width > maxW) scale = maxW / image.width;
            (image as any).scale = scale;

            setImg(image);
            const canvas = canvasRef.current;
            if (canvas) {
                canvas.width = image.width * scale;
                canvas.height = image.height * scale;
            }
        };
    };

    // ============================= SEARCH PATH =============================
    const handleSearchPath = async () => {
        if (!mapName || !startNode || !endNode) {
            alert("Nhập tên bản đồ, điểm bắt đầu và kết thúc");
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/v1/maps/shortest-path`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    map_name: mapName,
                    start: startNode,
                    end: endNode,
                    hospital_id: Number(hospitalId)
                }),
            });

            const data = await res.json();
            if (!res.ok) {
                alert(data?.detail || "Không tìm được đường đi");
                return;
            }

            // === Backend trả đầy đủ thông tin bản đồ ===
            const map = data.map;

            setNodes(map.nodes || {});
            setEdges(map.edges || []);
            setImageUrl(map.image_url || null);
            if (map.image_url) loadImageOnCanvas(map.image_url);

            setPath(data.path);
            setDirectionText(data.direction_text);
        } catch (err) {
            console.error(err);
            alert("Lỗi tìm đường");
        }
    };

    // ============================= UI =============================
    return (
        <div style={{ padding: 20, maxWidth: 900, margin: "auto" }}>
            <h2 style={{ textAlign: "center" }}>🚶‍♂️ Tìm đường trên bản đồ</h2>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <input placeholder="Tên bản đồ" value={mapName} onChange={(e) => setMapName(e.target.value)} style={inputStyle} />
                <input placeholder="Điểm bắt đầu" value={startNode} onChange={(e) => setStartNode(e.target.value)} style={inputStyle} />
                <input placeholder="Điểm kết thúc" value={endNode} onChange={(e) => setEndNode(e.target.value)} style={inputStyle} />

                <input type="number" placeholder="Hospital ID" value={hospitalId} onChange={(e) => setHospitalId(e.target.value)} style={inputStyle} />

                <button onClick={handleSearchPath} style={btnStyle}>🔍 Tìm đường</button>
            </div>

            <div style={{ marginTop: 20, display: "flex", justifyContent: "center" }}>
                <canvas ref={canvasRef} />
            </div>

            {directionText && (
                <div style={directionBox}>
                    <strong>📢 Chỉ dẫn:</strong>
                    <pre style={{ whiteSpace: "pre-line" }}>{directionText}</pre>
                </div>
            )}
        </div>
    );
}

// ===== CSS =====
const inputStyle: React.CSSProperties = {
    padding: 10,
    borderRadius: 8,
    border: "1px solid #ccc",
};

const btnStyle: React.CSSProperties = {
    padding: "10px 15px",
    borderRadius: 8,
    background: "#1a7594",
    color: "white",
    border: "none",
    fontWeight: 600,
    cursor: "pointer",
};

const directionBox: React.CSSProperties = {
    marginTop: 20,
    padding: 20,
    background: "#f1f3f5",
    borderRadius: 12,
    border: "1px solid #ccc",
};
