/**
 * P1.1 - Centralized API client.
 *
 * Wraps fetch with:
 * - Base URL config from env (chat / map / tts)
 * - Single error handler (throws ApiError on >= 400, except 404 returns null)
 * - Typed responses via generics
 * - X-Tenant-Id header (currently hardcoded to "1" per audit; centralize for
 *   future multi-tenant support)
 *
 * Replaces 9+ scattered fetch calls. See REFACTOR.md.
 */

import type {
  ChatMessage,
  MapData,
  ShortestPathRequest,
  ShortestPathResponse,
  Ticket,
} from "@/types";

export class ApiError extends Error {
  constructor(
    public status: number,
    public url: string,
    public body?: unknown,
  ) {
    super(`API ${status} at ${url}`);
    this.name = "ApiError";
  }
}

interface ApiConfig {
  chatBase: string;
  mapBase: string;
  ttsUrl: string;
  tenantId: string;
  kioskToken: string;
}

const _DEFAULT_CONFIG: ApiConfig = {
  chatBase: process.env.NEXT_PUBLIC_API_PATH || "",
  mapBase: process.env.NEXT_PUBLIC_MAP_API_BASE || "http://localhost:8000",
  ttsUrl:
    process.env.TTS_API_URL || "https://medicagent.cybertech.com.vn/tts",
  tenantId: "1",
  // CSO Finding #2 fix - per-kiosk auth token from env (configured at deploy)
  kioskToken: process.env.NEXT_PUBLIC_KIOSK_TOKEN || "",
};

let _config: ApiConfig = { ..._DEFAULT_CONFIG };

export function configureApi(overrides?: Partial<ApiConfig>) {
  _config = { ..._DEFAULT_CONFIG, ...overrides };
}

function _headers(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Tenant-Id": _config.tenantId,
    ...(extra ?? {}),
  };
  if (_config.kioskToken) {
    headers["X-Kiosk-Token"] = _config.kioskToken;
  }
  return headers;
}

async function _jsonRequest<T>(
  url: string,
  init: RequestInit,
  options: { allow404?: boolean } = {},
): Promise<T | null> {
  const response = await fetch(url, init);

  if (response.status === 404 && options.allow404) {
    return null;
  }

  if (response.status >= 400) {
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      body = await response.text().catch(() => undefined);
    }
    throw new ApiError(response.status, url, body);
  }

  return (await response.json()) as T;
}

export const api = {
  chat: {
    async send(conversationId: string, message: ChatMessage): Promise<unknown> {
      const url = `${_config.chatBase}/v1/chat/${conversationId}`;
      return _jsonRequest(url, {
        method: "POST",
        headers: _headers({
          "Idempotency-Key": `${conversationId}-${Date.now()}`,
        }),
        body: JSON.stringify(message),
      });
    },

    streamUrl(conversationId: string): string {
      return `${_config.chatBase}/v1/chat/${conversationId}/stream`;
    },
  },

  maps: {
    async list(): Promise<MapData[]> {
      const url = `${_config.mapBase}/v1/maps`;
      const result = await _jsonRequest<MapData[]>(url, { method: "GET" });
      return result ?? [];
    },

    async getByName(name: string): Promise<MapData | null> {
      const url = `${_config.mapBase}/v1/maps/${encodeURIComponent(name)}`;
      return _jsonRequest<MapData>(url, { method: "GET" }, { allow404: true });
    },

    async save(map: MapData): Promise<MapData> {
      const url = `${_config.mapBase}/v1/maps`;
      const result = await _jsonRequest<MapData>(url, {
        method: "POST",
        headers: _headers(),
        body: JSON.stringify(map),
      });
      return result as MapData;
    },

    async update(name: string, map: Partial<MapData>): Promise<MapData> {
      const url = `${_config.mapBase}/v1/maps/${encodeURIComponent(name)}`;
      const result = await _jsonRequest<MapData>(url, {
        method: "PUT",
        headers: _headers(),
        body: JSON.stringify(map),
      });
      return result as MapData;
    },

    async delete(name: string): Promise<void> {
      const url = `${_config.mapBase}/v1/maps/${encodeURIComponent(name)}`;
      await _jsonRequest(url, { method: "DELETE" });
    },

    async search(query: string): Promise<MapData[]> {
      const url = `${_config.mapBase}/v1/maps/search?q=${encodeURIComponent(query)}`;
      const result = await _jsonRequest<MapData[]>(url, { method: "GET" });
      return result ?? [];
    },

    async shortestPath(
      req: ShortestPathRequest,
    ): Promise<ShortestPathResponse> {
      const url = `${_config.mapBase}/v1/maps/shortest-path`;
      const result = await _jsonRequest<ShortestPathResponse>(url, {
        method: "POST",
        headers: _headers(),
        body: JSON.stringify(req),
      });
      return result as ShortestPathResponse;
    },
  },

  tts: {
    async synthesize(text: string): Promise<Response> {
      const url = _config.ttsUrl;
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (response.status >= 400) {
        throw new ApiError(response.status, url);
      }
      return response;
    },
  },
};

export type { Ticket };
