/**
 * P1.1 - Centralized API client.
 *
 * RED: test that api wrappers call correct URL + method + body before
 * implementing. Mocks global fetch.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api, configureApi } from "@/lib/api";

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockReset();
  vi.stubGlobal("fetch", mockFetch);
  configureApi({
    chatBase: "http://chat.test",
    mapBase: "http://map.test",
    ttsUrl: "http://tts.test",
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function mockJsonResponse<T>(data: T, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("api.chat.send", () => {
  it("POSTs to {chatBase}/v1/chat/{conversationId}", async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({ ok: true }));

    await api.chat.send("conv-123", {
      role: "user",
      content: "xin chao",
    });

    expect(mockFetch).toHaveBeenCalledOnce();
    const [url, init] = mockFetch.mock.calls[0];
    expect(url).toBe("http://chat.test/v1/chat/conv-123");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({
      role: "user",
      content: "xin chao",
    });
  });

  it("includes X-Tenant-Id header", async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({}));

    await api.chat.send("c1", { role: "user", content: "x" });

    const [, init] = mockFetch.mock.calls[0];
    expect(init.headers["X-Tenant-Id"]).toBe("1");
    expect(init.headers["Content-Type"]).toBe("application/json");
  });

  it("throws ApiError when status >= 400", async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({ detail: "bad" }, 400));

    await expect(api.chat.send("c1", { role: "user", content: "x" }))
      .rejects.toThrow(/400/);
  });
});

describe("api.chat.streamUrl", () => {
  it("returns SSE URL for given conversationId", () => {
    expect(api.chat.streamUrl("conv-123")).toBe(
      "http://chat.test/v1/chat/conv-123/stream",
    );
  });
});

describe("api.maps.getByName", () => {
  it("GETs {mapBase}/v1/maps/{name}", async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({ id: 1, name: "main" }));

    const result = await api.maps.getByName("main");

    const [url, init] = mockFetch.mock.calls[0];
    expect(url).toBe("http://map.test/v1/maps/main");
    expect(init.method).toBe("GET");
    expect(result).toEqual({ id: 1, name: "main" });
  });

  it("returns null when 404", async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({ detail: "not found" }, 404));

    const result = await api.maps.getByName("missing");
    expect(result).toBeNull();
  });
});

describe("api.maps.shortestPath", () => {
  it("POSTs to {mapBase}/v1/maps/shortest-path with start+end", async () => {
    mockFetch.mockResolvedValue(mockJsonResponse({ path: [] }));

    await api.maps.shortestPath({ from: "A", to: "B" });

    const [url, init] = mockFetch.mock.calls[0];
    expect(url).toBe("http://map.test/v1/maps/shortest-path");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ from: "A", to: "B" });
  });
});

describe("api.tts.synthesize", () => {
  it("POSTs to ttsUrl with text", async () => {
    const blob = new Blob(["audio"], { type: "audio/mpeg" });
    mockFetch.mockResolvedValue(new Response(blob, { status: 200 }));

    await api.tts.synthesize("xin chao");

    const [url, init] = mockFetch.mock.calls[0];
    expect(url).toBe("http://tts.test");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ text: "xin chao" });
  });
});

describe("configureApi defaults from process.env", () => {
  it("uses defaults when called with no args", () => {
    configureApi(); // reset to env-based defaults
    // streamUrl should still produce a deterministic URL
    expect(api.chat.streamUrl("c1")).toMatch(/\/v1\/chat\/c1\/stream$/);
  });
});
