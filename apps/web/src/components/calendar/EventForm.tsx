"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { useCreateCalendarEvent } from "@/hooks/useCalendar";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";

const schema = z.object({
  title: z.string().min(1, "عنوان الزامی است"),
  description: z.string().optional(),
  start_time: z.string().min(1),
  end_time: z.string().min(1),
  location: z.string().optional(),
  category: z.string().default("general"),
});

type FormData = z.infer<typeof schema>;

export function EventForm({ onSuccess }: { onSuccess?: () => void }) {
  const t = useTranslations();
  const create = useCreateCalendarEvent();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      category: "general",
      start_time: new Date().toISOString().slice(0, 16),
      end_time: new Date(Date.now() + 3600000).toISOString().slice(0, 16),
    },
  });

  const onSubmit = async (data: FormData) => {
    await create.mutateAsync({
      ...data,
      start_time: new Date(data.start_time).toISOString(),
      end_time: new Date(data.end_time).toISOString(),
      color: "#3b82f6",
    });
    reset();
    onSuccess?.();
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit(onSubmit)}
      className="grid gap-4 p-5 rounded-2xl border border-slate-800 bg-slate-900/60"
    >
      <h3 className="font-semibold text-slate-100">{t("calendar.new")}</h3>
      <FormField
        id="title"
        label="عنوان"
        {...register("title")}
        error={errors.title?.message}
      />
      <FormField id="description" label="توضیحات" {...register("description")} />
      <div className="grid sm:grid-cols-2 gap-4">
        <FormField
          id="start_time"
          label="شروع"
          type="datetime-local"
          {...register("start_time")}
          error={errors.start_time?.message}
        />
        <FormField
          id="end_time"
          label="پایان"
          type="datetime-local"
          {...register("end_time")}
          error={errors.end_time?.message}
        />
      </div>
      <FormField id="location" label="مکان" {...register("location")} />
      <FormField id="category" label="دسته" {...register("category")} />
      {create.error && (
        <p className="text-sm text-rose-400">
          {(create.error as { detail?: string }).detail || "خطا در ذخیره — ورود کنید"}
        </p>
      )}
      <Button type="submit" disabled={create.isPending} className="bg-blue-600 hover:bg-blue-500">
        {create.isPending ? "..." : t("calendar.save")}
      </Button>
    </motion.form>
  );
}
