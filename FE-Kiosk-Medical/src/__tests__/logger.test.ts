/**
 * P1.5 - logger should silence debug/info in production, always show warn/error.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { logger } from "@/lib/logger";

describe("logger", () => {
  let debugSpy: ReturnType<typeof vi.spyOn>;
  let infoSpy: ReturnType<typeof vi.spyOn>;
  let warnSpy: ReturnType<typeof vi.spyOn>;
  let errorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    debugSpy = vi.spyOn(console, "debug").mockImplementation(() => {});
    infoSpy = vi.spyOn(console, "info").mockImplementation(() => {});
    warnSpy = vi.spyOn(console, "warn").mockImplementation(() => {});
    errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // NODE_ENV in vitest is 'test', which is treated as non-production (verbose).
  it("logger.debug calls console.debug in non-production", () => {
    logger.debug("hello");
    expect(debugSpy).toHaveBeenCalledWith("hello");
  });

  it("logger.info calls console.info in non-production", () => {
    logger.info("hello");
    expect(infoSpy).toHaveBeenCalledWith("hello");
  });

  it("logger.warn always calls console.warn", () => {
    logger.warn("careful");
    expect(warnSpy).toHaveBeenCalledWith("careful");
  });

  it("logger.error always calls console.error", () => {
    logger.error("boom");
    expect(errorSpy).toHaveBeenCalledWith("boom");
  });
});
