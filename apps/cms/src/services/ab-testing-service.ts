import { StrapiService } from '@strapi/strapi';

interface ABTestingService {
  createTest(testData: ABTestInput): Promise<ABTest>;
  assignVariant(userId: string, testId: string): Promise<ABTestVariant>;
  recordConversion(testId: string, variantId: string, userId?: string): Promise<void>;
  getTestResults(testId: string): Promise<TestResults>;
  endTest(testId: string): Promise<FinalTestResults>;
  getActiveTests(tenant: string): Promise<ABTest[]>;
}

interface ABTestInput {
  name: string;
  description: string;
  trafficAllocation: number; // Percentage of traffic to include in test (0-100)
  variants: ABTestVariantInput[];
  startDate: Date;
  endDate: Date;
  tenant: string;
  goal: string; // Conversion goal (e.g., 'click', 'purchase', 'sign_up')
}

interface ABTestVariantInput {
  name: string;
  content: any; // Content for this variant
  weight: number; // Traffic percentage for this variant
}

interface ABTest {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'running' | 'completed' | 'paused';
  trafficAllocation: number;
  variants: ABTestVariant[];
  startDate: Date;
  endDate: Date;
  tenant: string;
  goal: string;
  createdAt: Date;
  updatedAt: Date;
}

interface ABTestVariant {
  id: string;
  testId: string;
  name: string;
  content: any;
  weight: number;
  impressions: number;
  conversions: number;
  createdAt: Date;
}

interface TestResults {
  testName: string;
  testId: string;
  variants: VariantResult[];
  winner?: string;
  confidence: number;
  isComplete: boolean;
}

interface VariantResult {
  variantId: string;
  variantName: string;
  impressions: number;
  conversions: number;
  conversionRate: number;
  relativeImprovement?: number;
  isWinner: boolean;
}

interface FinalTestResults {
  testId: string;
  winner: string;
  winningVariant: ABTestVariant;
  results: TestResults;
}

/**
 * سرویس تست A/B
 * امکان اجرای تست A/B برای محتوای بازاریابی را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): ABTestingService => ({
  /**
   * ایجاد یک تست A/B جدید
   */
  async createTest(testData: ABTestInput): Promise<ABTest> {
    try {
      // اعتبارسنجی داده‌های ورودی
      if (!testData.variants || testData.variants.length < 2) {
        throw new Error('A/B test must have at least 2 variants');
      }

      // بررسی مجموع وزن‌ها
      const totalWeight = testData.variants.reduce((sum, variant) => sum + variant.weight, 0);
      if (Math.abs(totalWeight - 100) > 0.01) {
        throw new Error(`Variant weights must sum to 100%, got ${totalWeight}%`);
      }

      // ایجاد تست
      const test = await strapi.query('api::ab-test.ab-test').create({
        data: {
          name: testData.name,
          description: testData.description,
          trafficAllocation: testData.trafficAllocation,
          startDate: testData.startDate,
          endDate: testData.endDate,
          tenant: testData.tenant,
          goal: testData.goal,
          status: 'draft',
          variants: []
        }
      });

      // ایجاد متغیرهای تست
      const createdVariants = [];
      for (const variantData of testData.variants) {
        const variant = await strapi.query('api::ab-test-variant.ab-test-variant').create({
          data: {
            test: test.id,
            name: variantData.name,
            content: variantData.content,
            weight: variantData.weight,
            impressions: 0,
            conversions: 0
          }
        });
        createdVariants.push(variant);
      }

      // به‌روزرسانی تست با لیست متغیرها
      const updatedTest = await strapi.query('api::ab-test.ab-test').update({
        where: { id: test.id },
        data: { 
          status: 'running',
          variants: createdVariants.map(v => v.id)
        }
      });

      strapi.log.info(`Created A/B test: ${testData.name} with ${testData.variants.length} variants`);
      return updatedTest;
    } catch (error) {
      strapi.log.error(`Error creating A/B test: ${error.message}`);
      throw error;
    }
  },

  /**
   * اختصاص یک متغیر به کاربر
   */
  async assignVariant(userId: string, testId: string): Promise<ABTestVariant> {
    try {
      // دریافت تست و متغیرهای آن
      const test = await strapi.query('api::ab-test.ab-test').findOne({
        where: { id: testId },
        populate: ['variants']
      });

      if (!test) {
        throw new Error(`A/B test not found: ${testId}`);
      }

      if (test.status !== 'running') {
        throw new Error(`A/B test is not running: ${testId}`);
      }

      // بررسی اینکه آیا کاربر قبلاً متغیری دریافت کرده است یا خیر
      const existingAssignment = await strapi.query('api::ab-test-user-assignment.ab-test-user-assignment').findOne({
        where: { 
          testId,
          userId 
        }
      });

      if (existingAssignment) {
        // بازگرداندن متغیر قبلی
        const assignedVariant = await strapi.query('api::ab-test-variant.ab-test-variant').findOne({
          where: { id: existingAssignment.variantId }
        });
        return assignedVariant;
      }

      // انتخاب تصادفی یک متغیر بر اساس وزن
      const randomValue = Math.random() * 100;
      let cumulativeWeight = 0;
      let selectedVariant: any = null;

      for (const variant of test.variants) {
        cumulativeWeight += variant.weight;
        if (randomValue <= cumulativeWeight) {
          selectedVariant = variant;
          break;
        }
      }

      // اطمینان از انتخاب یک متغیر
      if (!selectedVariant) {
        selectedVariant = test.variants[test.variants.length - 1];
      }

      // ثبت اختصاص کاربر به متغیر
      await strapi.query('api::ab-test-user-assignment.ab-test-user-assignment').create({
        data: {
          testId,
          userId,
          variantId: selectedVariant.id,
          assignedAt: new Date().toISOString()
        }
      });

      // افزایش شمارنده نمایش
      await strapi.query('api::ab-test-variant.ab-test-variant').update({
        where: { id: selectedVariant.id },
        data: { impressions: selectedVariant.impressions + 1 }
      });

      strapi.log.debug(`Assigned user ${userId} to variant ${selectedVariant.name} in test ${test.name}`);
      return selectedVariant;
    } catch (error) {
      strapi.log.error(`Error assigning variant: ${error.message}`);
      throw error;
    }
  },

  /**
   * ثبت تبدیل (conversion)
   */
  async recordConversion(testId: string, variantId: string, userId?: string): Promise<void> {
    try {
      // بررسی وجود متغیر و تست
      const test = await strapi.query('api::ab-test.ab-test').findOne({
        where: { id: testId }
      });

      if (!test) {
        throw new Error(`A/B test not found: ${testId}`);
      }

      const variant = await strapi.query('api::ab-test-variant.ab-test-variant').findOne({
        where: { id: variantId, test: testId }
      });

      if (!variant) {
        throw new Error(`Variant not found in test: ${variantId}`);
      }

      // افزایش شمارنده تبدیل
      await strapi.query('api::ab-test-variant.ab-test-variant').update({
        where: { id: variantId },
        data: { conversions: variant.conversions + 1 }
      });

      // ثبت رویداد تبدیل
      await strapi.query('api::ab-test-conversion.ab-test-conversion').create({
        data: {
          testId,
          variantId,
          userId,
          convertedAt: new Date().toISOString()
        }
      });

      strapi.log.info(`Recorded conversion for test ${testId}, variant ${variantId}${userId ? `, user ${userId}` : ''}`);
    } catch (error) {
      strapi.log.error(`Error recording conversion: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت نتایج تست
   */
  async getTestResults(testId: string): Promise<TestResults> {
    try {
      const test = await strapi.query('api::ab-test.ab-test').findOne({
        where: { id: testId },
        populate: ['variants']
      });

      if (!test) {
        throw new Error(`A/B test not found: ${testId}`);
      }

      // محاسبه نتایج برای هر متغیر
      const variantResults: VariantResult[] = [];
      let bestConversionRate = 0;
      let winningVariantId = '';

      for (const variant of test.variants) {
        const conversionRate = variant.impressions > 0 ? (variant.conversions / variant.impressions) * 100 : 0;
        
        const result: VariantResult = {
          variantId: variant.id,
          variantName: variant.name,
          impressions: variant.impressions,
          conversions: variant.conversions,
          conversionRate,
          isWinner: false
        };

        if (conversionRate > bestConversionRate) {
          bestConversionRate = conversionRate;
          winningVariantId = variant.id;
        }

        variantResults.push(result);
      }

      // تعیین برنده و به‌روزرسانی نتایج
      const finalResults = variantResults.map(result => {
        const baselineRate = variantResults[0].conversionRate;
        if (baselineRate > 0) {
          result.relativeImprovement = ((result.conversionRate - baselineRate) / baselineRate) * 100;
        }
        
        if (result.variantId === winningVariantId) {
          result.isWinner = true;
        }
        
        return result;
      });

      // محاسبه اطمینان (ساده‌شده)
      const confidence = this.calculateConfidence(finalResults);

      const results: TestResults = {
        testName: test.name,
        testId,
        variants: finalResults,
        winner: winningVariantId,
        confidence,
        isComplete: new Date() > new Date(test.endDate)
      };

      return results;
    } catch (error) {
      strapi.log.error(`Error getting test results: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه اطمینان (ساده‌شده)
   */
  calculateConfidence(results: VariantResult[]): number {
    // در این پیاده‌سازی ساده، اطمینان را بر اساس تفاوت نرخ تبدیل محاسبه می‌کنیم
    if (results.length < 2) return 0;

    const baselineRate = results[0].conversionRate;
    const winnerRate = results.find(r => r.isWinner)?.conversionRate || 0;

    if (baselineRate === 0) return winnerRate > 0 ? 95 : 50;

    const improvement = ((winnerRate - baselineRate) / baselineRate) * 100;
    
    // هر چقدر بهبود بیشتر باشد، اطمینان بیشتر است (تا 95%)
    return Math.min(95, 50 + (improvement * 2));
  },

  /**
   * پایان تست و تعیین برنده نهایی
   */
  async endTest(testId: string): Promise<FinalTestResults> {
    try {
      const test = await strapi.query('api::ab-test.ab-test').findOne({
        where: { id: testId },
        populate: ['variants']
      });

      if (!test) {
        throw new Error(`A/B test not found: ${testId}`);
      }

      // دریافت نتایج نهایی
      const results = await this.getTestResults(testId);

      // تعیین برنده نهایی
      const winningVariant = test.variants.find((v: any) => v.id === results.winner);

      if (!winningVariant) {
        throw new Error('Could not determine winning variant');
      }

      // به‌روزرسانی وضعیت تست
      await strapi.query('api::ab-test.ab-test').update({
        where: { id: testId },
        data: { status: 'completed' }
      });

      const finalResults: FinalTestResults = {
        testId,
        winner: results.winner!,
        winningVariant,
        results
      };

      strapi.log.info(`Ended A/B test ${testId}, winner: ${winningVariant.name}`);
      return finalResults;
    } catch (error) {
      strapi.log.error(`Error ending test: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت تست‌های فعال
   */
  async getActiveTests(tenant: string): Promise<ABTest[]> {
    try {
      const now = new Date().toISOString();
      const tests = await strapi.query('api::ab-test.ab-test').findMany({
        where: {
          tenant,
          status: 'running',
          startDate: { $lte: now },
          endDate: { $gte: now }
        },
        populate: ['variants']
      });

      return tests;
    } catch (error) {
      strapi.log.error(`Error getting active tests: ${error.message}`);
      throw error;
    }
  }
});