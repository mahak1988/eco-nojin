/**
 * Tests for cms | تست‌های cms
 *
 * Auto-scaffolded by phase1_complete_apps.py
 * Requires vitest + @testing-library/react to be installed.
 */

import { describe, it, expect } from "vitest";

import type { Cms } from "../types";

describe("Cms", () => {
  it("has the expected shape", () => {
    const item: Cms = {
      id: 1,
      name: "Test",
      description: "A test item",
      is_active: true,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };
    expect(item.id).toBe(1);
    expect(item.name).toBe("Test");
  });

  it("can be inactive", () => {
    const item: Cms = {
      id: 2,
      name: "Inactive",
      is_active: false,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };
    expect(item.is_active).toBe(false);
  });
});
