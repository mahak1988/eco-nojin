export default {
  /**
   * Content Sanitization Hook
   * Sanitizes content before it's saved to the database
   */
  beforeSave: async ({ data, model }) => {
    const strapi = global.strapi;
    const sanitizer = strapi.service('content-sanitizer');

    // Sanitize richtext fields
    for (const [key, value] of Object.entries(data)) {
      const attribute = model.attributes[key];
      
      if (attribute && attribute.type === 'richtext' && typeof value === 'string') {
        data[key] = sanitizer.sanitize(value);
      }
      
      // Sanitize text fields that might contain HTML
      if (attribute && attribute.type === 'text' && typeof value === 'string') {
        // Only sanitize if the text field likely contains HTML
        if (value.includes('<') && value.includes('>')) {
          data[key] = sanitizer.sanitize(value);
        }
      }
      
      // Sanitize string fields that might contain HTML
      if (attribute && attribute.type === 'string' && typeof value === 'string') {
        if (value.includes('<') && value.includes('>')) {
          data[key] = sanitizer.sanitize(value);
        }
      }
    }
  },
  
  /**
   * Validate content before saving
   */
  beforeCreate: async ({ data, model }) => {
    const strapi = global.strapi;
    const sanitizer = strapi.service('content-sanitizer');
    
    // Validate the content type
    const isValid = await sanitizer.validateContentType(data, model.uid);
    
    if (!isValid) {
      throw new Error('Content validation failed');
    }
    
    // Run sanitization
    await exports.beforeSave({ data, model });
  },
  
  beforeUpdate: async ({ data, model }) => {
    const strapi = global.strapi;
    const sanitizer = strapi.service('content-sanitizer');
    
    // Validate the content type
    const isValid = await sanitizer.validateContentType(data, model.uid);
    
    if (!isValid) {
      throw new Error('Content validation failed');
    }
    
    // Run sanitization
    await exports.beforeSave({ data, model });
  }
};