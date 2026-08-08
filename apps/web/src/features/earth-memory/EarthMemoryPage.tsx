import React, { useState, useEffect } from 'react';

/* ================================================================
   Earth Memory Page — طراحی بصری ایرانی-مدرن
   الهام از: تذهیب صفوی، گره‌چینی ایرانی، مکتب سوئیس، Ma ژاپنی

   پالت: لاجوردی (#1E3A5F) + فیروزه‌ای (#059669) + اخرایی (#B45309) + کاهگلی (#FFFBEB)
   تایپوگرافی: نسبت طلایی 1.618 — H1=36px, H2=22px, body=16px
   فضای تنفس: 120px بین سکشن‌ها (فضای منفی ژاپنی)
   ================================================================ */

interface TEKPattern {
  pattern_id: string;
  name_fa: string;
  civilization_fa: string;
  age_years: number;
  problem_category: string;
  solution_type: string;
  climate_zones: string[];
  success_score: number;
  sustainability_index: number;
}

const CATEGORIES = [
  { id: 'all', label: 'همه', icon: '🏛️' },
  { id: 'water_scarcity', label: 'کم‌آبی', icon: '💧' },
  { id: 'desertification', label: 'بیابان‌زایی', icon: '🏜️' },
  { id: 'frost_damage', label: 'یخبندان', icon: '❄️' },
  { id: 'soil_degradation', label: 'تخریب خاک', icon: '🪨' },
  { id: 'seasonal_flooding', label: 'سیلاب', icon: '🌊' },
  { id: 'limited_land', label: 'زمین محدود', icon: '🏝️' },
  { id: 'watershed_management', label: 'آبخیزداری', icon: '⛰️' },
  { id: 'steep_slope_erosion', label: 'فرسایش', icon: '⛏️' },
];

const DEMO_PATTERNS: TEKPattern[] = [
  { pattern_id: 'qanat_mirab', name_fa: 'قنات و میراب', civilization_fa: 'ایران باستان', age_years: 3000, problem_category: 'water_scarcity', solution_type: 'water_distribution', climate_zones: ['BWk', 'BWh'], success_score: 0.95, sustainability_index: 1.0 },
  { pattern_id: 'terra_preta', name_fa: 'ترا پرتا — خاک تاریک', civilization_fa: 'آمازون', age_years: 2500, problem_category: 'soil_degradation', solution_type: 'soil_amendment', climate_zones: ['Af', 'Am'], success_score: 0.92, sustainability_index: 1.0 },
  { pattern_id: 'milpa', name_fa: 'میلپا — سه خواهر', civilization_fa: 'مایا', age_years: 4000, problem_category: 'soil_nutrient_depletion', solution_type: 'polyculture_rotation', climate_zones: ['Aw', 'Cwb'], success_score: 0.85, sustainability_index: 0.90 },
  { pattern_id: 'subak', name_fa: 'سوباک — معبد آب', civilization_fa: 'بالی', age_years: 1000, problem_category: 'water_distribution', solution_type: 'community_governance', climate_zones: ['Af', 'Am'], success_score: 0.90, sustainability_index: 0.98 },
  { pattern_id: 'waru_waru', name_fa: 'وارو وارو', civilization_fa: 'آند (پرو)', age_years: 2000, problem_category: 'frost_damage', solution_type: 'thermal_buffer', climate_zones: ['ETH', 'Cwb'], success_score: 0.88, sustainability_index: 0.95 },
  { pattern_id: 'chinampas', name_fa: 'چینامپاس — باغ شناور', civilization_fa: 'آزتک', age_years: 1000, problem_category: 'limited_land', solution_type: 'floating_agriculture', climate_zones: ['Aw', 'Cwb'], success_score: 0.87, sustainability_index: 0.92 },
  { pattern_id: 'dujiangyan', name_fa: 'دوجیانگ‌یان', civilization_fa: 'چین باستان', age_years: 2300, problem_category: 'seasonal_flooding', solution_type: 'flow_diversion', climate_zones: ['Cwa', 'Cfa'], success_score: 0.96, sustainability_index: 1.0 },
  { pattern_id: 'mesopotamian_noria', name_fa: 'نوریا — چرخ آبی', civilization_fa: 'سومر', age_years: 5000, problem_category: 'river_below_fields', solution_type: 'mechanical_lift_irrigation', climate_zones: ['BWh', 'BSh'], success_score: 0.94, sustainability_index: 0.96 },
];

const formatAge = (years: number): string => {
  if (years >= 1000) return `${(years / 1000).toFixed(1)}`;
  return `${years}`;
};

const getCategoryLabel = (cat: string): string =>
  CATEGORIES.find(c => c.id === cat)?.label || cat;

const getCategoryIcon = (cat: string): string =>
  CATEGORIES.find(c => c.id === cat)?.icon || '📜';

// محاسبه درجه برای حلقه سن (older = fuller circle)
const getAgeDegrees = (ageYears: number): number =>
  Math.min(360, (ageYears / 5000) * 360);

const EarthMemoryPage: React.FC = () => {
  const [patterns, setPatterns] = useState<TEKPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  useEffect(() => {
    // Simulate API fetch with entrance animation stagger
    const timer = setTimeout(() => {
      setPatterns(DEMO_PATTERNS);
      setLoading(false);
    }, 600);
    return () => clearTimeout(timer);
  }, []);

  const filtered = selectedCategory === 'all'
    ? patterns
    : patterns.filter(p => p.problem_category === selectedCategory);

  // Persian manuscript border SVG pattern (Girih-inspired)
  const GirihCorner = ({ className }: { className?: string }) => (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path d="M0 12 L0 0 L12 0" stroke="#D97706" strokeWidth="0.5" opacity="0.3" />
      <circle cx="6" cy="6" r="1.5" fill="#D97706" opacity="0.2" />
    </svg>
  );

  return (
    <div style={{
      maxWidth: 1280, margin: '0 auto',
      padding: 'clamp(1rem, 5vw, 4rem)',
      fontFamily: "'Vazirmatn', system-ui, sans-serif",
      direction: 'rtl',
    }}>
      {/* ===== Hero Section — Persian Lapis + Gold ===== */}
      <section style={{
        background: 'linear-gradient(135deg, #1E3A5F 0%, #1a2744 40%, #0f766e 100%)',
        borderRadius: '1.5rem',
        padding: 'clamp(2rem, 6vw, 4rem)',
        marginBottom: '7.5rem',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative Girih Pattern Background */}
        <div style={{
          position: 'absolute', inset: 0, opacity: 0.05,
          backgroundImage: `
            radial-gradient(circle at 20% 30%, #fff 1px, transparent 1px),
            radial-gradient(circle at 80% 70%, #fff 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px',
        }} />

        {/* Gold illumination corners */}
        <div style={{ position: 'absolute', top: 16, left: 16 }}>
          <GirihCorner />
        </div>
        <div style={{ position: 'absolute', top: 16, right: 16, transform: 'scaleX(-1)' }}>
          <GirihCorner />
        </div>
        <div style={{ position: 'absolute', bottom: 16, left: 16, transform: 'scaleY(-1)' }}>
          <GirihCorner />
        </div>
        <div style={{ position: 'absolute', bottom: 16, right: 16, transform: 'scale(-1, -1)' }}>
          <GirihCorner />
        </div>

        {/* Content */}
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '2.5rem' }}>🧠</span>
            <div>
              <p style={{
                fontSize: '0.75rem', color: '#D97706', letterSpacing: '0.15em',
                textTransform: 'uppercase', margin: 0, fontFamily: "'JetBrains Mono', monospace"
              }}>
                Earth Memory Layer — لایه حافظه زمین
              </p>
              <h1 style={{
                fontSize: 'clamp(1.75rem, 4vw, 2.5rem)',
                fontWeight: 800, color: '#FAFAF9', margin: '0.25rem 0 0',
                letterSpacing: '-0.02em', lineHeight: 1.2,
              }}>
                خرد ۵۰۰۰ ساله
                <span style={{ color: '#D97706', margin: '0 0.5rem' }}>·</span>
                کشاورزی پایدار
              </h1>
            </div>
          </div>
          <p style={{ color: '#A7C4D4', fontSize: '1.05rem', maxWidth: 600, lineHeight: 1.7 }}>
            الگوهای آزموده‌شده در گذر هزاره‌ها — از قنات‌های ایران تا چرخ‌های آبی سومر.
            دانشی که تمدن‌ها را در سخت‌ترین اقلیم‌ها پایدار نگه داشت.
          </p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
            <StatBadge label="الگوی تمدنی" value="۲۳" />
            <StatBadge label="قاره" value="۶" />
            <StatBadge label="سال خرد بشری" value="۵۰۰۰" suffix="+" />
          </div>
        </div>
      </section>

      {/* ===== Category Filter — Tabs ===== */}
      <nav style={{
        display: 'flex', flexWrap: 'wrap', gap: '0.5rem',
        marginBottom: '3rem', padding: '0 0.5rem',
      }}>
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.35rem',
              padding: '0.5rem 1rem', borderRadius: '2rem',
              fontSize: '0.8rem', fontWeight: 500,
              border: selectedCategory === cat.id
                ? '1.5px solid #059669'
                : '1.5px solid transparent',
              background: selectedCategory === cat.id
                ? 'linear-gradient(135deg, #ecfdf5, #d1fae5)'
                : '#f5f5f4',
              color: selectedCategory === cat.id ? '#065f46' : '#57534e',
              cursor: 'pointer',
              transition: 'all 200ms cubic-bezier(0.16, 1, 0.3, 1)',
            }}
          >
            <span>{cat.icon}</span>
            {cat.label}
          </button>
        ))}
      </nav>

      {/* ===== Loading State ===== */}
      {loading && (
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem',
        }}>
          {[1,2,3,4,5,6].map(i => (
            <div key={i} style={{
              height: 260, borderRadius: '1rem',
              background: 'linear-gradient(110deg, #f5f5f4 30%, #e7e5e4 50%, #f5f5f4 70%)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 1.5s infinite',
            }} />
          ))}
        </div>
      )}

      {/* ===== Patterns Grid ===== */}
      {!loading && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '1.5rem',
        }}>
          {filtered.map((pattern, idx) => (
            <article
              key={pattern.pattern_id}
              onMouseEnter={() => setHoveredCard(pattern.pattern_id)}
              onMouseLeave={() => setHoveredCard(null)}
              style={{
                background: 'linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)',
                border: hoveredCard === pattern.pattern_id
                  ? '1.5px solid #B45309'
                  : '1px solid rgba(217, 119, 6, 0.2)',
                borderRadius: '1rem',
                padding: '1.75rem',
                position: 'relative',
                overflow: 'hidden',
                cursor: 'pointer',
                transform: hoveredCard === pattern.pattern_id
                  ? 'translateY(-4px)'
                  : 'translateY(0)',
                boxShadow: hoveredCard === pattern.pattern_id
                  ? '0 0 24px rgba(217, 119, 6, 0.25), 0 4px 12px rgba(217, 119, 6, 0.1)'
                  : '0 1px 3px rgba(0,0,0,0.04)',
                transition: 'all 300ms cubic-bezier(0.16, 1, 0.3, 1)',
                animation: `fadeSlideUp 500ms ${idx * 80}ms both cubic-bezier(0.34, 1.56, 0.64, 1)`,
              }}>
                {/* Persian ornamental inner border */}
                <div style={{
                  position: 'absolute', top: 8, left: 8, right: 8, bottom: 8,
                  border: '1px solid rgba(217, 119, 6, 0.12)',
                  borderRadius: '0.75rem', pointerEvents: 'none',
                }} />

                {/* Top row: Civilization + Age Ring */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                  <span style={{
                    fontSize: '0.7rem', fontWeight: 600,
                    background: 'rgba(5, 150, 105, 0.1)',
                    color: '#065f46', padding: '0.2rem 0.6rem', borderRadius: '1rem',
                  }}>
                    {pattern.civilization_fa}
                  </span>

                  {/* Age Ring — tree ring inspired */}
                  <div style={{
                    width: 48, height: 48, borderRadius: '50%',
                    background: `conic-gradient(#059669 0deg, #10b981 ${getAgeDegrees(pattern.age_years)}deg, transparent ${getAgeDegrees(pattern.age_years)}deg)`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    position: 'relative',
                  }}>
                    <div style={{
                      width: 34, height: 34, borderRadius: '50%',
                      background: '#FFFBEB',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '0.65rem', fontWeight: 700, color: '#92400e',
                    }}>
                      {formatAge(pattern.age_years)}
                    </div>
                  </div>
                </div>

                {/* Pattern Name */}
                <h3 style={{
                  fontSize: '1.15rem', fontWeight: 700, color: '#1c1917',
                  margin: '0 0 0.5rem', lineHeight: 1.3,
                }}>
                  {pattern.name_fa}
                </h3>

                {/* Category + Solution */}
                <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                  <span style={{
                    fontSize: '0.65rem', background: '#eff6ff',
                    color: '#1d4ed8', padding: '0.15rem 0.5rem', borderRadius: '1rem',
                    display: 'inline-flex', alignItems: 'center', gap: '0.2rem',
                  }}>
                    <span>{getCategoryIcon(pattern.problem_category)}</span>
                    {getCategoryLabel(pattern.problem_category)}
                  </span>
                </div>

                {/* Climate Zones */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginBottom: '1rem' }}>
                  {pattern.climate_zones?.map(z => (
                    <span key={z} style={{
                      fontSize: '0.6rem', background: '#f5f5f4', color: '#78716c',
                      padding: '0.1rem 0.4rem', borderRadius: '0.25rem',
                      fontFamily: "'JetBrains Mono', monospace",
                    }}>
                      {z}
                    </span>
                  ))}
                </div>

                {/* Score bars — Persian geometric style */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <ScoreBar
                    label="موفقیت تاریخی"
                    value={pattern.success_score}
                    color="#059669"
                  />
                  <ScoreBar
                    label="پایداری زیست‌محیطی"
                    value={pattern.sustainability_index}
                    color="#1E3A5F"
                  />
                </div>

                {/* Hover glow effect */}
                {hoveredCard === pattern.pattern_id && (
                  <div style={{
                    position: 'absolute', inset: 0,
                    background: 'radial-gradient(circle at 50% 0%, rgba(217, 119, 6, 0.08) 0%, transparent 60%)',
                    pointerEvents: 'none', borderRadius: '1rem',
                  }} />
                )}
              </article>
            ))}
          </div>
        )}

      {/* ===== Empty State ===== */}
      {!loading && filtered.length === 0 && (
        <div style={{ textAlign: 'center', padding: '5rem 0' }}>
          <p style={{ fontSize: '4rem', margin: '0 0 1rem', opacity: 0.5 }}>📜</p>
          <p style={{ fontSize: '1.1rem', color: '#78716c', margin: 0 }}>
            الگویی برای این دسته‌بندی یافت نشد
          </p>
          <p style={{ fontSize: '0.85rem', color: '#a8a29e', marginTop: '0.25rem' }}>
            دسته‌بندی دیگری را امتحان کنید
          </p>
        </div>
      )}

      {/* ===== Global Styles (inline for standalone use) ===== */}
      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>
    </div>
  );
};

/* ===== Sub-components ===== */

const StatBadge: React.FC<{ label: string; value: string; suffix?: string }> = ({ label, value, suffix }) => (
  <div style={{
    background: 'rgba(255,255,255,0.12)',
    backdropFilter: 'blur(8px)',
    padding: '0.5rem 1rem',
    borderRadius: '0.75rem',
    textAlign: 'center',
  }}>
    <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FAFAF9', lineHeight: 1.2 }}>
      {value}{suffix && <span style={{ fontSize: '0.9rem', color: '#D97706' }}>{suffix}</span>}
    </div>
    <div style={{ fontSize: '0.7rem', color: '#A7C4D4', marginTop: '0.15rem' }}>{label}</div>
  </div>
);

const ScoreBar: React.FC<{ label: string; value: number; color: string }> = ({ label, value, color }) => (
  <div>
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', marginBottom: '0.2rem' }}>
      <span style={{ color: '#78716c' }}>{label}</span>
      <span style={{ color: '#57534e', fontWeight: 600 }}>{Math.round(value * 100)}٪</span>
    </div>
    <div style={{
      height: 5, borderRadius: '1rem',
      background: '#f5f5f4',
      overflow: 'hidden',
    }}>
      <div style={{
        height: '100%', width: `${Math.round(value * 100)}%`,
        background: `linear-gradient(90deg, ${color}, ${color}dd)`,
        borderRadius: '1rem',
        transition: 'width 800ms cubic-bezier(0.34, 1.56, 0.64, 1)',
      }} />
    </div>
  </div>
);

export default EarthMemoryPage;
