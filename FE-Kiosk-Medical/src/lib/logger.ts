/**
 * Centralized logger - silent in production, console.* in development.
 *
 * Use instead of bare console.log for dev/debug output. Production builds
 * (`next build`) tree-shake the no-op implementation.
 */

const _IS_DEV = process.env.NODE_ENV !== "production";

export const logger = {
  debug: (...args: unknown[]) => {
    if (_IS_DEV) console.debug(...args);
  },
  info: (...args: unknown[]) => {
    if (_IS_DEV) console.info(...args);
  },
  warn: (...args: unknown[]) => {
    // Warnings always visible
    console.warn(...args);
  },
  error: (...args: unknown[]) => {
    // Errors always visible
    console.error(...args);
  },
};
