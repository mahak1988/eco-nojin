import { StrapiService } from '@strapi/strapi';

interface InteractiveContentService {
  createQuiz(quizData: QuizData, tenant: string): Promise<Quiz>;
  createCalculator(calcData: CalculatorData, tenant: string): Promise<Calculator>;
  submitQuizResponse(quizId: string, userId: string, answers: Answer[]): Promise<QuizResult>;
  calculateResult(calcId: string, inputs: CalculationInput[]): Promise<CalculationResult>;
  getPopularInteractiveContent(tenant: string, type: 'quiz' | 'calculator', limit?: number): Promise<any[]>;
  trackUserInteraction(contentId: string, contentType: 'quiz' | 'calculator', userId: string, interaction: InteractionData): Promise<void>;
}

interface QuizData {
  title: string;
  description: string;
  questions: Question[];
  settings: QuizSettings;
}

interface CalculatorData {
  title: string;
  description: string;
  inputs: CalcInput[];
  formula: string;
  settings: CalcSettings;
}

interface Question {
  id: string;
  text: string;
  type: 'multiple-choice' | 'true-false' | 'open-ended';
  options?: string[];
  correctAnswer?: string;
  points?: number;
}

interface Answer {
  questionId: string;
  answer: string;
  timeTaken?: number;
}

interface Quiz {
  id: string;
  title: string;
  description: string;
  questions: Question[];
  settings: QuizSettings;
  tenant: string;
  createdAt: Date;
  updatedAt: Date;
}

interface QuizSettings {
  timeLimit?: number; // in minutes
  randomized: boolean;
  allowReview: boolean;
  showResultsImmediately: boolean;
  passPercentage: number;
}

interface QuizResult {
  quizId: string;
  userId: string;
  score: number;
  maxScore: number;
  percentage: number;
  passed: boolean;
  answers: Answer[];
  completionTime: number; // in seconds
  submittedAt: Date;
}

interface CalcInput {
  id: string;
  label: string;
  type: 'number' | 'text' | 'select';
  defaultValue?: any;
  options?: string[];
  required: boolean;
}

interface CalculationInput {
  inputId: string;
  value: any;
}

interface Calculator {
  id: string;
  title: string;
  description: string;
  inputs: CalcInput[];
  formula: string;
  settings: CalcSettings;
  tenant: string;
  createdAt: Date;
  updatedAt: Date;
}

interface CalcSettings {
  showFormula: boolean;
  allowSaveResults: boolean;
  requireLogin: boolean;
}

interface CalculationResult {
  calculatorId: string;
  inputs: CalculationInput[];
  result: any;
  calculationTime: number;
  calculatedAt: Date;
}

interface InteractionData {
  action: 'view' | 'start' | 'complete' | 'calculate' | 'save';
  metadata?: any;
}

/**
 * سرویس محتوای تعاملی
 * امکان ایجاد و مدیریت محتوای تعاملی مانند آزمون‌ها و ماشین‌حساب‌ها را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): InteractiveContentService => ({
  /**
   * ایجاد یک آزمون جدید
   */
  async createQuiz(quizData: QuizData, tenant: string): Promise<Quiz> {
    try {
      // اعتبارسنجی داده‌های آزمون
      this.validateQuizData(quizData);

      // ایجاد آزمون در پایگاه داده
      const newQuiz = await strapi.query('api::interactive-quiz.interactive-quiz').create({
        data: {
          title: quizData.title,
          description: quizData.description,
          questions: quizData.questions,
          settings: quizData.settings,
          tenant
        }
      });

      strapi.log.info(`Created quiz: ${quizData.title} for tenant: ${tenant}`);
      return newQuiz;
    } catch (error) {
      strapi.log.error(`Error creating quiz: ${error.message}`);
      throw error;
    }
  },

  /**
   * ایجاد یک ماشین‌حساب جدید
   */
  async createCalculator(calcData: CalculatorData, tenant: string): Promise<Calculator> {
    try {
      // اعتبارسنجی داده‌های ماشین‌حساب
      this.validateCalculatorData(calcData);

      // ایجاد ماشین‌حساب در پایگاه داده
      const newCalculator = await strapi.query('api::interactive-calculator.interactive-calculator').create({
        data: {
          title: calcData.title,
          description: calcData.description,
          inputs: calcData.inputs,
          formula: calcData.formula,
          settings: calcData.settings,
          tenant
        }
      });

      strapi.log.info(`Created calculator: ${calcData.title} for tenant: ${tenant}`);
      return newCalculator;
    } catch (error) {
      strapi.log.error(`Error creating calculator: ${error.message}`);
      throw error;
    }
  },

  /**
   * ارسال پاسخ آزمون
   */
  async submitQuizResponse(quizId: string, userId: string, answers: Answer[]): Promise<QuizResult> {
    try {
      // دریافت اطلاعات آزمون
      const quiz = await strapi.query('api::interactive-quiz.interactive-quiz').findOne({
        where: { id: quizId }
      });

      if (!quiz) {
        throw new Error(`Quiz not found: ${quizId}`);
      }

      // محاسبه نمره
      let score = 0;
      let maxScore = 0;

      for (const answer of answers) {
        const question = quiz.questions.find(q => q.id === answer.questionId);
        if (question) {
          maxScore += question.points || 1;
          
          if (question.correctAnswer && answer.answer === question.correctAnswer) {
            score += question.points || 1;
          }
        }
      }

      const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0;
      const passed = percentage >= quiz.settings.passPercentage;

      // زمان تقریبی تکمیل (در این نمونه فرض می‌کنیم)
      const completionTime = answers.reduce((sum, ans) => sum + (ans.timeTaken || 30), 0);

      // ایجاد نتیجه آزمون
      const result: QuizResult = {
        quizId,
        userId,
        score,
        maxScore,
        percentage,
        passed,
        answers,
        completionTime,
        submittedAt: new Date()
      };

      // ذخیره نتیجه در پایگاه داده
      await strapi.query('api::quiz-result.quiz-result').create({
        data: result
      });

      // ردیابی تعامل کاربر
      await this.trackUserInteraction(quizId, 'quiz', userId, {
        action: 'complete',
        metadata: { score, percentage, passed }
      });

      strapi.log.info(`User ${userId} completed quiz ${quizId} with score: ${percentage}%`);
      return result;
    } catch (error) {
      strapi.log.error(`Error submitting quiz response: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه نتیجه ماشین‌حساب
   */
  async calculateResult(calcId: string, inputs: CalculationInput[]): Promise<CalculationResult> {
    try {
      // دریافت اطلاعات ماشین‌حساب
      const calculator = await strapi.query('api::interactive-calculator.interactive-calculator').findOne({
        where: { id: calcId }
      });

      if (!calculator) {
        throw new Error(`Calculator not found: ${calcId}`);
      }

      // اعتبارسنجی ورودی‌ها
      this.validateCalculationInputs(calculator.inputs, inputs);

      // اجرای فرمول (در این نمونه ساده‌شده)
      const result = this.executeCalculationFormula(calculator.formula, inputs);

      const calculationResult: CalculationResult = {
        calculatorId: calcId,
        inputs,
        result,
        calculationTime: Date.now(), // زمان اجرای محاسبه
        calculatedAt: new Date()
      };

      // ذخیره نتیجه در صورت تنظیمات
      if (calculator.settings.allowSaveResults) {
        await strapi.query('api::calculation-result.calculation-result').create({
          data: calculationResult
        });
      }

      strapi.log.info(`Calculated result for calculator: ${calcId}`);
      return calculationResult;
    } catch (error) {
      strapi.log.error(`Error in calculation: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت محتوای تعاملی محبوب
   */
  async getPopularInteractiveContent(tenant: string, type: 'quiz' | 'calculator', limit: number = 10): Promise<any[]> {
    try {
      let popularContent = [];

      if (type === 'quiz') {
        // دریافت آزمون‌های محبوب بر اساس تعداد انجام داده شده
        const quizResults = await strapi.query('api::quiz-result.quiz-result').findMany({
          where: { tenant },
          groupBy: ['quizId'],
          aggregate: {
            count: { field: 'id' }
          }
        });

        // دریافت جزئیات آزمون‌های برتر
        const topQuizIds = quizResults
          .sort((a, b) => (b.count__id || 0) - (a.count__id || 0))
          .slice(0, limit)
          .map(result => result.quizId);

        popularContent = await strapi.query('api::interactive-quiz.interactive-quiz').findMany({
          where: { id: { $in: topQuizIds } }
        });
      } else if (type === 'calculator') {
        // دریافت ماشین‌حساب‌های محبوب بر اساس تعداد محاسبات انجام شده
        const calcResults = await strapi.query('api::calculation-result.calculation-result').findMany({
          where: { tenant },
          groupBy: ['calculatorId'],
          aggregate: {
            count: { field: 'id' }
          }
        });

        // دریافت جزئیات ماشین‌حساب‌های برتر
        const topCalcIds = calcResults
          .sort((a, b) => (b.count__id || 0) - (a.count__id || 0))
          .slice(0, limit)
          .map(result => result.calculatorId);

        popularContent = await strapi.query('api::interactive-calculator.interactive-calculator').findMany({
          where: { id: { $in: topCalcIds } }
        });
      }

      strapi.log.debug(`Retrieved ${popularContent.length} popular ${type} for tenant: ${tenant}`);
      return popularContent;
    } catch (error) {
      strapi.log.error(`Error getting popular interactive content: ${error.message}`);
      return [];
    }
  },

  /**
   * ردیابی تعامل کاربر
   */
  async trackUserInteraction(contentId: string, contentType: 'quiz' | 'calculator', userId: string, interaction: InteractionData): Promise<void> {
    try {
      await strapi.query('api::user-interaction.user-interaction').create({
        data: {
          contentId,
          contentType,
          userId,
          action: interaction.action,
          metadata: interaction.metadata,
          timestamp: new Date().toISOString()
        }
      });

      strapi.log.debug(`Tracked user interaction: ${userId} ${interaction.action} ${contentType} ${contentId}`);
    } catch (error) {
      strapi.log.error(`Error tracking user interaction: ${error.message}`);
    }
  },

  /**
   * اعتبارسنجی داده‌های آزمون
   */
  validateQuizData(quizData: QuizData): void {
    if (!quizData.title) {
      throw new Error('Quiz title is required');
    }

    if (!Array.isArray(quizData.questions) || quizData.questions.length === 0) {
      throw new Error('Quiz must have at least one question');
    }

    for (const question of quizData.questions) {
      if (!question.id || !question.text) {
        throw new Error('Each question must have an id and text');
      }

      if (question.type === 'multiple-choice' && (!Array.isArray(question.options) || question.options.length === 0)) {
        throw new Error('Multiple choice questions must have options');
      }

      if (question.type === 'true-false' && (!Array.isArray(question.options) || question.options.length !== 2)) {
        throw new Error('True/false questions must have exactly 2 options');
      }
    }
  },

  /**
   * اعتبارسنجی داده‌های ماشین‌حساب
   */
  validateCalculatorData(calcData: CalculatorData): void {
    if (!calcData.title) {
      throw new Error('Calculator title is required');
    }

    if (!Array.isArray(calcData.inputs) || calcData.inputs.length === 0) {
      throw new Error('Calculator must have at least one input');
    }

    if (!calcData.formula) {
      throw new Error('Calculator must have a formula');
    }

    for (const input of calcData.inputs) {
      if (!input.id || !input.label) {
        throw new Error('Each input must have an id and label');
      }
    }
  },

  /**
   * اعتبارسنجی ورودی‌های محاسبه
   */
  validateCalculationInputs(expectedInputs: CalcInput[], providedInputs: CalculationInput[]): void {
    for (const expected of expectedInputs) {
      const provided = providedInputs.find(inp => inp.inputId === expected.id);
      
      if (!provided && expected.required) {
        throw new Error(`Required input missing: ${expected.label}`);
      }

      if (provided) {
        // اعتبارسنجی نوع داده
        if (expected.type === 'number' && isNaN(Number(provided.value))) {
          throw new Error(`Input ${expected.label} must be a number`);
        }
      }
    }
  },

  /**
   * اجرای فرمول محاسبه (ساده‌شده)
   */
  executeCalculationFormula(formula: string, inputs: CalculationInput[]): any {
    try {
      // در محیط واقعی، از یک موتور فرمول امن مانند math.js استفاده می‌شود
      // برای نمونه، فقط چند فرمول ساده پشتیبانی می‌کنیم
      
      // تبدیل ورودی‌ها به متغیرهای قابل استفاده در فرمول
      const inputValues: Record<string, any> = {};
      for (const input of inputs) {
        inputValues[input.inputId] = Number(input.value) || input.value;
      }

      // بررسی چند نمونه فرمول ساده
      if (formula.includes('BMI')) {
        // فرمول BMI: weight / (height/100)^2
        const weight = inputValues['weight'] || 0;
        const height = inputValues['height'] || 1;
        return weight / Math.pow(height / 100, 2);
      } else if (formula.includes('simple_interest')) {
        // فرمول سود ساده: (principal * rate * time) / 100
        const principal = inputValues['principal'] || 0;
        const rate = inputValues['rate'] || 0;
        const time = inputValues['time'] || 0;
        return (principal * rate * time) / 100;
      } else {
        // در محیط واقعی، فرمول واقعی اجرا می‌شود
        return `Calculated result for formula: ${formula}`;
      }
    } catch (error) {
      strapi.log.error(`Error executing calculation formula: ${error.message}`);
      return null;
    }
  }
});