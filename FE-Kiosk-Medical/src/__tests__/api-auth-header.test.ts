/**
 * W4.6 - api client must send X-Kiosk-Token header when configured (CSO Finding #2).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api, configureApi } from "@/lib/api";

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockReset();
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function mockJson<T>(data: T, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("api.chat.send with kiosk token", () => {
  it("includes X-Kiosk-Token header when configured", async () => {
    configureApi({
      chatBase: "http://chat.test",
      kioskToken: "kt_abc123def456",
    });
    mockFetch.mockResolvedValue(mockJson({ ok: true }));

    await api.chat.send("c1", { role: "user", content: "x" });

    const [, init] = mockFetch.mock.calls[0];
    expect(init.headers["X-Kiosk-Token"]).toBe("kt_abc123def456");
  });

  it("omits X-Kiosk-Token header when token not set", async () => {
    configureApi({
      chatBase: "http://chat.test",
      kioskToken: "",
    });
    mockFetch.mockResolvedValue(mockJson({ ok: true }));

    await api.chat.send("c1", { role: "user", content: "x" });

    const [, init] = mockFetch.mock.calls[0];
    expect(init.headers["X-Kiosk-Token"]).toBeUndefined();
  });
});

describe("api.maps with kiosk token", () => {
  it("includes X-Kiosk-Token in POST maps.shortestPath", async () => {
    configureApi({
      mapBase: "http://map.test",
      kioskToken: "kt_token_xyz",
    });
    mockFetch.mockResolvedValue(mockJson({ path: [] }));

    await api.maps.shortestPath({ from: "A", to: "B" });

    const [, init] = mockFetch.mock.calls[0];
    expect(init.headers["X-Kiosk-Token"]).toBe("kt_token_xyz");
  });
});
