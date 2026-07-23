// src/lib/src/security/security.ts

export const sanitizeHtml = (input: string): string => {
  return input
    .replace(/&/g, '&')
    .replace(/</g, '<')
    .replace(/>/g, '>')
    .replace(/"/g, '"')
    .replace(/'/g, '&#039;');
};

export const escapeCsp = (input: string): string => {
  return input.replace(/[<>"'&]/g, (char) => {
    const escapeMap: Record<string, string> = {
      '<': '\\u003C',
      '>': '\\u003E',
      "'": '\\u0027',
      '"': '\\u0022',
      '&': '\\u0026',
    };
    return escapeMap[char];
  });
};

export const getCspHeader = (): string => {
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "img-src 'self' data: https:",
    "font-src 'self' data: https://fonts.gstatic.com",
    "connect-src 'self' http://localhost:* ws://localhost:*",
  ].join('; ');
  return csp;
};

export const validateOrigin = (allowedOrigins: string[]): (origin: string) => boolean => {
  return (origin: string): boolean => {
    if (!origin) return false;
    return allowedOrigins.some((allowed) => origin === allowed || origin.startsWith(`${allowed}`));
  };
};

export const generateCsrfToken = (): string => {
  const array = new Uint8Array(32);
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    crypto.getRandomValues(array);
  } else {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256);
    }
  }
  return Array.from(array, (byte) => byte.toString(16).padStart(2, '0')).join('');
};