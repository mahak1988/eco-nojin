import { z } from 'zod';

// ============================================================================
// Login Schema
// ============================================================================

export const loginSchema = z.object({
  fid: z
    .string()
    .min(1, 'شناسه کشاورز الزامی است')
    .min(3, 'شناسه کشاورز باید حداقل ۳ کاراکتر باشد')
    .regex(/^F\d{3,}$/, 'فرمت شناسه نامعتبر است (مثال: F001)'),
  
  phone: z
    .string()
    .min(1, 'شماره تلفن الزامی است')
    .regex(/^\+98\d{10}$/, 'شماره تلفن نامعتبر است (مثال: +989123456789)'),
});

export type LoginInput = z.infer<typeof loginSchema>;

// ============================================================================
// Register Schema
// ============================================================================

export const registerSchema = z.object({
  name: z
    .string()
    .min(1, 'نام الزامی است')
    .min(2, 'نام باید حداقل ۲ کاراکتر باشد')
    .max(50, 'نام نباید بیشتر از ۵۰ کاراکتر باشد'),
  
  fid: z
    .string()
    .min(1, 'شناسه کشاورز الزامی است')
    .regex(/^F\d{3,}$/, 'فرمت شناسه نامعتبر است'),
  
  phone: z
    .string()
    .min(1, 'شماره تلفن الزامی است')
    .regex(/^\+98\d{10}$/, 'شماره تلفن نامعتبر است'),
  
  email: z
    .string()
    .email('ایمیل نامعتبر است')
    .optional()
    .or(z.literal('')),
  
  password: z
    .string()
    .min(1, 'رمز عبور الزامی است')
    .min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'رمز عبور باید شامل حروف بزرگ، کوچک و عدد باشد'
    ),
  
  confirmPassword: z.string().min(1, 'تأیید رمز عبور الزامی است'),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'رمز عبور و تأیید آن مطابقت ندارند',
  path: ['confirmPassword'],
});

export type RegisterInput = z.infer<typeof registerSchema>;

// ============================================================================
// Forgot Password Schema
// ============================================================================

export const forgotPasswordSchema = z.object({
  phone: z
    .string()
    .min(1, 'شماره تلفن الزامی است')
    .regex(/^\+98\d{10}$/, 'شماره تلفن نامعتبر است'),
});

export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;

// ============================================================================
// Reset Password Schema
// ============================================================================

export const resetPasswordSchema = z.object({
  token: z.string().min(1, 'توکن الزامی است'),
  
  newPassword: z
    .string()
    .min(1, 'رمز عبور جدید الزامی است')
    .min(8, 'رمز عبور باید حداقل ۸ کاراکتر باشد')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'رمز عبور باید شامل حروف بزرگ، کوچک و عدد باشد'
    ),
  
  confirmPassword: z.string().min(1, 'تأیید رمز عبور الزامی است'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: 'رمز عبور و تأیید آن مطابقت ندارند',
  path: ['confirmPassword'],
});

export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;