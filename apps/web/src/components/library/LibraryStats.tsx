// apps/web/src/components/library/LibraryStats.tsx
import { BookOpen, FileText, Video, Headphones } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { Resource } from "./libraryData";
import { countByType } from "./libraryData";
import type { LibraryStrings } from "./libraryI18n";

interface Props {
  resources: Resource[];
  strings: LibraryStrings;
}

export function LibraryStats({ resources, strings: s }: Props) {
  const cards = [
    { icon: BookOpen, label: s.statTotal, value: resources.length, color: "text-green-700", bg: "bg-green-50" },
    { icon: FileText, label: s.statDocs, value: countByType(resources, "pdf") + countByType(resources, "doc"), color: "text-blue-700", bg: "bg-blue-50" },
    { icon: Video, label: s.statVideos, value: countByType(resources, "video"), color: "text-violet-700", bg: "bg-violet-50" },
    { icon: Headphones, label: s.statAudio, value: countByType(resources, "audio"), color: "text-amber-700", bg: "bg-amber-50" },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <c.icon className={`h-5 w-5 shrink-0 ${c.color}`} />
            <div>
              <p className={`font-display text-2xl font-black tabular-nums leading-none ${c.color}`}>
                <AnimatedCounter end={c.value} />
              </p>
              <p className="mt-1 text-xs font-medium text-stone-600">{c.label}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}