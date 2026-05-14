/**
 * Shared types across the kiosk app.
 *
 * Consolidates duplicates that previously lived in:
 * - context/KioskProvider.tsx (Ticket)
 * - app/chon-chuyen-khoa/page.tsx (Ticket)
 * - app/tu-van/xac-nhan-in-phieu/page.tsx (Ticket)
 * - app/xac-nhan-in-phieu/page.tsx (Ticket)
 */

export interface Ticket {
  queue_number?: string;
  service_name?: string;
  doctor_name?: string;
  room?: string;
  department?: string;
  patient_name?: string;
  printed_at?: string;
  [key: string]: unknown;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface MapNode {
  id: string;
  name?: string;
  x: number;
  y: number;
  type?: string;
}

export interface MapEdge {
  from: string;
  to: string;
  weight?: number;
}

export interface MapData {
  id?: number | string;
  name: string;
  background_url?: string;
  nodes: MapNode[];
  edges: MapEdge[];
  [key: string]: unknown;
}

export interface ShortestPathRequest {
  from: string;
  to: string;
  map_name?: string;
}

export interface ShortestPathResponse {
  path: MapNode[];
  distance?: number;
}
