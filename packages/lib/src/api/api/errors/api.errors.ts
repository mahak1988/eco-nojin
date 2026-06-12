import type { ApiError } from '../types/auth.types';

export class ApiClientError extends Error {
  public status: number;
  public errorCode?: string;
  public timestamp: string;

  constructor(error: ApiError) {
    super(error.detail);
    this.name = 'ApiClientError';
    this.status = error.status;
    this.errorCode = error.error_code;
    this.timestamp = error.timestamp;

    // Maintains proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiClientError);
    }
  }

  // تبدیل خطا به پیام فارسی
  get PersianMessage(): string {
    const errorMessages: Record<string, string> = {
      'INVALID_CREDENTIALS': 'شناسه یا رمز عبور اشتباه است',
      'ACCOUNT_LOCKED': 'حساب شما قفل شده است. لطفاً بعداً تلاش کنید',
      'TOKEN_EXPIRED': 'نشست شما منقضی شده است. لطفاً دوباره وارد شوید',
      'INVALID_TOKEN': 'توکن نامعتبر است',
      'UNAUTHORIZED': 'شما اجازه دسترسی به این بخش را ندارید',
      'FORBIDDEN': 'دسترسی ممنوع',
      'NOT_FOUND': 'منبع مورد نظر یافت نشد',
      'VALIDATION_ERROR': 'داده‌های ارسالی نامعتبر است',
      'RATE_LIMIT_EXCEEDED': 'تعداد درخواست‌های شما بیش از حد مجاز است',
      'INTERNAL_SERVER_ERROR': 'خطای داخلی سرور. لطفاً بعداً تلاش کنید',
      'SERVICE_UNAVAILABLE': 'سرویس در دسترس نیست. لطفاً بعداً تلاش کنید',
    };

    return errorMessages[this.errorCode || ''] || this.message || 'خطای ناشناخته';
  }
}

export class NetworkError extends Error {
  constructor(message: string = 'خطای شبکه. لطفاً اتصال اینترنت خود را بررسی کنید') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class TimeoutError extends Error {
  constructor(message: string = 'زمان درخواست به پایان رسید. لطفاً دوباره تلاش کنید') {
    super(message);
    this.name = 'TimeoutError';
  }
}