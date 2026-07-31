import { StrapiService } from '@strapi/strapi';
import xss from 'xss';

interface ContentSanitizerService {
  sanitize(content: string): string;
  validateContentType(data: any, contentType: string): Promise<boolean>;
  validateRichText(content: string): boolean;
}

/**
 * Content Sanitization Service
 * Validates and sanitizes content to prevent XSS and other attacks
 */
export default ({
  strapi
}: {
  strapi: { log: any };
}): ContentSanitizerService => ({
  /**
   * Sanitize user-provided content to prevent XSS
   */
  sanitize(content: string): string {
    if (typeof content !== 'string') {
      return content;
    }

    // Use XSS library to sanitize HTML content
    const sanitized = xss(content, {
      whiteList: {
        p: ['style', 'class'],
        br: [],
        span: ['style', 'class'],
        strong: ['style', 'class'],
        b: ['style', 'class'],
        em: ['style', 'class'],
        i: ['style', 'class'],
        u: ['style', 'class'],
        h1: ['style', 'class'],
        h2: ['style', 'class'],
        h3: ['style', 'class'],
        h4: ['style', 'class'],
        h5: ['style', 'class'],
        h6: ['style', 'class'],
        ul: ['style', 'class'],
        ol: ['style', 'class'],
        li: ['style', 'class'],
        a: ['href', 'title', 'style', 'class', 'target'],
        img: ['src', 'alt', 'title', 'width', 'height', 'style', 'class'],
        div: ['style', 'class'],
        blockquote: ['style', 'class'],
        code: ['class'],
        pre: ['class'],
        table: ['style', 'class'],
        thead: ['style', 'class'],
        tbody: ['style', 'class'],
        tr: ['style', 'class'],
        th: ['style', 'class'],
        td: ['style', 'class']
      },
      stripIgnoreTag: true,
      stripIgnoreTagBody: ['script', 'style', 'xml']
    });

    return sanitized;
  },

  /**
   * Validate content against specific content type schema
   */
  async validateContentType(data: any, contentType: string): Promise<boolean> {
    try {
      // Get content type schema from Strapi
      const schema = strapi.contentTypes[`api::${contentType}.${contentType}`];
      
      if (!schema) {
        throw new Error(`Content type ${contentType} not found`);
      }

      // Validate required fields
      for (const [attrName, attrConfig] of Object.entries(schema.attributes)) {
        if (attrConfig.required && !data[attrName]) {
          throw new Error(`Required field ${attrName} is missing`);
        }
        
        // Validate field types
        if (data[attrName] !== undefined && data[attrName] !== null) {
          const value = data[attrName];
          const type = attrConfig.type;
          
          switch (type) {
            case 'string':
              if (typeof value !== 'string') {
                throw new Error(`Field ${attrName} must be a string`);
              }
              break;
              
            case 'text':
              if (typeof value !== 'string') {
                throw new Error(`Field ${attrName} must be a text string`);
              }
              break;
              
            case 'number':
            case 'integer':
            case 'float':
              if (typeof value !== 'number' && typeof value !== 'string') {
                throw new Error(`Field ${attrName} must be a number`);
              }
              if (isNaN(Number(value))) {
                throw new Error(`Field ${attrName} must be a valid number`);
              }
              break;
              
            case 'boolean':
              if (typeof value !== 'boolean' && 
                  !(typeof value === 'string' && ['true', 'false'].includes(value.toLowerCase())) &&
                  !(typeof value === 'number' && [0, 1].includes(value))) {
                throw new Error(`Field ${attrName} must be a boolean`);
              }
              break;
              
            case 'date':
            case 'datetime':
              if (isNaN(Date.parse(value))) {
                throw new Error(`Field ${attrName} must be a valid date`);
              }
              break;
              
            case 'relation':
              // Relations validation depends on the relation type
              if (Array.isArray(attrConfig.relation) || attrConfig.relation.includes('Many')) {
                if (!Array.isArray(value)) {
                  throw new Error(`Field ${attrName} must be an array for many relations`);
                }
              }
              break;
              
            case 'media':
              // Validate media fields
              if (typeof value !== 'object' && !Array.isArray(value)) {
                throw new Error(`Field ${attrName} must be a media object or array`);
              }
              break;
          }
        }
      }

      return true;
    } catch (error) {
      strapi.log.error(`Content validation failed: ${error.message}`);
      return false;
    }
  },

  /**
   * Validate rich text content for security
   */
  validateRichText(content: string): boolean {
    if (typeof content !== 'string') {
      return false;
    }

    // Check for potentially dangerous patterns
    const dangerousPatterns = [
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,  // Script tags
      /javascript:/gi,                                         // JS protocol
      /vbscript:/gi,                                           // VBScript protocol
      /on\w+\s*=/gi,                                           // Event handlers
      /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,   // Iframe tags
      /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,   // Object tags
      /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi       // Embed tags
    ];

    for (const pattern of dangerousPatterns) {
      if (pattern.test(content)) {
        return false;
      }
    }

    return true;
  }
});