import { StrapiService } from '@strapi/strapi';
import { Server } from 'socket.io';

interface RealtimeSyncService {
  initialize(): void;
  emitToTenant(tenant: string, event: string, data: any): void;
  broadcastToAll(data: any): void;
  handleContentChange(contentType: string, action: string, data: any, tenant: string): void;
}

/**
 * سرویس همگام‌سازی لحظه‌ای
 * امکان ارسال اطلاع‌رسانی‌های لحظه‌ای به فرانت‌اند وب را فراهم می‌کند
 */
export default ({
  strapi
}: {
  strapi: { log: any; server: any; config: any };
}): RealtimeSyncService => {
  let io: Server | null = null;

  return {
    /**
     * مقداردهی اولیه سرویس WebSocket
     */
    initialize(): void {
      try {
        // دریافت سرور HTTP از Strapi
        const httpServer = strapi.server.httpServer;

        // ایجاد نمونه Socket.IO
        io = new Server(httpServer, {
          cors: {
            origin: strapi.config.get('middleware.settings.cors.origin', '*'),
            methods: ['GET', 'POST']
          },
          transports: ['websocket', 'polling']
        });

        // مدیریت اتصالات
        io.on('connection', (socket) => {
          strapi.log.info(`New socket connection established: ${socket.id}`);

          // اجازه به کلاینت برای عضویت در اتاق‌های tenant
          socket.on('join_tenant_room', (tenantId) => {
            socket.join(`tenant_${tenantId}`);
            strapi.log.info(`Socket ${socket.id} joined tenant room: ${tenantId}`);
          });

          // اجازه به کلاینت برای عضویت در اتاق‌های نوع محتوا
          socket.on('join_content_type_room', (contentType) => {
            socket.join(`content_type_${contentType}`);
            strapi.log.info(`Socket ${socket.id} joined content type room: ${contentType}`);
          });

          // مدیریت قطع اتصال
          socket.on('disconnect', () => {
            strapi.log.info(`Socket disconnected: ${socket.id}`);
          });
        });

        strapi.log.info('WebSocket server initialized for realtime sync');
      } catch (error) {
        strapi.log.error(`Error initializing WebSocket server: ${error.message}`);
      }
    },

    /**
     * ارسال رویداد به تمام کاربران یک tenant
     */
    emitToTenant(tenant: string, event: string, data: any): void {
      if (!io) {
        strapi.log.error('WebSocket server not initialized');
        return;
      }

      try {
        io.to(`tenant_${tenant}`).emit(event, data);
        strapi.log.debug(`Emitted event '${event}' to tenant '${tenant}' with data:`, data);
      } catch (error) {
        strapi.log.error(`Error emitting to tenant ${tenant}: ${error.message}`);
      }
    },

    /**
     * ارسال رویداد به تمام کاربران
     */
    broadcastToAll(data: any): void {
      if (!io) {
        strapi.log.error('WebSocket server not initialized');
        return;
      }

      try {
        io.emit('broadcast', data);
        strapi.log.debug('Broadcasted data to all clients:', data);
      } catch (error) {
        strapi.log.error(`Error broadcasting: ${error.message}`);
      }
    },

    /**
     * مدیریت تغییر محتوا و ارسال اطلاع‌رسانی لحظه‌ای
     */
    handleContentChange(contentType: string, action: string, data: any, tenant: string): void {
      if (!io) {
        strapi.log.error('WebSocket server not initialized');
        return;
      }

      try {
        // ارسال به اتاق tenant
        this.emitToTenant(tenant, 'content_update', {
          contentType,
          action,
          data,
          timestamp: new Date().toISOString()
        });

        // ارسال به اتاق نوع محتوا
        io.to(`content_type_${contentType}`).emit('content_update', {
          contentType,
          action,
          data,
          tenant,
          timestamp: new Date().toISOString()
        });

        strapi.log.info(`Handled content change: ${contentType} - ${action} for tenant: ${tenant}`);
      } catch (error) {
        strapi.log.error(`Error handling content change: ${error.message}`);
      }
    }
  };
};