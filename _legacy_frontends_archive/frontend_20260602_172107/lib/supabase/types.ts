export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      resources: {
        Row: {
          id: string;
          title: string;
          description: string;
          resource_type: string;
          file_url: string;
          category: string;
          language: string;
          author: string;
          tags: string[];
          download_count: number;
          view_count: number;
          rating: number;
          rating_count: number;
          cover_color: string;
          uploader_id: string | null;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['resources']['Row'], 'id' | 'created_at' | 'download_count' | 'view_count' | 'rating' | 'rating_count'>;
        Update: Partial<Database['public']['Tables']['resources']['Insert']>;
      };
      comments: {
        Row: {
          id: string;
          resource_id: string;
          user_id: string;
          user_name: string;
          user_avatar: string | null;
          content: string;
          rating: number | null;
          parent_id: string | null;
          likes_count: number;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['comments']['Row'], 'id' | 'created_at' | 'likes_count'>;
        Update: Partial<Database['public']['Tables']['comments']['Insert']>;
      };
      wishlists: {
        Row: {
          id: string;
          user_id: string;
          resource_id: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['wishlists']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['wishlists']['Insert']>;
      };
    };
  };
}

export type Resource = Database['public']['Tables']['resources']['Row'];
export type Comment = Database['public']['Tables']['comments']['Row'];
export type Wishlist = Database['public']['Tables']['wishlists']['Row'];