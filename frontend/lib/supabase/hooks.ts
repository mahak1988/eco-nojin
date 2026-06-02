'use client';

import { useEffect, useState } from 'react';
import { getSupabaseClient } from './client';
import type { Resource, Comment } from './types';

// Hook for fetching resources
export function useResources(filters?: {
  category?: string;
  type?: string;
  search?: string;
  limit?: number;
}) {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchResources() {
      try {
        const supabase = getSupabaseClient();
        let query = supabase
          .from('resources')
          .select('*')
          .order('created_at', { ascending: false });

        if (filters?.category && filters.category !== 'all') {
          query = query.eq('category', filters.category);
        }
        if (filters?.type && filters.type !== 'all') {
          query = query.eq('resource_type', filters.type);
        }
        if (filters?.search) {
          query = query.or(`title.ilike.%${filters.search}%,description.ilike.%${filters.search}%`);
        }
        if (filters?.limit) {
          query = query.limit(filters.limit);
        }

        const { data, error } = await query;
        if (error) throw error;
        setResources(data || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchResources();
  }, [filters?.category, filters?.type, filters?.search, filters?.limit]);

  return { resources, loading, error };
}

// Hook for fetching comments
export function useComments(resourceId: string) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchComments = async () => {
    try {
      const supabase = getSupabaseClient();
      const { data, error } = await supabase
        .from('comments')
        .select('*')
        .eq('resource_id', resourceId)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setComments(data || []);
    } catch (err) {
      console.error('Error fetching comments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (resourceId) fetchComments();
  }, [resourceId]);

  const addComment = async (content: string, rating?: number) => {
    const supabase = getSupabaseClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      alert('لطفا ابتدا وارد شوید');
      return null;
    }

    const { data, error } = await supabase
      .from('comments')
      .insert({
        resource_id: resourceId,
        user_id: user.id,
        user_name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'کاربر',
        user_avatar: user.user_metadata?.avatar_url || null,
        content,
        rating: rating || null,
      })
      .select()
      .single();

    if (error) {
      console.error('Error adding comment:', error);
      return null;
    }

    setComments(prev => [data, ...prev]);
    return data;
  };

  return { comments, loading, addComment, refetch: fetchComments };
}

// Hook for wishlist
export function useWishlist() {
  const [wishlistIds, setWishlistIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchWishlist() {
      try {
        const supabase = getSupabaseClient();
        const { data: { user } } = await supabase.auth.getUser();
        
        if (!user) {
          setLoading(false);
          return;
        }

        const { data } = await supabase
          .from('wishlists')
          .select('resource_id')
          .eq('user_id', user.id);

        setWishlistIds((data || []).map(item => item.resource_id));
      } catch (err) {
        console.error('Error fetching wishlist:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchWishlist();
  }, []);

  const isInWishlist = (resourceId: string) => wishlistIds.includes(resourceId);

  const toggleWishlist = async (resourceId: string) => {
    const supabase = getSupabaseClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      alert('لطفا ابتدا وارد شوید');
      return false;
    }

    if (isInWishlist(resourceId)) {
      await supabase
        .from('wishlists')
        .delete()
        .eq('user_id', user.id)
        .eq('resource_id', resourceId);
      setWishlistIds(prev => prev.filter(id => id !== resourceId));
      return false;
    } else {
      await supabase
        .from('wishlists')
        .insert({ user_id: user.id, resource_id: resourceId });
      setWishlistIds(prev => [...prev, resourceId]);
      return true;
    }
  };

  return { wishlistIds, isInWishlist, toggleWishlist, loading };
}