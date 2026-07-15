/**
 * ============================================================================
 *  useCommandPalette — manage Command Palette open/close + Ctrl+K shortcut
 * ============================================================================
 */

import { useCallback, useEffect, useState } from "react";

export function useCommandPalette(): {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
} {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    function handleKey(event: KeyboardEvent): void {
      if ((event.ctrlKey || event.metaKey) && event.key === "k") {
        event.preventDefault();
        setIsOpen((v) => !v);
      }
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, []);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);

  return { isOpen, open, close, toggle };
}
