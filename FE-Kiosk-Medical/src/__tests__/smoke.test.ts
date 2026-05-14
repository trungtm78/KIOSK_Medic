/**
 * P3.2 - FE smoke test foundation.
 *
 * Pin Vitest setup works before adding behavior tests for KioskProvider
 * and the centralized api client (P1.1).
 */
import { describe, expect, it } from "vitest";

describe("vitest setup", () => {
  it("runs", () => {
    expect(1 + 1).toBe(2);
  });

  it("has jsdom environment", () => {
    expect(typeof window).toBe("object");
    expect(typeof document).toBe("object");
  });
});
