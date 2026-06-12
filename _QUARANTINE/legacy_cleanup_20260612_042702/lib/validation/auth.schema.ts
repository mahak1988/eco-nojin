import { z } from 'zod';

export const loginSchema = z.object({
  fid: z.string()
    .min(3, 'شناسه کشاورز باید حداقل ۳ کاراکتر باشد')
    .regex(/^F\d{3,}$/, 'فرمت شناسه نامعتبر است (مثال: F001)'),
  phone: z.string()
    .regex(/^\+98\d{10}$/, 'شماره تلفن نامعتبر است'),
});

export type LoginInput = z.infer<typeof loginSchema>;