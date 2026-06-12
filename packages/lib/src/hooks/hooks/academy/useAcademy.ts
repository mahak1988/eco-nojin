import { useQuery } from '@tanstack/react-query';
import { academyApi } from '@/lib/academy/api';

export function useAcademyStats() {
  return useQuery({
    queryKey: ['academy', 'stats'],
    queryFn: academyApi.getStats,
  });
}

export function useCourses(filters?: { category?: string; level?: string }) {
  return useQuery({
    queryKey: ['academy', 'courses', filters],
    queryFn: () => academyApi.getCourses(filters),
  });
}

export function useCourse(id: number) {
  return useQuery({
    queryKey: ['academy', 'course', id],
    queryFn: () => academyApi.getCourse(id),
    enabled: !!id,
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ['academy', 'categories'],
    queryFn: academyApi.getCategories,
  });
}

export function useStandards() {
  return useQuery({
    queryKey: ['academy', 'standards'],
    queryFn: academyApi.getStandards,
  });
}
