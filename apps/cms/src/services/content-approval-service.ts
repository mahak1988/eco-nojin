import { StrapiService } from '@strapi/strapi';

interface ContentApprovalService {
  submitForApproval(contentId: string, contentType: string, submitterId: string, notes?: string): Promise<any>;
  approveContent(approvalId: string, approverId: string, notes?: string): Promise<any>;
  rejectContent(approvalId: string, approverId: string, reason: string): Promise<any>;
  getPendingApprovals(tenant: string, contentType?: string): Promise<any[]>;
  getApprovalHistory(contentId: string, contentType: string): Promise<any[]>;
}

/**
 * سرویس گردش کار تأیید محتوا
 * امکان مدیریت فرآیند تأیید محتوا توسط کاربران مجاز را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { query: any; log: any; config: any; entityService: any };
}): ContentApprovalService => ({
  /**
   * ارسال محتوا برای تأیید
   */
  async submitForApproval(contentId: string, contentType: string, submitterId: string, notes?: string): Promise<any> {
    try {
      // بررسی وجود محتوا
      const content = await strapi.entityService.findOne(`api::${contentType}.${contentType}`, contentId);
      if (!content) {
        throw new Error(`Content not found: ${contentId}`);
      }

      // بررسی وضعیت فعلی محتوا
      if (content.publishedAt) {
        throw new Error('Cannot submit already published content for approval');
      }

      // تعیین tenant
      const tenant = content.tenant || 'main';

      // ایجاد درخواست تأیید
      const approvalRequest = await strapi.query('api::content-approval.content-approval').create({
        data: {
          contentId,
          contentType,
          submitter: submitterId,
          status: 'pending',
          notes: notes || '',
          tenant,
          createdAt: new Date().toISOString()
        }
      });

      // ارسال اعلان به تأییدکنندگان
      await this.notifyApprovers(contentId, contentType, tenant);

      strapi.log.info(`Content ${contentId} submitted for approval by user ${submitterId}`);
      return approvalRequest;
    } catch (error) {
      strapi.log.error(`Error submitting content for approval: ${error.message}`);
      throw error;
    }
  },

  /**
   * تأیید محتوا
   */
  async approveContent(approvalId: string, approverId: string, notes?: string): Promise<any> {
    try {
      // دریافت درخواست تأیید
      const approval = await strapi.query('api::content-approval.content-approval').findOne({
        where: { id: approvalId }
      });

      if (!approval) {
        throw new Error(`Approval request not found: ${approvalId}`);
      }

      if (approval.status !== 'pending') {
        throw new Error(`Approval request is not pending: ${approvalId}`);
      }

      // بررسی دسترسی تأییدکننده
      const approver = await strapi.query('plugin::users-permissions.user').findOne({
        where: { id: approverId }
      });

      if (!this.hasApprovalPermission(approver, approval.tenant)) {
        throw new Error('User does not have permission to approve content');
      }

      // به‌روزرسانی وضعیت درخواست تأیید
      const updatedApproval = await strapi.query('api::content-approval.content-approval').update({
        where: { id: approvalId },
        data: {
          status: 'approved',
          approver: approverId,
          approvedAt: new Date().toISOString(),
          reviewNotes: notes || ''
        }
      });

      // انتشار محتوا
      await strapi.entityService.update(`api::${approval.contentType}.${approval.contentType}`, approval.contentId, {
        data: {
          publishedAt: new Date().toISOString()
        }
      });

      // ارسال اعلان درباره تأیید
      await this.notifyContentApproved(approval.contentId, approval.contentType, approverId);

      strapi.log.info(`Content ${approval.contentId} approved by user ${approverId}`);
      return updatedApproval;
    } catch (error) {
      strapi.log.error(`Error approving content: ${error.message}`);
      throw error;
    }
  },

  /**
   * عدم تأیید محتوا
   */
  async rejectContent(approvalId: string, approverId: string, reason: string): Promise<any> {
    try {
      // دریافت درخواست تأیید
      const approval = await strapi.query('api::content-approval.content-approval').findOne({
        where: { id: approvalId }
      });

      if (!approval) {
        throw new Error(`Approval request not found: ${approvalId}`);
      }

      if (approval.status !== 'pending') {
        throw new Error(`Approval request is not pending: ${approvalId}`);
      }

      // بررسی دسترسی تأییدکننده
      const approver = await strapi.query('plugin::users-permissions.user').findOne({
        where: { id: approverId }
      });

      if (!this.hasApprovalPermission(approver, approval.tenant)) {
        throw new Error('User does not have permission to reject content');
      }

      // به‌روزرسانی وضعیت درخواست تأیید
      const updatedApproval = await strapi.query('api::content-approval.content-approval').update({
        where: { id: approvalId },
        data: {
          status: 'rejected',
          approver: approverId,
          rejectedAt: new Date().toISOString(),
          reviewNotes: reason
        }
      });

      // ارسال اعلان درباره عدم تأیید
      await this.notifyContentRejected(approval.contentId, approval.contentType, approverId, reason);

      strapi.log.info(`Content ${approval.contentId} rejected by user ${approverId}`);
      return updatedApproval;
    } catch (error) {
      strapi.log.error(`Error rejecting content: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت تأییدهای در انتظار
   */
  async getPendingApprovals(tenant: string, contentType?: string): Promise<any[]> {
    try {
      const whereClause: any = {
        tenant,
        status: 'pending'
      };

      if (contentType) {
        whereClause.contentType = contentType;
      }

      const approvals = await strapi.query('api::content-approval.content-approval').findMany({
        where: whereClause,
        populate: ['submitter', 'content']
      });

      strapi.log.debug(`Found ${approvals.length} pending approvals for tenant ${tenant}`);
      return approvals;
    } catch (error) {
      strapi.log.error(`Error getting pending approvals: ${error.message}`);
      throw error;
    }
  },

  /**
   * دریافت تاریخچه تأیید
   */
  async getApprovalHistory(contentId: string, contentType: string): Promise<any[]> {
    try {
      const history = await strapi.query('api::content-approval.content-approval').findMany({
        where: {
          contentId,
          contentType
        },
        sort: { createdAt: 'desc' },
        populate: ['submitter', 'approver']
      });

      strapi.log.debug(`Found ${history.length} approval history items for content ${contentId}`);
      return history;
    } catch (error) {
      strapi.log.error(`Error getting approval history: ${error.message}`);
      throw error;
    }
  },

  /**
   * بررسی مجوز تأیید برای یک کاربر
   */
  hasApprovalPermission(user: any, tenant: string): boolean {
    // بررسی نقش کاربر برای تعیین مجوز تأیید
    const userRole = user.role?.name || '';
    
    // کاربران ادمین و سوپر ادمین همیشه مجوز دارند
    if (['strapi-admin', 'strapi-super-admin'].includes(userRole)) {
      return true;
    }

    // بررسی مجوزهای سفارشی در تنظیمات tenant
    // در این نمونه، فرض می‌کنیم نقش‌های خاصی مجوز تأیید دارند
    return ['editor', 'reviewer', 'approver'].includes(userRole);
  },

  /**
   * اعلان به تأییدکنندگان
   */
  async notifyApprovers(contentId: string, contentType: string, tenant: string): Promise<void> {
    try {
      // دریافت تأییدکنندگان مجاز برای این tenant
      const approvers = await strapi.query('plugin::users-permissions.user').findMany({
        where: {
          tenant,
          role: {
            name: {
              $in: ['strapi-admin', 'editor', 'reviewer', 'approver']
            }
          }
        }
      });

      // ارسال اعلان به هر یک از تأییدکنندگان
      const notificationService = strapi.service('notification-service');
      if (notificationService) {
        await notificationService.notifyContentUpdate(
          contentType,
          'submitted_for_approval',
          { id: contentId },
          approvers.map(user => user.id)
        );
      }

      strapi.log.info(`Notified ${approvers.length} approvers about content ${contentId}`);
    } catch (error) {
      strapi.log.error(`Error notifying approvers: ${error.message}`);
    }
  },

  /**
   * اعلان درباره تأیید محتوا
   */
  async notifyContentApproved(contentId: string, contentType: string, approverId: string): Promise<void> {
    try {
      const notificationService = strapi.service('notification-service');
      if (notificationService) {
        await notificationService.notifyContentUpdate(
          contentType,
          'approved',
          { id: contentId },
          [approverId]
        );
      }

      // همچنین ارسال اطلاع‌رسانی لحظه‌ای
      const realtimeSync = strapi.service('realtime-sync');
      if (realtimeSync) {
        realtimeSync.handleContentChange(contentType, 'publish', { id: contentId }, 'main');
      }
    } catch (error) {
      strapi.log.error(`Error notifying content approved: ${error.message}`);
    }
  },

  /**
   * اعلان درباره عدم تأیید محتوا
   */
  async notifyContentRejected(contentId: string, contentType: string, approverId: string, reason: string): Promise<void> {
    try {
      const notificationService = strapi.service('notification-service');
      if (notificationService) {
        await notificationService.notifyContentUpdate(
          contentType,
          'rejected',
          { id: contentId, reason },
          [approverId]
        );
      }
    } catch (error) {
      strapi.log.error(`Error notifying content rejected: ${error.message}`);
    }
  }
});