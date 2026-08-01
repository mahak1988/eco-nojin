// Minimal OpenAPI schema containing only essential API paths for the application
export interface paths {
  "/api/v1/login/access-token": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post: operations["login_access_token_api_v1_login_access_token_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/v1/users/me": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    /** Read Current User */
    get: operations["read_current_user_api_v1_users_me_get"];
    /** Update Current User */
    put: operations["update_current_user_api_v1_users_me_put"];
    post?: never;
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
  "/api/v1/auth/register": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    get?: never;
    put?: never;
    post: operations["register_user_api_v1_auth_register_post"];
    delete?: never;
    options?: never;
    head?: never;
    patch?: never;
    trace?: never;
  };
}

export interface components {
  schemas: {
    HTTPValidationError: {
      detail?: string;
    };
    Token: {
      access_token: string;
      token_type?: string;
    };
    UserPublic: {
      email: string;
      full_name?: string;
      id: string;
      is_active?: boolean;
      is_superuser?: boolean;
      is_verified?: boolean;
      locale?: string;
    };
    UserCreate: {
      email: string;
      password: string;
      full_name?: string;
      locale?: string;
    };
    UserUpdate: {
      email?: string;
      full_name?: string;
      locale?: string;
    };
  };
}

export interface operations {
  "login_access_token_api_v1_login_access_token_post": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/x-www-form-urlencoded": {
          grant_type?: string;
          username: string;
          password: string;
          scope?: string;
          client_id?: string;
          client_secret?: string;
        };
      };
    };
    responses: {
      200: {
        content: {
          "application/json": components["schemas"]["Token"];
        };
      };
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  "read_current_user_api_v1_users_me_get": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    responses: {
      200: {
        content: {
          "application/json": components["schemas"]["UserPublic"];
        };
      };
    };
  };
  "update_current_user_api_v1_users_me_put": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["UserUpdate"];
      };
    };
    responses: {
      200: {
        content: {
          "application/json": components["schemas"]["UserPublic"];
        };
      };
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  "register_user_api_v1_auth_register_post": {
    parameters: {
      query?: never;
      header?: never;
      path?: never;
      cookie?: never;
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["UserCreate"];
      };
    };
    responses: {
      200: {
        content: {
          "application/json": components["schemas"]["UserPublic"];
        };
      };
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
}