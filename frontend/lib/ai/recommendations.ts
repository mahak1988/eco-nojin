import { getSupabaseClient } from '../supabase/client';
import type { Resource } from '../supabase/types';

/**
 * AI-powered recommendation engine
 * Uses content-based filtering with tag similarity
 */

interface RecommendationOptions {
  resourceId: string;
  limit?: number;
  category?: string;
}

function calculateSimilarity(tags1: string[], tags2: string[]): number {
  if (tags1.length === 0 || tags2.length === 0) return 0;
  const intersection = tags1.filter(tag => tags2.includes(tag));
  const union = [...new Set([...tags1, ...tags2])];
  return intersection.length / union.length; // Jaccard similarity
}

export async function getRecommendations({
  resourceId,
  limit = 6,
  category,
}: RecommendationOptions): Promise<Resource[]> {
  try {
    const supabase = getSupabaseClient();

    // Fetch current resource
    const { data: currentResource, error: currentError } = await supabase
      .from('resources')
      .select('*')
      .eq('id', resourceId)
      .single();

    if (currentError || !currentResource) {
      console.error('Error fetching current resource:', currentError);
      return [];
    }

    // Fetch all other resources
    let query = supabase
      .from('resources')
      .select('*')
      .neq('id', resourceId)
      .order('download_count', { ascending: false });

    if (category) {
      query = query.eq('category', category);
    }

    const { data: allResources, error } = await query;

    if (error || !allResources) {
      console.error('Error fetching resources:', error);
      return [];
    }

    // Calculate similarity scores
    const scoredResources = allResources.map(resource => {
      const tagSimilarity = calculateSimilarity(
        currentResource.tags || [],
        resource.tags || []
      );
      
      const categoryBonus = resource.category === currentResource.category ? 0.2 : 0;
      const authorBonus = resource.author === currentResource.author ? 0.15 : 0;
      const popularityBonus = Math.min(resource.download_count / 1000, 0.3);
      
      const totalScore = tagSimilarity + categoryBonus + authorBonus + popularityBonus;

      return {
        resource,
        score: totalScore,
      };
    });

    // Sort by score and take top N
    const topRecommendations = scoredResources
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(item => item.resource);

    return topRecommendations;
  } catch (err) {
    console.error('Error in recommendations:', err);
    return [];
  }
}

/**
 * Get trending resources based on recent downloads
 */
export async function getTrendingResources(limit: number = 6): Promise<Resource[]> {
  try {
    const supabase = getSupabaseClient();
    const { data, error } = await supabase
      .from('resources')
      .select('*')
      .order('download_count', { ascending: false })
      .limit(limit);

    if (error) throw error;
    return data || [];
  } catch (err) {
    console.error('Error fetching trending:', err);
    return [];
  }
}

/**
 * Get personalized recommendations based on user wishlist
 */
export async function getPersonalizedRecommendations(
  userId: string,
  limit: number = 6
): Promise<Resource[]> {
  try {
    const supabase = getSupabaseClient();

    // Get user's wishlist
    const { data: wishlist } = await supabase
      .from('wishlists')
      .select('resource_id')
      .eq('user_id', userId);

    if (!wishlist || wishlist.length === 0) {
      return getTrendingResources(limit);
    }

    // Get resources from wishlist
    const wishlistIds = wishlist.map(w => w.resource_id);
    const { data: wishlistResources } = await supabase
      .from('resources')
      .select('*')
      .in('id', wishlistIds);

    if (!wishlistResources || wishlistResources.length === 0) {
      return getTrendingResources(limit);
    }

    // Combine all tags from wishlist
    const allTags = wishlistResources.flatMap(r => r.tags || []);
    const tagFrequency = new Map<string, number>();
    allTags.forEach(tag => {
      tagFrequency.set(tag, (tagFrequency.get(tag) || 0) + 1);
    });

    // Get top tags
    const topTags = Array.from(tagFrequency.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([tag]) => tag);

    // Find resources with similar tags
    const { data: allResources } = await supabase
      .from('resources')
      .select('*')
      .not('id', 'in', `(${wishlistIds.join(',')})`);

    if (!allResources) return [];

    const scored = allResources.map(resource => {
      const resourceTags = resource.tags || [];
      const matchCount = resourceTags.filter(tag => topTags.includes(tag)).length;
      return { resource, score: matchCount };
    });

    return scored
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(item => item.resource);
  } catch (err) {
    console.error('Error in personalized recommendations:', err);
    return [];
  }
}