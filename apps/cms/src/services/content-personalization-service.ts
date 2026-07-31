import { StrapiService } from '@strapi/strapi';

interface ContentPersonalizationService {
  personalizeContent(contentId: string, contentType: string, userId: string, context: PersonalizationContext): Promise<any>;
  createUserProfile(userId: string, initialData?: any): Promise<UserProfile>;
  updateUserProfile(userId: string, data: any): Promise<UserProfile>;
  getPersonalizedRecommendations(userId: string, limit?: number): Promise<any[]>;
  trackUserEngagement(userId: string, contentId: string, contentType: string, engagement: EngagementData): Promise<void>;
  createAudienceSegment(segmentData: AudienceSegment): Promise<AudienceSegment>;
  getAudienceSegments(tenant: string): Promise<AudienceSegment[]>;
}

interface PersonalizationContext {
  userId?: string;
  deviceId?: string;
  location?: string;
  deviceType?: 'desktop' | 'mobile' | 'tablet';
  timeOfDay?: number; // 0-23
  referrer?: string;
  interests?: string[];
  pastBehavior?: any[];
}

interface UserProfile {
  id: string;
  userId: string;
  interests: string[];
  preferences: Record<string, any>;
  behaviorPatterns: BehaviorPattern[];
  lastInteraction: Date;
  engagementScore: number;
  segments: string[];
  createdAt: Date;
  updatedAt: Date;
}

interface BehaviorPattern {
  category: string;
  weight: number;
  lastSeen: Date;
}

interface EngagementData {
  viewDuration?: number;
  scrollDepth?: number;
  clicks?: number;
  shares?: number;
  comments?: number;
  rating?: number;
  completed?: boolean;
}

interface AudienceSegment {
  id: string;
  name: string;
  description: string;
  criteria: SegmentCriteria;
  memberCount: number;
  createdAt: Date;
  tenant: string;
}

interface SegmentCriteria {
  interests?: string[];
  demographics?: Record<string, any>;
  behavior?: Record<string, any>;
  engagementLevel?: 'low' | 'medium' | 'high';
}

/**
 * سرویس شخصی‌سازی محتوا
 * امکان شخصی‌سازی محتوا بر اساس نیازها و رفتار کاربران را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; entityService: any };
}): ContentPersonalizationService => ({
  /**
   * شخصی‌سازی یک محتوا برای کاربر
   */
  async personalizeContent(contentId: string, contentType: string, userId: string, context: PersonalizationContext): Promise<any> {
    try {
      // دریافت محتوای اصلی
      const content = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
      if (!content) {
        throw new Error(`Content not found: ${contentId}`);
      }

      // دریافت پروفایل کاربر
      let userProfile = await this.getUserProfile(userId);
      if (!userProfile) {
        userProfile = await this.createUserProfile(userId, { 
          initialInterests: context.interests || [] 
        });
      }

      // تعیین شخصی‌سازی‌های لازم بر اساس پروفایل کاربر و زمینه
      const personalizedContent = { ...content };

      // شخصی‌سازی بر اساس علایق
      if (userProfile.interests && userProfile.interests.length > 0) {
        // تقویت بخش‌های مرتبط با علایق کاربر
        const interestMatch = this.calculateInterestMatch(content, userProfile.interests);
        if (interestMatch > 0.7) {
          // افزودن برچسب "پیشنهاد شده برای شما" 
          personalizedContent.personalizedLabel = "پیشنهاد شده برای شما";
        }
      }

      // شخصی‌سازی بر اساس رفتار قبلی
      if (userProfile.behaviorPatterns) {
        const commonPattern = userProfile.behaviorPatterns.find(pattern => 
          content.title?.toLowerCase().includes(pattern.category.toLowerCase()) ||
          content.content?.toLowerCase().includes(pattern.category.toLowerCase())
        );

        if (commonPattern && commonPattern.weight > 0.5) {
          // افزودن محتوای مرتبط بر اساس الگوی رفتاری
          const relatedContent = await this.getRelatedContent(contentId, contentType, commonPattern.category);
          personalizedContent.relatedContent = relatedContent;
        }
      }

      // شخصی‌سازی بر اساس نوع دستگاه
      if (context.deviceType === 'mobile') {
        // ساده‌سازی محتوا برای دستگاه تلفن همراه
        personalizedContent.optimizedForMobile = true;
      }

      // شخصی‌سازی بر اساس زمان روز
      if (context.timeOfDay && context.timeOfDay >= 18) {
        // برای ساعات بعد از ظهر، محتوای آرام‌بخش تر
        personalizedContent.timeBasedAdjustment = "evening";
      }

      // ثبت تعامل کاربر با محتوا
      await this.trackUserEngagement(userId, contentId, contentType, {
        viewDuration: 0, // توسط کلاینت تنظیم می‌شود
        scrollDepth: 0,
        clicks: 0
      });

      strapi.log.info(`Personalized content ${contentId} for user ${userId}`);
      return personalizedContent;
    } catch (error) {
      strapi.log.error(`Error personalizing content: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه تطابق علایق با محتوا
   */
  calculateInterestMatch(content: any, interests: string[]): number {
    const contentText = (content.title || '') + ' ' + (content.content || '') + ' ' + (content.description || '');
    const lowerContent = contentText.toLowerCase();

    let matchCount = 0;
    for (const interest of interests) {
      if (lowerContent.includes(interest.toLowerCase())) {
        matchCount++;
      }
    }

    return matchCount / Math.max(1, interests.length);
  },

  /**
   * دریافت محتوای مرتبط
   */
  async getRelatedContent(contentId: string, contentType: string, category: string): Promise<any[]> {
    try {
      // جستجوی محتوای مرتبط بر اساس دسته‌بندی
      const relatedContent = await strapi.entityService.findMany(`api::${contentType}.${contentType}`, {
        where: {
          id: { $ne: contentId }, // استثنای محتوای فعلی
          $or: [
            { title: { $containsi: category } },
            { content: { $containsi: category } },
            { description: { $containsi: category } }
          ]
        },
        limit: 5
      });

      return relatedContent;
    } catch (error) {
      strapi.log.error(`Error getting related content: ${error.message}`);
      return [];
    }
  },

  /**
   * ایجاد پروفایل کاربر
   */
  async createUserProfile(userId: string, initialData?: any): Promise<UserProfile> {
    try {
      const profile: UserProfile = {
        id: `profile_${userId}`,
        userId,
        interests: initialData?.initialInterests || [],
        preferences: {},
        behaviorPatterns: [],
        lastInteraction: new Date(),
        engagementScore: 0,
        segments: [],
        createdAt: new Date(),
        updatedAt: new Date()
      };

      // ذخیره در پایگاه داده
      const createdProfile = await strapi.query('api::user-profile.user-profile').create({
        data: profile
      });

      strapi.log.info(`Created user profile for user: ${userId}`);
      return createdProfile;
    } catch (error) {
      strapi.log.error(`Error creating user profile: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت پروفایل کاربر
   */
  async getUserProfile(userId: string): Promise<UserProfile | null> {
    try {
      const profile = await strapi.query('api::user-profile.user-profile').findOne({
        where: { userId }
      });

      return profile;
    } catch (error) {
      strapi.log.error(`Error getting user profile: ${error.message}`);
      return null;
    }
  },

  /**
   * به‌روزرسانی پروفایل کاربر
   */
  async updateUserProfile(userId: string, data: any): Promise<UserProfile> {
    try {
      const existingProfile = await this.getUserProfile(userId);
      if (!existingProfile) {
        throw new Error(`User profile not found for user: ${userId}`);
      }

      const updatedProfile = await strapi.query('api::user-profile.user-profile').update({
        where: { userId },
        data: {
          ...data,
          updatedAt: new Date().toISOString()
        }
      });

      strapi.log.info(`Updated user profile for user: ${userId}`);
      return updatedProfile;
    } catch (error) {
      strapi.log.error(`Error updating user profile: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت توصیه‌های شخصی‌سازی شده
   */
  async getPersonalizedRecommendations(userId: string, limit: number = 5): Promise<any[]> {
    try {
      // دریافت پروفایل کاربر
      const userProfile = await this.getUserProfile(userId);
      if (!userProfile) {
        // اگر پروفایل وجود نداشت، یکی ایجاد می‌کنیم
        await this.createUserProfile(userId);
        return []; // بازگرداندن خالی تا کاربر ابتدا تعامل ایجاد کند
      }

      // تهیه لیست توصیه‌ها بر اساس علایق و رفتار کاربر
      const recommendations = [];

      // ۱. محتوای مرتبط با علایق کاربر
      if (userProfile.interests.length > 0) {
        for (const interest of userProfile.interests) {
          const contentByInterest = await strapi.entityService.findMany('api::blog-post.blog-post', {
            where: {
              $or: [
                { title: { $containsi: interest } },
                { content: { $containsi: interest } },
                { tags: { name: { $containsi: interest } } }
              ]
            },
            limit: Math.floor(limit / userProfile.interests.length)
          });

          recommendations.push(...contentByInterest);
        }
      }

      // ۲. محتوای مرتبط با الگوهای رفتاری
      if (userProfile.behaviorPatterns.length > 0) {
        for (const pattern of userProfile.behaviorPatterns) {
          if (pattern.weight > 0.3) { // فقط الگوهای قوی
            const contentByPattern = await strapi.entityService.findMany('api::blog-post.blog-post', {
              where: {
                $or: [
                  { title: { $containsi: pattern.category } },
                  { content: { $containsi: pattern.category } }
                ]
              },
              limit: 2
            });

            recommendations.push(...contentByPattern);
          }
        }
      }

      // ۳. محتوای پرطرفدار در زمینه‌های مرتبط
      const trendingContent = await strapi.service('analytics-service').getTrendingContent(
        'main', // tenant - در عمل باید از پروفایل کاربر گرفته شود
        'blog-post',
        7, // ۷ روز اخیر
        Math.max(1, limit - recommendations.length) // تعداد باقیمانده
      );

      recommendations.push(...trendingContent);

      // حذف تکراری‌ها و محدود کردن نتایج
      const uniqueRecommendations = [...new Map(recommendations.map(item => [item.id, item])).values()];
      return uniqueRecommendations.slice(0, limit);
    } catch (error) {
      strapi.log.error(`Error getting personalized recommendations: ${error.message}`);
      return [];
    }
  },

  /**
   * ردیابی تعامل کاربر
   */
  async trackUserEngagement(userId: string, contentId: string, contentType: string, engagement: EngagementData): Promise<void> {
    try {
      // ذخیره داده تعامل در پایگاه داده
      await strapi.query('api::user-engagement.user-engagement').create({
        data: {
          userId,
          contentId,
          contentType,
          engagementData: engagement,
          timestamp: new Date().toISOString()
        }
      });

      // به‌روزرسانی پروفایل کاربر بر اساس تعامل
      await this.updateUserProfileBasedOnEngagement(userId, contentId, contentType, engagement);

      strapi.log.info(`Tracked user engagement: ${userId} -> ${contentType}:${contentId}`);
    } catch (error) {
      strapi.log.error(`Error tracking user engagement: ${error.message}`);
      throw error;
    }
  },

  /**
   * به‌روزرسانی پروفایل کاربر بر اساس تعامل
   */
  async updateUserProfileBasedOnEngagement(userId: string, contentId: string, contentType: string, engagement: EngagementData): Promise<void> {
    try {
      const userProfile = await this.getUserProfile(userId);
      if (!userProfile) {
        return;
      }

      // محاسبه نمره تعامل جدید
      let engagementScore = userProfile.engagementScore || 0;
      engagementScore += (engagement.viewDuration || 0) / 100; // هر 100 ثانیه یک نمره
      engagementScore += (engagement.scrollDepth || 0) / 10;
      engagementScore += (engagement.clicks || 0) * 2;
      engagementScore += (engagement.shares || 0) * 5;
      engagementScore += (engagement.comments || 0) * 3;
      engagementScore += (engagement.rating || 0);
      if (engagement.completed) engagementScore += 10;

      // به‌روزرسانی الگوهای رفتاری
      const content = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
      if (content) {
        const category = content.category || content.tags?.[0]?.name || 'general';
        let patternFound = false;

        const updatedPatterns = userProfile.behaviorPatterns.map(pattern => {
          if (pattern.category === category) {
            patternFound = true;
            // افزایش وزن الگو بر اساس تعامل
            const newWeight = Math.min(1, pattern.weight + (engagementScore * 0.01));
            return { ...pattern, weight: newWeight, lastSeen: new Date() };
          }
          return pattern;
        });

        if (!patternFound) {
          updatedPatterns.push({
            category,
            weight: Math.min(1, engagementScore * 0.01),
            lastSeen: new Date()
          });
        }

        // به‌روزرسانی پروفایل
        await strapi.query('api::user-profile.user-profile').update({
          where: { userId },
          data: {
            behaviorPatterns: updatedPatterns,
            engagementScore,
            lastInteraction: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        });
      }

      strapi.log.debug(`Updated user profile based on engagement: ${userId}`);
    } catch (error) {
      strapi.log.error(`Error updating user profile based on engagement: ${error.message}`);
    }
  },

  /**
   * ایجاد بخش مخاطب
   */
  async createAudienceSegment(segmentData: AudienceSegment): Promise<AudienceSegment> {
    try {
      const segment = await strapi.query('api::audience-segment.audience-segment').create({
        data: segmentData
      });

      // محاسبه تعداد اعضای بخش
      const memberCount = await this.calculateSegmentMembers(segment);
      await strapi.query('api::audience-segment.audience-segment').update({
        where: { id: segment.id },
        data: { memberCount }
      });

      strapi.log.info(`Created audience segment: ${segment.name}`);
      return { ...segment, memberCount };
    } catch (error) {
      strapi.log.error(`Error creating audience segment: ${error.message}`);
      throw error;
    }
  },

  /**
   * محاسبه اعضای بخش
   */
  async calculateSegmentMembers(segment: AudienceSegment): Promise<number> {
    try {
      // این تابع باید بر اساس معیارهای بخش، تعداد کاربران مطابق را بشمارد
      // در این نمونه، فقط یک عدد ساده برمی‌گردانیم
      return await strapi.query('plugin::users-permissions.user').count({});
    } catch (error) {
      strapi.log.error(`Error calculating segment members: ${error.message}`);
      return 0;
    }
  },

  /**
   * دریافت بخشهای مخاطب
   */
  async getAudienceSegments(tenant: string): Promise<AudienceSegment[]> {
    try {
      const segments = await strapi.query('api::audience-segment.audience-segment').findMany({
        where: { tenant }
      });

      return segments;
    } catch (error) {
      strapi.log.error(`Error getting audience segments: ${error.message}`);
      return [];
    }
  }
});