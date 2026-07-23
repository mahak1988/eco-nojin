import { sanitizeHtml, escapeCsp, validateOrigin, generateCsrfToken } from '@econojin/lib';

describe('Security Utils', () => {
  test('sanitizeHtml escapes dangerous characters', () => {
    expect(sanitizeHtml('<script>alert("xss")</script>')).toBe(
      '<script>alert("xss")</script>'
    );
    expect(sanitizeHtml("It's a test")).toBe('It&#039;s a test');
  });

  test('escapeCsp escapes for CSP nonce', () => {
    const escaped = escapeCsp('<script>alert(1)</script>');
    expect(escaped).toContain('\\u003C');
    expect(escaped).toContain('\\u003E');
  });

  test('validateOrigin blocks unknown origins', () => {
    const validate = validateOrigin(['https://econojin.com', 'https://app.econojin.com']);
    expect(validate('https://econojin.com')).toBe(true);
    expect(validate('https://malicious.com')).toBe(false);
    expect(validate('')).toBe(false);
  });

  test('generateCsrfToken returns 64 hex chars', () => {
    const token = generateCsrfToken();
    expect(token).toHaveLength(64);
    expect(/^[0-9a-f]+$/).test(token);
  });
});