/**
 * ============================================================================
 *  AgricultureSchools — directory of agriculture schools (i18n-aware)
 * ============================================================================
 */

import { useMemo, useState } from "react";

import { useLanguage } from "@/hooks/useLanguage";
import { formatNumber } from "@/lib/i18n-utils";

// ---------------------------------------------------------------------------
// Types + mock data
// ---------------------------------------------------------------------------

interface School {
  id: string;
  nameKey: string;
  provinceKey: string;
  cityKey: string;
  type: "university" | "institute" | "training-center";
  established: number;
  studentsCount: number;
  fieldsKeys: readonly string[];
  website: string;
  logo: string;
}

const SCHOOLS: readonly School[] = [
  {
    id: "s-1",
    nameKey: "schools.s1Name",
    provinceKey: "schools.s1Province",
    cityKey: "schools.s1City",
    type: "university",
    established: 1963,
    studentsCount: 4200,
    fieldsKeys: ["schools.fieldIrrigation", "schools.fieldSoil", "schools.fieldHorticulture", "schools.fieldPlantProtection"],
    website: "https://abf.ut.ac.ir",
    logo: "\u{1F393}",
  },
  {
    id: "s-2",
    nameKey: "schools.s2Name",
    provinceKey: "schools.s2Province",
    cityKey: "schools.s2City",
    type: "university",
    established: 1957,
    studentsCount: 6800,
    fieldsKeys: ["schools.fieldForestry", "schools.fieldEnvironment", "schools.fieldFisheries", "schools.fieldIrrigation"],
    website: "https://gau.ac.ir",
    logo: "\u{1F332}",
  },
  {
    id: "s-3",
    nameKey: "schools.s3Name",
    provinceKey: "schools.s3Province",
    cityKey: "schools.s3City",
    type: "university",
    established: 1955,
    studentsCount: 3100,
    fieldsKeys: ["schools.fieldAgronomy", "schools.fieldHorticulture", "schools.fieldWaterEng", "schools.fieldPlantProtection"],
    website: "https://agri.cu.ac.ir",
    logo: "\u{1F33E}",
  },
  {
    id: "s-4",
    nameKey: "schools.s4Name",
    provinceKey: "schools.s4Province",
    cityKey: "schools.s4City",
    type: "institute",
    established: 2011,
    studentsCount: 450,
    fieldsKeys: ["schools.fieldOrganic", "schools.fieldPermaculture", "schools.fieldGreenEcon"],
    website: "https://saii.ir",
    logo: "\u{1F331}",
  },
  {
    id: "s-5",
    nameKey: "schools.s5Name",
    provinceKey: "schools.s5Province",
    cityKey: "schools.s5City",
    type: "training-center",
    established: 2015,
    studentsCount: 220,
    fieldsKeys: ["schools.fieldOrganic", "schools.fieldBiodynamic", "schools.fieldLowTill"],
    website: "https://sac-esf.ir",
    logo: "\u{1F33F}",
  },
  {
    id: "s-6",
    nameKey: "schools.s6Name",
    provinceKey: "schools.s6Province",
    cityKey: "schools.s6City",
    type: "university",
    established: 1973,
    studentsCount: 3900,
    fieldsKeys: ["schools.fieldAgronomy", "schools.fieldIrrigation", "schools.fieldHorticulture", "schools.fieldSeedTech"],
    website: "https://ag.um.ac.ir",
    logo: "\u{1F33B}",
  },
] as const;

// ---------------------------------------------------------------------------
// Subcomponents
// ---------------------------------------------------------------------------

function FilterBar({
  search, province, onSearch, onProvince, provinces,
}: {
  search: string;
  province: string;
  onSearch: (v: string) => void;
  onProvince: (v: string) => void;
  provinces: readonly string[];
}): JSX.Element {
  const { t, dir } = useLanguage();
  return (
    <div dir={dir} className="flex flex-col gap-3 sm:flex-row">
      <div className="relative flex-1">
        <input
          type="search"
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          placeholder={t("agricultureSchools.searchPlaceholder")}
          className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 pe-10 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        />
        <svg
          className="pointer-events-none absolute end-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <select
        value={province}
        onChange={(e) => onProvince(e.target.value)}
        className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
        aria-label={t("hydrology.filterProvince")}
      >
        <option value="all">{t("hydrology.allProvinces")}</option>
        {provinces.map((p) => (<option key={p} value={p}>{p}</option>))}
      </select>
    </div>
  );
}

function SchoolCard({ school }: { school: School }): JSX.Element {
  const { t, dir, language } = useLanguage();
  return (
    <article dir={dir} className="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5 transition hover:border-emerald-200 hover:shadow-sm">
      <div className="flex items-start gap-4">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-2xl">
          {school.logo}
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold leading-6 text-gray-900">{t(school.nameKey)}</h3>
          <p className="mt-0.5 text-xs text-gray-500">
            {t(`agricultureSchools.types.${school.type}`)} \u2022 {t(school.cityKey)}\u060C {t(school.provinceKey)}
          </p>
        </div>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-3 text-xs">
        <div>
          <dt className="text-gray-500">{t("agricultureSchools.established")}</dt>
          <dd className="mt-0.5 font-medium text-gray-900">{formatNumber(school.established, language)}</dd>
        </div>
        <div>
          <dt className="text-gray-500">{t("agricultureSchools.studentsCount")}</dt>
          <dd className="mt-0.5 font-medium text-gray-900">
            {formatNumber(school.studentsCount, language)} {t("agricultureSchools.students")}
          </dd>
        </div>
      </dl>

      <div className="mt-4">
        <p className="text-xs text-gray-500">{t("agricultureSchools.mainFields")}</p>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {school.fieldsKeys.map((f) => (
            <span key={f} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700">{t(f)}</span>
          ))}
        </div>
      </div>

      <a
        href={school.website}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-5 inline-flex items-center justify-center rounded-lg border border-emerald-600 px-4 py-2 text-xs font-medium text-emerald-700 transition hover:bg-emerald-50"
      >
        {t("agricultureSchools.visitWebsite")}
      </a>
    </article>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function AgricultureSchools(): JSX.Element {
  const { t, dir } = useLanguage();
  const [search, setSearch] = useState("");
  const [province, setProvince] = useState("all");

  const provinces = useMemo(
    () => [...new Set(SCHOOLS.map((s) => t(s.provinceKey)))].sort(),
    [t],
  );

  const filtered = useMemo(() => {
    return SCHOOLS.filter((s) => {
      if (search) {
        const q = search.toLowerCase();
        if (!t(s.nameKey).toLowerCase().includes(q) && !t(s.cityKey).toLowerCase().includes(q)) return false;
      }
      if (province !== "all" && t(s.provinceKey) !== province) return false;
      return true;
    });
  }, [search, province, t]);

  return (
    <div dir={dir} className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("agricultureSchools.title")}</h1>
        <p className="mt-1 text-sm text-gray-600">{t("agricultureSchools.subtitle")}</p>
      </header>

      <div className="mb-6">
        <FilterBar
          search={search}
          province={province}
          onSearch={setSearch}
          onProvince={setProvince}
          provinces={provinces}
        />
      </div>

      {filtered.length === 0 ? (
        <div dir={dir} className="rounded-xl border border-dashed border-gray-300 p-12 text-center">
          <div className="text-4xl">🔍</div>
          <h3 className="mt-3 text-base font-semibold text-gray-900">{t("agricultureSchools.noResults")}</h3>
          <p className="mt-1 text-sm text-gray-600">{t("agricultureSchools.noResultsDescription")}</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((school) => (
            <SchoolCard key={school.id} school={school} />
          ))}
        </div>
      )}
    </div>
  );
}