import { z } from 'zod';

export const TafqeetFormattingSchema = z.object({
  sourceElementKey: z.string().nullable().default(null),
  currencyCode: z.enum(['EGP', 'SAR', 'AED', 'USD']).nullable().default(null),
  outputLanguage: z.enum(['ar', 'en', 'both']).default('ar'),
  showCurrency: z.boolean().default(true),
  prefix: z.enum(['none', 'faqat']).default('none'),
  suffix: z.enum(['none', 'la_ghair', 'faqat_la_ghair', 'only']).default('none'),
  previewValue: z.number().nullable().default(null),
});

export type TafqeetFormatting = z.infer<typeof TafqeetFormattingSchema>;
