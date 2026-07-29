// apps/web/src/pages/JournalEntriesPage.tsx
import { useMemo, useState } from "react";
import { BookOpen, Download, Plus, Search } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { JournalStats } from "../components/journal/JournalStats";
import { JournalTable } from "../components/journal/JournalTable";
import { NewEntryModal, type NewEntryData } from "../components/journal/NewEntryModal";
import { JR_STR, accountText, type JrLang } from "../components/journal/journalI18n";
import {
  INITIAL_ENTRIES, ACCOUNT_KEYS, nextEntryId, entryTotals, journalToCSV, downloadCSV,
  type JournalEntry, type SortKey, type SortDir,
} from "../components/journal/journalData";

export default function JournalEntriesPage() {
  const { lang } = useLang();
  const s = JR_STR[lang as JrLang];

  const [entries, setEntries] = useState<JournalEntry[]>(INITIAL_ENTRIES);
  const [search, setSearch] = useState("");
  const [accountFilter, setAccountFilter] = useState<string>("all");
  const [sortKey, setSortKey] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [modalOpen, setModalOpen] = useState(false);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return entries.filter((e) => {
      const matchQ = q === "" ||
        e.memo.toLowerCase().includes(q) ||
        e.id.toLowerCase().includes(q) ||
        e.lines.some((l) => accountText(s, l.account).toLowerCase().includes(q) || l.description.toLowerCase().includes(q));
      const matchAcc = accountFilter === "all" || e.lines.some((l) => l.account === accountFilter);
      return matchQ && matchAcc;
    });
  }, [entries, search, accountFilter, lang]); // eslint-disable-line react-hooks/exhaustive-deps

  const sorted = useMemo(() => {
    const arr = [...filtered];
    arr.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "date") cmp = +new Date(a.date) - +new Date(b.date);
      else cmp = entryTotals(a).debit - entryTotals(b).debit;
      return sortDir === "asc" ? cmp : -cmp;
    });
    return arr;
  }, [filtered, sortKey, sortDir]);

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir("desc"); }
  };

  const createEntry = (data: NewEntryData) =>
    setEntries((prev) => [
      { id: nextEntryId(prev), date: data.date, memo: data.memo,
        lines: data.lines.map((l, i) => ({ id: `l${i + 1}`, account: l.account, description: l.description, debit: l.debit, credit: l.credit })) },
      ...prev,
    ]);

  const headers = s.csvHeaders.split(",");
  const exportAll = () => downloadCSV("journal-entries.csv", journalToCSV(sorted, headers));
  const exportOne = (e: JournalEntry) => downloadCSV(`${e.id}.csv`, journalToCSV([e], headers));

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      {/* header */}
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15">
              <BookOpen className="h-5 w-5 text-green-700" />
            </div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={exportAll} className="inline-flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-bold text-stone-700 hover:bg-stone-50">
              <Download className="h-4 w-4" />{s.exportAll}
            </button>
            <button onClick={() => setModalOpen(true)} className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Plus className="h-4 w-4" />{s.newEntry}
            </button>
          </div>
        </div>
      </SectionReveal>

      {/* KPIs (derived) */}
      <JournalStats entries={entries} strings={s} lang={lang as JrLang} />

      {/* toolbar */}
      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <select value={accountFilter} onChange={(e) => setAccountFilter(e.target.value)}
            className="rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15">
            <option value="all">{s.filterAccount}</option>
            {ACCOUNT_KEYS.map((k) => <option key={k} value={k}>{accountText(s, k)}</option>)}
          </select>
        </div>
      </SectionReveal>

      {/* table */}
      <SectionReveal delay={120}>
        <JournalTable entries={sorted} strings={s} lang={lang as JrLang}
          sortKey={sortKey} sortDir={sortDir} onSort={onSort} onDownloadOne={exportOne} />
      </SectionReveal>

      {/* modal */}
      <NewEntryModal open={modalOpen} strings={s} lang={lang as JrLang}
        onClose={() => setModalOpen(false)} onCreate={createEntry} />
    </div>
  );
}