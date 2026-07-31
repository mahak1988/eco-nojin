import { StrapiService } from '@strapi/strapi';

interface AdvancedFormBuilderService {
  createForm(formData: FormDefinition, tenant: string): Promise<FormDefinition>;
  updateForm(formId: string, formData: FormDefinition, tenant: string): Promise<FormDefinition>;
  submitForm(formId: string, submissionData: any, userId?: string): Promise<FormSubmission>;
  getFormSubmissions(formId: string, tenant: string, filters?: SubmissionFilters): Promise<FormSubmission[]>;
  generateFormEmbedCode(formId: string, options?: EmbedOptions): Promise<string>;
  validateFormData(formId: string, data: any): Promise<FormValidationResult>;
}

interface FormDefinition {
  id: string;
  title: string;
  description: string;
  fields: FormField[];
  settings: FormSettings;
  isActive: boolean;
  tenant: string;
  createdAt: Date;
  updatedAt: Date;
}

interface FormField {
  id: string;
  type: 'text' | 'email' | 'phone' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'date' | 'number' | 'file';
  label: string;
  placeholder?: string;
  required: boolean;
  validations?: FieldValidation[];
  options?: string[]; // برای select، radio، checkbox
  defaultValue?: any;
  order: number;
}

interface FieldValidation {
  type: 'required' | 'email' | 'minLength' | 'maxLength' | 'pattern' | 'custom';
  value?: any;
  message?: string;
}

interface FormSettings {
  redirectUrl?: string;
  submitButtonText: string;
  successMessage: string;
  errorMessage: string;
  emailNotifications: EmailNotification[];
  webhookUrl?: string;
  saveToDatabase: boolean;
  captchaEnabled: boolean;
  analyticsTracking: boolean;
}

interface EmailNotification {
  recipient: string; // email address or 'submitter'
  template: string;
  condition?: string;
}

interface FormSubmission {
  id: string;
  formId: string;
  formData: Record<string, any>;
  userId?: string;
  ipAddress?: string;
  userAgent?: string;
  submittedAt: Date;
  tenant: string;
}

interface SubmissionFilters {
  dateFrom?: Date;
  dateTo?: Date;
  limit?: number;
  offset?: number;
}

interface EmbedOptions {
  width?: string;
  height?: string;
  theme?: 'light' | 'dark';
  hideTitle?: boolean;
}

interface FormValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

interface ValidationError {
  fieldId: string;
  message: string;
}

/**
 * سرویس ابزار فرم پیشرفته
 * امکان ایجاد و مدیریت فرم‌های پیشرفته برای جمع‌آوری اطلاعات مشتریان بالقوه را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any };
}): AdvancedFormBuilderService => ({
  /**
   * ایجاد یک فرم جدید
   */
  async createForm(formData: FormDefinition, tenant: string): Promise<FormDefinition> {
    try {
      // اعتبارسنجی داده‌های فرم
      this.validateFormDataStructure(formData);

      // ایجاد فرم در پایگاه داده
      const newForm = await strapi.query('api::lead-form.lead-form').create({
        data: {
          title: formData.title,
          description: formData.description,
          fields: formData.fields,
          settings: formData.settings,
          isActive: formData.isActive ?? true,
          tenant
        }
      });

      strapi.log.info(`Created form: ${formData.title} for tenant: ${tenant}`);
      return newForm;
    } catch (error) {
      strapi.log.error(`Error creating form: ${error.message}`);
      throw error;
    }
  },

  /**
   * به‌روزرسانی یک فرم
   */
  async updateForm(formId: string, formData: FormDefinition, tenant: string): Promise<FormDefinition> {
    try {
      // بررسی اینکه آیا فرم متعلق به tenant داده شده است یا خیر
      const existingForm = await strapi.query('api::lead-form.lead-form').findOne({
        where: { id: formId, tenant }
      });

      if (!existingForm) {
        throw new Error('Form not found or does not belong to tenant');
      }

      // اعتبارسنجی داده‌های فرم
      this.validateFormDataStructure(formData);

      // به‌روزرسانی فرم
      const updatedForm = await strapi.query('api::lead-form.lead-form').update({
        where: { id: formId },
        data: {
          title: formData.title,
          description: formData.description,
          fields: formData.fields,
          settings: formData.settings,
          isActive: formData.isActive
        }
      });

      strapi.log.info(`Updated form: ${formId} for tenant: ${tenant}`);
      return updatedForm;
    } catch (error) {
      strapi.log.error(`Error updating form: ${error.message}`);
      throw error;
    }
  },

  /**
   * ارسال فرم
   */
  async submitForm(formId: string, submissionData: any, userId?: string): Promise<FormSubmission> {
    try {
      // دریافت تعریف فرم
      const form = await strapi.query('api::lead-form.lead-form').findOne({
        where: { id: formId }
      });

      if (!form) {
        throw new Error(`Form not found: ${formId}`);
      }

      if (!form.isActive) {
        throw new Error(`Form is not active: ${formId}`);
      }

      // اعتبارسنجی داده‌های ارسالی
      const validation = await this.validateFormData(formId, submissionData);
      if (!validation.isValid) {
        const errorMessages = validation.errors.map(e => e.message).join('; ');
        throw new Error(`Form validation failed: ${errorMessages}`);
      }

      // ایجاد سابمیشن
      const submission: FormSubmission = {
        id: `submission_${Date.now()}`,
        formId,
        formData: submissionData,
        userId,
        ipAddress: submissionData._ipAddress, // فرض می‌کنیم IP از کلاینت ارسال شده است
        userAgent: submissionData._userAgent,
        submittedAt: new Date(),
        tenant: form.tenant
      };

      // ذخیره سابمیشن در پایگاه داده
      const savedSubmission = await strapi.query('api::form-submission.form-submission').create({
        data: submission
      });

      // اجرای اقدامات پس از ارسال فرم
      await this.executePostSubmissionActions(form, submission);

      strapi.log.info(`Submitted form: ${formId} by user: ${userId || 'anonymous'}`);
      return savedSubmission;
    } catch (error) {
      strapi.log.error(`Error submitting form: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت سابمیشن‌های فرم
   */
  async getFormSubmissions(formId: string, tenant: string, filters?: SubmissionFilters): Promise<FormSubmission[]> {
    try {
      const whereClause: any = { formId, tenant };

      if (filters?.dateFrom) {
        whereClause.submittedAt = { $gte: filters.dateFrom };
      }

      if (filters?.dateTo) {
        whereClause.submittedAt = whereClause.submittedAt || {};
        whereClause.submittedAt.$lte = filters.dateTo;
      }

      const submissions = await strapi.query('api::form-submission.form-submission').findMany({
        where: whereClause,
        sort: { submittedAt: 'desc' },
        limit: filters?.limit,
        offset: filters?.offset
      });

      strapi.log.debug(`Retrieved ${submissions.length} submissions for form: ${formId}`);
      return submissions;
    } catch (error) {
      strapi.log.error(`Error getting form submissions: ${error.message}`);
      throw error;
    }
  },

  /**
   * تولید کد جاسازی فرم
   */
  async generateFormEmbedCode(formId: string, options?: EmbedOptions): Promise<string> {
    try {
      // تولید کد HTML جاسازی فرم
      const width = options?.width || '100%';
      const height = options?.height || 'auto';
      const theme = options?.theme || 'light';
      const hideTitle = options?.hideTitle || false;

      const embedCode = `
<div id="econojin-form-${formId}" class="econojin-embedded-form" style="width: ${width}; height: ${height};">
  <iframe 
    src="/api/lead-forms/${formId}/embed?theme=${theme}&hideTitle=${hideTitle}"
    width="${width === '100%' ? '100' : parseInt(width)}"
    height="${height === 'auto' ? '600' : parseInt(height)}"
    frameborder="0"
    scrolling="no"
    style="width: 100%; border: none;">
  </iframe>
</div>
<script>
  // ارتفاع داینامیک iframe بر اساس محتوا
  window.addEventListener('message', function(e) {
    if (e.data.type === 'formHeightChanged') {
      document.querySelector('#econojin-form-${formId} iframe').style.height = e.data.height + 'px';
    }
  });
</script>
      `;

      strapi.log.info(`Generated embed code for form: ${formId}`);
      return embedCode;
    } catch (error) {
      strapi.log.error(`Error generating embed code: ${error.message}`);
      throw error;
    }
  },

  /**
   * اعتبارسنجی داده‌های فرم
   */
  async validateFormData(formId: string, data: any): Promise<FormValidationResult> {
    try {
      // دریافت تعریف فرم
      const form = await strapi.query('api::lead-form.lead-form').findOne({
        where: { id: formId }
      });

      if (!form) {
        throw new Error(`Form not found: ${formId}`);
      }

      const errors: ValidationError[] = [];

      // اعتبارسنجی هر فیلد
      for (const field of form.fields) {
        const fieldValue = data[field.id];

        // بررسی الزامی بودن
        if (field.required && (fieldValue === undefined || fieldValue === null || fieldValue === '')) {
          errors.push({
            fieldId: field.id,
            message: `${field.label} الزامی است`
          });
          continue;
        }

        // اگر مقدار وجود داشت، اعتبارسنجی‌های دیگر را انجام بده
        if (fieldValue !== undefined && fieldValue !== null && fieldValue !== '') {
          for (const validation of field.validations || []) {
            switch (validation.type) {
              case 'email':
                if (field.type === 'email' && !this.isValidEmail(fieldValue)) {
                  errors.push({
                    fieldId: field.id,
                    message: 'آدرس ایمیل معتبر نیست'
                  });
                }
                break;

              case 'minLength':
                if (typeof fieldValue === 'string' && fieldValue.length < validation.value) {
                  errors.push({
                    fieldId: field.id,
                    message: `حداقل ${validation.value} کاراکتر مورد نیاز است`
                  });
                }
                break;

              case 'maxLength':
                if (typeof fieldValue === 'string' && fieldValue.length > validation.value) {
                  errors.push({
                    fieldId: field.id,
                    message: `حداکثر ${validation.value} کاراکتر مجاز است`
                  });
                }
                break;

              case 'pattern':
                if (typeof fieldValue === 'string' && !new RegExp(validation.value).test(fieldValue)) {
                  errors.push({
                    fieldId: field.id,
                    message: validation.message || 'فرمت ورودی نامعتبر است'
                  });
                }
                break;

              case 'custom':
                // اعتبارسنجی سفارشی - در این نمونه، فقط یک بررسی ساده انجام می‌دهیم
                if (validation.value === 'noSpecialChars' && /[!@#$%^&*(),.?":{}|<>]/.test(fieldValue)) {
                  errors.push({
                    fieldId: field.id,
                    message: 'استفاده از کاراکترهای خاص مجاز نیست'
                  });
                }
                break;
            }
          }
        }
      }

      const result: FormValidationResult = {
        isValid: errors.length === 0,
        errors
      };

      return result;
    } catch (error) {
      strapi.log.error(`Error validating form data: ${error.message}`);
      throw error;
    }
  },

  /**
   * اعتبارسنجی ساختار داده فرم
   */
  validateFormDataStructure(formData: FormDefinition): void {
    if (!formData.title) {
      throw new Error('Form title is required');
    }

    if (!Array.isArray(formData.fields) || formData.fields.length === 0) {
      throw new Error('Form must have at least one field');
    }

    // بررسی تکراری نبودن آیدی فیلدها
    const fieldIds = formData.fields.map(f => f.id);
    const uniqueFieldIds = new Set(fieldIds);
    if (fieldIds.length !== uniqueFieldIds.size) {
      throw new Error('Field IDs must be unique');
    }
  },

  /**
   * اجرای اقدامات پس از ارسال فرم
   */
  async executePostSubmissionActions(form: any, submission: FormSubmission): Promise<void> {
    try {
      // ۱. ارسال اعلان‌های ایمیل
      if (form.settings.emailNotifications && form.settings.emailNotifications.length > 0) {
        await this.sendEmailNotifications(form, submission);
      }

      // ۲. ارسال داده به URL وب هوک
      if (form.settings.webhookUrl) {
        await this.sendToWebhook(form.settings.webhookUrl, submission);
      }

      // ۳. ذخیره در پایگاه داده (قبلاً انجام شده)

      // ۴. ردیابی تحلیلی
      if (form.settings.analyticsTracking) {
        await this.trackAnalytics(submission);
      }

      strapi.log.info(`Executed post-submission actions for form: ${form.id}`);
    } catch (error) {
      strapi.log.error(`Error in post-submission actions: ${error.message}`);
    }
  },

  /**
   * ارسال اعلان‌های ایمیل
   */
  async sendEmailNotifications(form: any, submission: FormSubmission): Promise<void> {
    // در محیط واقعی، از یک سرویس ایمیل مانند Strapi Email Plugin استفاده می‌شود
    strapi.log.info(`Would send email notifications for form: ${form.id}`);
  },

  /**
   * ارسال به وب هوک
   */
  async sendToWebhook(webhookUrl: string, submission: FormSubmission): Promise<void> {
    // در محیط واقعی، درخواست HTTP به URL وب هوک ارسال می‌شود
    strapi.log.info(`Would send submission to webhook: ${webhookUrl}`);
  },

  /**
   * ردیابی تحلیلی
   */
  async trackAnalytics(submission: FormSubmission): Promise<void> {
    // ردیابی رویداد ارسال فرم برای تحلیل‌های بعدی
    const analyticsService = strapi.service('analytics-service');
    if (analyticsService) {
      await analyticsService.trackEngagement(
        submission.formId,
        'form_submission',
        'lead-generation',
        submission.userId
      );
    }
  },

  /**
   * بررسی ایمیل معتبر
   */
  isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
});