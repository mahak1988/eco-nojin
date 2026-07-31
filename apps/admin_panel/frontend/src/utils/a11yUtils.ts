/**
 * Utilities for accessibility (a11y) features
 */

// Focus trap utility for modal dialogs
export function createFocusTrap(element: HTMLElement) {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  ) as NodeListOf<HTMLElement>;
  
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey && document.activeElement === firstElement) {
      lastElement.focus();
      e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === lastElement) {
      firstElement.focus();
      e.preventDefault();
    }
  };

  element.addEventListener('keydown', handleKeyDown);

  // Focus the first element initially
  firstElement?.focus();

  return () => {
    element.removeEventListener('keydown', handleKeyDown);
  };
}

// Announce to screen readers
export function announce(message: string) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// Ensure high contrast mode detection
export function isHighContrastMode() {
  if (typeof window === 'undefined') return false;
  
  const mediaQuery = '(prefers-contrast: more)';
  return window.matchMedia(mediaQuery).matches;
}

// Set focus to element with scroll prevention
export function focusWithoutScroll(element: HTMLElement) {
  const x = window.scrollX;
  const y = window.scrollY;
  element.focus();
  window.scrollTo(x, y);
}

// Handle keyboard navigation for custom controls
export function handleKeyboardNavigation(
  e: React.KeyboardEvent,
  onEnter?: () => void,
  onSpace?: () => void,
  onArrowKeys?: (direction: 'up' | 'down' | 'left' | 'right') => void
) {
  switch (e.key) {
    case 'Enter':
      onEnter?.();
      break;
    case ' ':
      onSpace?.();
      e.preventDefault(); // Prevent scrolling
      break;
    case 'ArrowUp':
      onArrowKeys?.('up');
      break;
    case 'ArrowDown':
      onArrowKeys?.('down');
      break;
    case 'ArrowLeft':
      onArrowKeys?.('left');
      break;
    case 'ArrowRight':
      onArrowKeys?.('right');
      break;
  }
}