import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { calendarService } from "@/lib/api";

export type CalendarEventInput = {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  category?: string;
  color?: string;
};

export function useCalendarEvents() {
  return useQuery({
    queryKey: ["calendar", "events"],
    queryFn: () => calendarService.list(),
  });
}

export function useCreateCalendarEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CalendarEventInput) => calendarService.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["calendar"] }),
  });
}

export function useDeleteCalendarEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => calendarService.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["calendar"] }),
  });
}
