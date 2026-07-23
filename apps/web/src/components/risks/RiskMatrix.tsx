// apps/web/src/components/risks/RiskMatrix.tsx
// ماتریس ۳×۳ تعاملی: impact (سطرها، high بالا) × likelihood (ستون‌ها).
// شمارش per-cell فقط برای ریسک‌های open؛ کلیک → toggle فیلتر آن ترکیب.
import { IMPACTS, LIKELIHOODS, SCORE_MATRIX, SCORE_STYLE, matrixCounts, type Risk, type Impact, type Likelihood } from "./risksData";
import { impactText, likelihoodText, scoreText, type RiskStrings, type RiskLang } from "./risksI18n";
import { SectionReveal } from "../eco/SectionReveal";

export interface MatrixFilter { impact: Impact; likelihood: Likelihood; }

interface Props {
  risks: Risk[];            // ریسک‌هایی که باید شمرده شوند (بدون فیلتر ماتریس)
  filter: MatrixFilter | null;
  onToggle: (f: MatrixFilter) => void;
  strings: RiskStrings;
  lang: RiskLang;
}

export function RiskMatrix({ risks, filter, onToggle, strings: s }: Props) {
  const counts = matrixCounts(risks);

  return (
    <SectionReveal delay={90}>
      <div className="rounded-2xl border border-stone-200/80 bg-white p-5 shadow-sm sm:p-6">
        <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-display text-lg text-stone-800">{s.matrixTitle}</h2>
          <p className="text-xs text-stone-500">{s.matrixHint}</p>
        </div>

        <div className="mt-4 flex gap-3">
          {/* برچسب محور Y */}
          <div className="flex flex-col justify-around py-1 text-end">
            <span className="text-[10px] font-bold uppercase tracking-wide text-stone-400 [writing-mode:vertical-rl] rotate-180 sm:[writing-mode:horizontal-tb] sm:rotate-0 sm:hidden">{s.axisImpact}</span>
            {IMPACTS.map((imp) => (
              <span key={imp} className="hidden text-xs font-bold text-stone-600 sm:block">{impactText(s, imp)}</span>
            ))}
          </div>

          <div className="flex-1">
            {/* برچسب محور X */}
            <div className="mb-1 grid grid-cols-3 gap-2">
              {LIKELIHOODS.map((lk) => (
                <span key={lk} className="text-center text-xs font-bold text-stone-600">{likelihoodText(s, lk)}</span>
              ))}
            </div>
            <p className="mb-2 text-center text-[10px] font-bold uppercase tracking-wide text-stone-400">{s.axisLikelihood}</p>

            {/* سلول‌ها */}
            <div className="grid grid-cols-3 gap-2">
              {IMPACTS.map((imp) =>
                LIKELIHOODS.map((lk) => {
                  const sc = SCORE_MATRIX[imp][lk];
                  const st = SCORE_STYLE[sc];
                  const n = counts[`${imp}|${lk}`] || 0;
                  const active = filter?.impact === imp && filter?.likelihood === lk;
                  return (
                    <button
                      key={`${imp}|${lk}`}
                      onClick={() => onToggle({ impact: imp, likelihood: lk })}
                      aria-pressed={active}
                      aria-label={`${impactText(s, imp)} × ${likelihoodText(s, lk)}: ${n} — ${scoreText(s, sc)}`}
                      className={`relative grid aspect-[4/3] place-items-center rounded-xl text-center transition-all hover:-translate-y-0.5 hover:shadow-md ${st.cell} ${active ? "ring-4 ring-stone-800/30 scale-[1.03]" : "opacity-95 hover:opacity-100"}`}
                    >
                      <span className="font-display text-2xl font-black tabular-nums leading-none">{n}</span>
                      <span className="mt-0.5 text-[10px] font-bold uppercase opacity-90">{scoreText(s, sc)}</span>
                    </button>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </SectionReveal>
  );
}