"use client";

import React, { useEffect, useRef, useState } from "react";

type NodeType = { x: number; y: number };
type EdgeType = [string, string, number];

interface Props {
  nodes: Record<string, NodeType>;
  edges: EdgeType[];
  path: string[];
  imageUrl: string;
}

export default function NavigationMap({ nodes, edges, path, imageUrl }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [img, setImg] = useState<HTMLImageElement | null>(null);

  // ============================= LOAD IMAGE =============================
  useEffect(() => {
    if (!imageUrl) return;

    const image = new Image();
    image.crossOrigin = "anonymous";
    image.src = imageUrl;

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
  }, [imageUrl]);

  // ============================= DRAW =============================
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !img) return;

    const ctx = canvas.getContext("2d")!;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const scale = (img as any).scale || 1;
    ctx.drawImage(img, 0, 0, img.width * scale, img.height * scale);

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

    // Draw node box
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
      ctx.quadraticCurveTo(
        x + boxWidth,
        y + boxHeight,
        x + boxWidth - radius,
        y + boxHeight
      );
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
  }, [nodes, edges, path, img]);

  return (
    <div className="flex justify-center mt-6">
      <canvas ref={canvasRef} />
    </div>
  );
}
