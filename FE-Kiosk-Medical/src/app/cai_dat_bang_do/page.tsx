"use client";

import React, { useEffect, useRef, useState } from "react";

type NodeType = {
    x: number;
    y: number;
};

type EdgeType = [string, string, number];

const CLOUD_NAME = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;
const UPLOAD_PRESET = process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET;
const API_BASE = process.env.NEXT_PUBLIC_MAP_API_BASE || "https://localhost:8000";

export default function Page() {
    const [searchList, setSearchList] = useState<string[]>([]);
    const [typingTimeout, setTypingTimeout] = useState<any>(null);


    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const fileRef = useRef<HTMLInputElement | null>(null);

    const [img, setImg] = useState<HTMLImageElement | null>(null);
    const [imageFile, setImageFile] = useState<File | null>(null); // để upload Cloudinary
    const [imageUrl, setImageUrl] = useState<string | null>(null); // link Cloudinary / BE

    const [mode, setMode] = useState("addNode");
    const [nodes, setNodes] = useState<Record<string, NodeType>>({});
    const [edges, setEdges] = useState<EdgeType[]>([]);
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const draggingNodeRef = useRef<string | null>(null);

    // quản lý map theo tên
    const [mapName, setMapName] = useState("");
    const [loadingSave, setLoadingSave] = useState(false);
    const [loadingLoad, setLoadingLoad] = useState(false);
    const [loadingUpdate, setLoadingUpdate] = useState(false);
    const [loadingDelete, setLoadingDelete] = useState(false);

    // ================= DRAW =================
    const draw = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d")!;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (img) {
            const scale = (img as any).scale || 1;
            ctx.drawImage(img, 0, 0, img.width * scale, img.height * scale);
        }

        ctx.lineWidth = 3;
        ctx.font = "15px Arial";

        // Edges
        edges.forEach(([a, b, dist]) => {
            const n1 = nodes[a];
            const n2 = nodes[b];
            if (!n1 || !n2) return;

            ctx.strokeStyle = "#333";
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.stroke();

            const mx = (n1.x + n2.x) / 2;
            const my = (n1.y + n2.y) / 2;

            ctx.fillStyle = "yellow";
            ctx.fillRect(mx - 12, my - 12, 30, 20);

            ctx.fillStyle = "black";
            ctx.fillText(dist.toString(), mx - 5, my + 5);
        });

        // Nodes
        // Nodes
        Object.entries(nodes).forEach(([name, n]) => {
            ctx.font = "14px Arial";

            // đo text
            const textWidth = ctx.measureText(name).width;
            const paddingX = 8;
            const paddingY = 6;

            const boxWidth = textWidth + paddingX * 2;
            const boxHeight = 20 + paddingY * 2;

            const x = n.x - boxWidth / 2;
            const y = n.y - boxHeight / 2;

            // vẽ hình chữ nhật bo góc
            ctx.fillStyle = "#d9534f";
            const radius = 6;

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

            // vẽ text
            ctx.fillStyle = "white";
            ctx.textBaseline = "middle";
            ctx.textAlign = "center";
            ctx.fillText(name, n.x, n.y);
        });
    };

    useEffect(() => {
        draw();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [nodes, edges, img]);

    // ================= HELPER: setup image on canvas =================
    const setupImageOnCanvas = (image: HTMLImageElement) => {
        const maxW = 800;
        let scale = 1;

        if (image.width > maxW) {
            scale = maxW / image.width;
        }

        (image as any).scale = scale;
        setImg(image);

        const canvas = canvasRef.current;
        if (canvas) {
            canvas.width = image.width * scale;
            canvas.height = image.height * scale;
        }
    };

    const loadImageFromUrl = (url: string) => {
        const image = new Image();
        image.crossOrigin = "anonymous";
        image.src = url;

        image.onload = () => {
            setupImageOnCanvas(image);
        };

        image.onerror = () => {
            console.error("Không tải được ảnh từ URL:", url);
            alert("Không tải được ảnh bản đồ từ image_url.");
        };
    };

    // ================= UPLOAD IMAGE (local file) =================
    const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const f = e.target.files?.[0];
        if (!f) return;

        // RESET toàn bộ khi chọn ảnh mới
        setNodes({});
        setEdges([]);
        setSelectedNode(null);
        draggingNodeRef.current = null;
        setMapName("");
        setImageUrl(null);

        if (canvasRef.current) {
            const ctx = canvasRef.current.getContext("2d");
            ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        }

        // Set ảnh mới
        setImageFile(f);

        const image = new Image();
        image.src = URL.createObjectURL(f);

        image.onload = () => {
            setupImageOnCanvas(image);
        };
    };

    // Helpers cho canvas
    const mousePos = (evt: MouseEvent) => {
        const canvas = canvasRef.current!;
        const r = canvas.getBoundingClientRect();
        return { x: evt.clientX - r.left, y: evt.clientY - r.top };
    };

    const findNodeAt = (x: number, y: number) => {
        for (const name in nodes) {
            const n = nodes[name];
            if (Math.hypot(n.x - x, n.y - y) <= 10) return name;
        }
        return null;
    };

    const findEdgeAt = (x: number, y: number) => {
        for (const [a, b, dist] of edges) {
            const n1 = nodes[a];
            const n2 = nodes[b];
            if (!n1 || !n2) continue;

            const t =
                ((x - n1.x) * (n2.x - n1.x) + (y - n1.y) * (n2.y - n1.y)) /
                ((n2.x - n1.x) ** 2 + (n2.y - n1.y) ** 2);

            if (t < 0 || t > 1) continue;

            const px = n1.x + t * (n2.x - n1.x);
            const py = n1.y + t * (n2.y - n1.y);

            if (Math.hypot(px - x, py - y) <= 8) return { a, b, dist };
        }
        return null;
    };

    // ================= CANVAS EVENTS =================
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const mousedown = (e: MouseEvent) => {
            const { x, y } = mousePos(e);
            const clicked = findNodeAt(x, y);
            const clickedEdge = findEdgeAt(x, y);

            if (mode === "addNode") {
                const name = prompt("Tên node?");
                if (name) setNodes((prev) => ({ ...prev, [name]: { x, y } }));
                return;
            }

            if (mode === "deleteNode" && clicked) {
                const del = clicked;
                setNodes((prev) => {
                    const copy = { ...prev };
                    delete copy[del];
                    return copy;
                });
                setEdges((prev) => prev.filter((e) => e[0] !== del && e[1] !== del));
                return;
            }

            if (mode === "editNode" && clicked) {
                const newName = prompt("Tên node mới?", clicked);
                if (!newName || newName === clicked) return;

                setNodes((prev) => {
                    const copy = { ...prev };
                    copy[newName] = { ...copy[clicked] };
                    delete copy[clicked];
                    return copy;
                });

                setEdges((prev) =>
                    prev.map((e) => [
                        e[0] === clicked ? newName : e[0],
                        e[1] === clicked ? newName : e[1],
                        e[2],
                    ])
                );
                return;
            }

            if (mode === "addEdge") {
                if (!clicked) return;

                if (!selectedNode) {
                    setSelectedNode(clicked);
                    alert("Chọn node thứ 2 để tạo cạnh!")
                } else {
                    if (selectedNode !== clicked) {
                        const d = prompt("Khoảng cách?");
                        if (d) {
                            setEdges((prev) => [
                                ...prev,
                                [selectedNode, clicked, Number(d)],
                            ]);
                        }
                    }
                    setSelectedNode(null);
                }
                return;
            }

            if (mode === "deleteEdge" && clickedEdge) {
                setEdges((prev) =>
                    prev.filter(
                        (e) =>
                            !(
                                (e[0] === clickedEdge.a && e[1] === clickedEdge.b) ||
                                (e[1] === clickedEdge.a && e[0] === clickedEdge.b)
                            )
                    )
                );
                return;
            }

            if (mode === "editEdge" && clickedEdge) {
                const newW = prompt("Khoảng cách mới?", clickedEdge.dist.toString());
                if (!newW) return;

                setEdges((prev) =>
                    prev.map((e) =>
                        (e[0] === clickedEdge.a && e[1] === clickedEdge.b) ||
                            (e[1] === clickedEdge.a && e[0] === clickedEdge.b)
                            ? [e[0], e[1], Number(newW)]
                            : e
                    )
                );
                return;
            }

            if (mode === "dragNode" && clicked) {
                draggingNodeRef.current = clicked;
            }
        };

        const mousemove = (e: MouseEvent) => {
            if (!draggingNodeRef.current) return;

            const { x, y } = mousePos(e);
            const name = draggingNodeRef.current;

            setNodes((prev) => ({
                ...prev,
                [name]: { x, y },
            }));
        };

        const mouseup = () => {
            draggingNodeRef.current = null;
        };

        canvas.addEventListener("mousedown", mousedown);
        canvas.addEventListener("mousemove", mousemove);
        canvas.addEventListener("mouseup", mouseup);

        return () => {
            canvas.removeEventListener("mousedown", mousedown);
            canvas.removeEventListener("mousemove", mousemove);
            canvas.removeEventListener("mouseup", mouseup);
        };
    }, [nodes, edges, mode, selectedNode]);

    // ================= BUILD graph & weights =================
    const buildGraphAndWeights = () => {
        const graph: Record<string, string[]> = {};
        const weights: Record<string, number> = {};

        for (const n in nodes) graph[n] = [];

        edges.forEach(([a, b, dist]) => {
            graph[a].push(b);
            graph[b].push(a);
            weights[`${a}-${b}`] = dist;
            weights[`${b}-${a}`] = dist;
        });

        return { graph, weights };
    };

    // ================= EXPORT JSON (preview & copy) =================
    const exportJson = () => {
        const { graph, weights } = buildGraphAndWeights();
        return JSON.stringify(
            {
                name: mapName || undefined,
                nodes,
                edges,
                graph,
                weights,
                image_url: imageUrl || undefined,
            },
            null,
            2
        );
    };

    // ================= CLOUDINARY UPLOAD =================
    const uploadImageIfNeeded = async (): Promise<string | null> => {
        if (!CLOUD_NAME || !UPLOAD_PRESET) {
            alert("Thiếu cấu hình Cloudinary ENV (CLOUD_NAME hoặc UPLOAD_PRESET).");
            return null;
        }

        // Nếu có file mới → upload
        if (imageFile) {
            const formData = new FormData();
            formData.append("file", imageFile);
            formData.append("upload_preset", UPLOAD_PRESET);

            const res = await fetch(
                `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!res.ok) {
                console.error("Upload Cloudinary lỗi:", await res.text());
                throw new Error("Upload ảnh lên Cloudinary thất bại");
            }

            const data = await res.json();
            const url = data.secure_url as string;
            setImageUrl(url);
            return url;
        }

        // Không có file mới → dùng url cũ (load từ BE)
        if (imageUrl) return imageUrl;

        alert("Chưa có ảnh bản đồ để upload/lưu.");
        return null;
    };

    // ================= API: Lưu map mới =================
    // ================= API: Lưu map mới =================
    const handleSaveMap = async () => {
        const name = prompt("Nhập tên bản đồ muốn lưu?");
        if (!name || !name.trim()) {
            alert("Bạn chưa nhập tên bản đồ.");
            return;
        }

        if (!Object.keys(nodes).length) {
            alert("Bản đồ chưa có node nào.");
            return;
        }

        try {
            setLoadingSave(true);
            const imgUrl = await uploadImageIfNeeded();
            if (!imgUrl) return;

            const { graph, weights } = buildGraphAndWeights();

            const payload = {
                name: name.trim(),
                nodes,
                edges,
                graph,
                weights,
                image_url: imgUrl,
            };

            const res = await fetch(`${API_BASE}/v1/maps`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const data = await res.json().catch(() => null);
                alert(data?.detail || "Lưu bản đồ thất bại.");
                return;
            }

            alert("Lưu bản đồ thành công!");

            // cập nhật ô tìm kiếm về tên map vừa lưu
            setMapName(name.trim());
        } catch (err: any) {
            console.error(err);
            alert(err.message || "Có lỗi khi lưu bản đồ.");
        } finally {
            setLoadingSave(false);
        }
    };

    // ================= API: Tải (search) map theo tên =================
    const handleLoadMap = async () => {
        if (!mapName.trim()) {
            alert("Nhập tên bản đồ để tải.");
            return;
        }

        try {
            setLoadingLoad(true);

            const res = await fetch(
                `${API_BASE}/v1/maps/${encodeURIComponent(mapName.trim())}`
            );

            if (!res.ok) {
                const data = await res.json().catch(() => null);
                alert(data?.detail || "Không tìm thấy bản đồ.");
                return;
            }

            const data = await res.json();

            setNodes(data.nodes || {});
            setEdges(data.edges || []);
            setImageUrl(data.image_url || null);
            setImageFile(null); // map tải về dùng image_url, không có file local

            if (data.image_url) {
                loadImageFromUrl(data.image_url);
            } else {
                setImg(null);
            }

            alert("Tải bản đồ thành công!");
        } catch (err) {
            console.error(err);
            alert("Có lỗi khi tải bản đồ.");
        } finally {
            setLoadingLoad(false);
        }
    };

    // ================= API: Cập nhật map =================
    const handleUpdateMap = async () => {
        if (!mapName.trim()) {
            alert("Nhập tên bản đồ để cập nhật.");
            return;
        }
        if (!Object.keys(nodes).length) {
            alert("Bản đồ chưa có node nào.");
            return;
        }

        try {
            setLoadingUpdate(true);
            const imgUrl = await uploadImageIfNeeded();
            if (!imgUrl) return;

            const { graph, weights } = buildGraphAndWeights();

            // MapUpdate không cần name
            const payload = {
                nodes,
                edges,
                graph,
                weights,
                image_url: imgUrl,
            };

            const res = await fetch(
                `${API_BASE}/v1/maps/${encodeURIComponent(mapName.trim())}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                }
            );

            if (!res.ok) {
                const data = await res.json().catch(() => null);
                alert(data?.detail || "Cập nhật bản đồ thất bại.");
                return;
            }

            alert("Cập nhật bản đồ thành công!");
        } catch (err: any) {
            console.error(err);
            alert(err.message || "Có lỗi khi cập nhật bản đồ.");
        } finally {
            setLoadingUpdate(false);
        }
    };

    // ================= API: Xóa map =================
    const handleDeleteMap = async () => {
        if (!mapName.trim()) {
            alert("Nhập tên bản đồ để xóa.");
            return;
        }

        if (!confirm(`Bạn có chắc muốn xóa bản đồ "${mapName.trim()}"?`)) {
            return;
        }

        try {
            setLoadingDelete(true);

            const res = await fetch(
                `${API_BASE}/v1/maps/${encodeURIComponent(mapName.trim())}`,
                {
                    method: "DELETE",
                }
            );

            if (!res.ok) {
                const data = await res.json().catch(() => null);
                alert(data?.detail || "Xóa bản đồ thất bại.");
                return;
            }

            // clear state
            setNodes({});
            setEdges([]);
            setImg(null);
            setImageFile(null);
            setImageUrl(null);

            alert("Xóa bản đồ thành công!");
        } catch (err) {
            console.error(err);
            alert("Có lỗi khi xóa bản đồ.");
        } finally {
            setLoadingDelete(false);
        }
    };

    const handleSearchTyping = (value: string) => {
        setMapName(value);

        if (typingTimeout) clearTimeout(typingTimeout);

        const t = setTimeout(async () => {
            if (!value.trim()) {
                setSearchList([]);
                return;
            }

            const res = await fetch(`${API_BASE}/v1/maps/search?q=${encodeURIComponent(value)}`);
            if (!res.ok) {
                setSearchList([]);
                return;
            }

            const data = await res.json();
            setSearchList(data.results || []);
        }, 300);

        setTypingTimeout(t);
    };

    const loadMapByName = async (name: string) => {
        try {
            const res = await fetch(`${API_BASE}/v1/maps/${encodeURIComponent(name)}`);
            if (!res.ok) {
                alert("Không tìm thấy bản đồ.");
                return;
            }

            const data = await res.json();

            setMapName(name);
            setSearchList([]);

            setNodes(data.nodes || {});
            setEdges(data.edges || []);
            setImageUrl(data.image_url || null);
            setImageFile(null);

            if (data.image_url) loadImageFromUrl(data.image_url);
            else setImg(null);

            alert("Tải bản đồ thành công!");
        } catch (err) {
            console.error(err);
            alert("Lỗi khi tải bản đồ!");
        }
    };


    // ==================== UI ====================
    return (
        <div style={{ padding: 20, maxWidth: 1200, margin: "auto" }}>
            {/* Header */}
            <div style={{
                background: "linear-gradient(135deg, #1a7594 0%, #2a94b8 100%)",
                padding: "10px",
                borderRadius: "12px",
                marginBottom: "25px",
                boxShadow: "0 4px 12px rgba(26, 117, 148, 0.3)",
                color: "white"
            }}>
                <div style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "15px"
                }}>
                    <div style={{
                        background: "white",
                        padding: "4px",
                        borderRadius: "10px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center"
                    }}>
                        <img
                            src="/map/map.png"
                            alt="map"
                            style={{ width: 32, height: 32 }}
                        />
                    </div>
                    <p style={{
                        fontSize: "20px",
                        fontWeight: "600",
                        textTransform: "uppercase",
                        letterSpacing: "1px",
                        margin: 0,
                        textShadow: "0 2px 4px rgba(0,0,0,0.1)"
                    }}>
                        Thiết kế bản đồ bệnh viện
                    </p>
                </div>
            </div>

            {/* Control Panel */}
            <div style={{
                background: "#f8f9fa",
                padding: "20px",
                borderRadius: "12px",
                marginBottom: "20px",
                border: "1px solid #e9ecef"
            }}>
                {/* Map Name & Actions Row */}
                {/* SEARCH + SAVE/UPDATE/DELETE IN ONE ROW */}
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                        marginBottom: "15px",
                        flexWrap: "nowrap"
                    }}
                >
                    {/* SEARCH COLUMN */}
                    <div style={{ position: "relative", flex: 1 }}>
                        <input
                            type="text"
                            placeholder="Tìm bản đồ..."
                            value={mapName}
                            onChange={(e) => handleSearchTyping(e.target.value)}
                            style={{
                                width: "100%",
                                padding: "10px 14px",
                                borderRadius: "8px",
                                border: "2px solid #e9ecef",
                                fontSize: "14px",
                            }}
                        />

                        {searchList.length > 0 && (
                            <div
                                style={{
                                    position: "absolute",
                                    top: "45px",
                                    left: 0,
                                    width: "100%",
                                    background: "white",
                                    border: "1px solid #ddd",
                                    borderRadius: "8px",
                                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                                    zIndex: 20,
                                }}
                            >
                                {searchList.map((name) => (
                                    <div
                                        key={name}
                                        onClick={() => loadMapByName(name)}
                                        style={{
                                            padding: "10px 14px",
                                            cursor: "pointer",
                                            borderBottom: "1px solid #eee",
                                        }}
                                        onMouseOver={(e) =>
                                            (e.currentTarget.style.background = "#f1f3f5")
                                        }
                                        onMouseOut={(e) =>
                                            (e.currentTarget.style.background = "white")
                                        }
                                    >
                                        {name}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* ACTION BUTTONS */}
                    <div style={{ display: "flex", gap: "8px", whiteSpace: "nowrap" }}>
                        <button
                            onClick={handleSaveMap}
                            disabled={loadingSave}
                            style={{
                                padding: "10px 16px",
                                borderRadius: "8px",
                                border: "none",
                                cursor: loadingSave ? "not-allowed" : "pointer",
                                background: "#1a7594",
                                color: "white",
                                fontWeight: "600",
                                fontSize: "14px"
                            }}
                        >
                            💾 {loadingSave ? "Đang lưu..." : "Lưu bản đồ"}
                        </button>

                        <button
                            onClick={handleUpdateMap}
                            disabled={loadingUpdate}
                            style={{
                                padding: "10px 16px",
                                borderRadius: "8px",
                                border: "none",
                                cursor: loadingUpdate ? "not-allowed" : "pointer",
                                background: "#dca009ff",
                                color: "#fff",
                                fontWeight: "600",
                                fontSize: "14px"
                            }}
                        >
                            ♻️ {loadingUpdate ? "Đang cập nhật..." : "Cập nhật bản đồ"}
                        </button>

                        <button
                            onClick={handleDeleteMap}
                            disabled={loadingDelete}
                            style={{
                                padding: "10px 16px",
                                borderRadius: "8px",
                                border: "none",
                                cursor: loadingDelete ? "not-allowed" : "pointer",
                                background: "#dc3545",
                                color: "white",
                                fontWeight: "600",
                                fontSize: "14px"
                            }}
                        >
                            🗑 {loadingDelete ? "Đang xóa..." : "Xóa bản đồ"}
                        </button>
                    </div>
                </div>

                {/* Tools & Upload Row */}
                <div style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "15px",
                    flexWrap: "wrap"
                }}>
                    {/* Tools */}
                    <div style={{
                        display: "flex",
                        gap: "6px",
                        flexWrap: "wrap",
                        flex: "1"
                    }}>
                        {[
                            ["addNode", "➕ Thêm Node"],
                            ["addEdge", "🔗 Thêm Cạnh"],
                            ["editNode", "✏️ Sửa Node"],
                            ["deleteNode", "❌ Xóa Node"],
                            ["editEdge", "✏️ Sửa Cạnh"],
                            ["deleteEdge", "❌ Xóa Cạnh"],
                            ["dragNode", "🖐️ Kéo Node"],
                        ].map(([m, label]) => (
                            <button
                                key={m}
                                onClick={() => setMode(m)}
                                style={{
                                    padding: "8px 12px",
                                    borderRadius: "6px",
                                    border: mode === m ? "none" : "1px solid #dee2e6",
                                    borderWidth: mode === m ? "0px" : "1px",
                                    borderStyle: mode === m ? "none" : "solid",
                                    borderColor: mode === m ? "transparent" : "#dee2e6",
                                    cursor: "pointer",
                                    background: mode === m ? "#1a7594" : "white",
                                    color: mode === m ? "white" : "#495057",
                                    fontWeight: "500",
                                    fontSize: "13px",
                                    transition: "all 0.2s",
                                    boxShadow: mode === m ? "0 2px 4px rgba(26, 117, 148, 0.3)" : "0 1px 2px rgba(0,0,0,0.05)"
                                }}
                                onMouseOver={(e) => {
                                    if (mode !== m) {
                                        e.currentTarget.style.background = "#f8f9fa";
                                        e.currentTarget.style.borderColor = "#1a7594";
                                    }
                                }}
                                onMouseOut={(e) => {
                                    if (mode !== m) {
                                        e.currentTarget.style.background = "white";
                                        e.currentTarget.style.borderColor = "#dee2e6";
                                    }
                                }}
                            >
                                {label}
                            </button>
                        ))}
                    </div>

                    <button
                        onClick={() => {
                            if (!confirm("Bạn có chắc muốn RESET toàn bộ bản đồ hiện tại?")) return;
                            setNodes({});
                            setEdges([]);
                            setSelectedNode(null);
                            draggingNodeRef.current = null;
                            setImg(null);
                            setImageFile(null);
                            setImageUrl(null);
                            setMapName("");
                            if (canvasRef.current) {
                                const ctx = canvasRef.current.getContext("2d");
                                ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
                            }
                        }}
                        style={{
                            padding: "8px 12px",
                            borderRadius: "6px",
                            cursor: "pointer",
                            background: "#6c757d",
                            color: "white",
                            fontWeight: "600"
                        }}
                    >
                        🔄 Reset
                    </button>

                    {/* Upload Button */}
                    <label
                        style={{
                            padding: "10px 18px",
                            background: "#1a7594",
                            color: "white",
                            borderRadius: "8px",
                            fontWeight: "600",
                            cursor: "pointer",
                            fontSize: "14px",
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                            transition: "all 0.2s",
                            border: "none",
                            boxShadow: "0 2px 4px rgba(26, 117, 148, 0.3)",
                            whiteSpace: "nowrap"
                        }}
                        onMouseOver={(e) => {
                            const target = e.currentTarget as HTMLLabelElement;
                            target.style.background = "#155d77";
                        }}
                        onMouseOut={(e) => {
                            const target = e.currentTarget as HTMLLabelElement;
                            target.style.background = "#1a7594";
                        }}
                    >
                        📁 Chọn ảnh bản đồ
                        <input
                            type="file"
                            accept="image/png, image/jpeg, image/jpg"
                            ref={fileRef}
                            onChange={handleUpload}
                            style={{ display: "none" }}
                        />
                    </label>
                </div>
            </div>

            {/* Canvas centered */}
            <div
                style={{
                    display: "flex",
                    justifyContent: "center",
                    padding: 20,
                }}
            >
                <div
                    style={{
                        border: "1px solid #bbb",
                        boxShadow: "0 3px 10px rgba(0,0,0,0.15)",
                    }}
                >
                    <canvas ref={canvasRef} />
                </div>
            </div>
        </div>
    );
}
