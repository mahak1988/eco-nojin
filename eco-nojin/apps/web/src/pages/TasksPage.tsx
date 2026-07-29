import { FormEvent, useCallback, useEffect, useState } from "react";
import { CheckSquare, Loader2, Plus } from "lucide-react";

interface Task {
  id: number;
  title: string;
  category: string;
  priority: string;
  status: string;
  due_date?: string | null;
  assigned_to?: string | null;
  estimated_hours?: number | null;
  description?: string | null;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    category: "field",
    priority: "medium",
    status: "todo",
    due_date: "",
    assigned_to: "",
    estimated_hours: "",
    description: "",
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/tasks?page=1&size=50", {
        credentials: "include",
        headers: { Accept: "application/json" },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const j = await res.json();
      setTasks(j.data || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const res = await fetch("/api/v1/tasks", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        title: form.title,
        category: form.category,
        priority: form.priority,
        status: form.status,
        due_date: form.due_date || null,
        assigned_to: form.assigned_to || null,
        estimated_hours: form.estimated_hours ? Number(form.estimated_hours) : null,
        description: form.description || null,
      }),
    });
    if (!res.ok) {
      setError(`HTTP ${res.status}`);
      return;
    }
    setShowForm(false);
    await load();
  }

  const priorityColor: Record<string, string> = {
    high: "bg-rose-50 text-rose-700",
    medium: "bg-amber-50 text-amber-800",
    low: "bg-stone-100 text-stone-600",
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-5 sm:p-8">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-violet-50">
            <CheckSquare className="h-5 w-5 text-violet-700" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-stone-800">Farm tasks</h1>
            <p className="text-sm text-stone-500">Priority · due date · assignment</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setShowForm((v) => !v)}
          className="inline-flex items-center gap-1 rounded-xl bg-violet-600 px-3 py-2 text-sm font-bold text-white"
        >
          <Plus className="h-4 w-4" /> Task
        </button>
      </div>

      {error && <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

      {showForm && (
        <form onSubmit={onCreate} className="grid gap-3 rounded-2xl border bg-white p-5 sm:grid-cols-2">
          <label className="text-sm sm:col-span-2">
            Title *
            <input
              required
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              className="mt-1 w-full rounded-xl border px-3 py-2"
            />
          </label>
          <label className="text-sm">
            Category
            <select
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              className="mt-1 w-full rounded-xl border px-3 py-2"
            >
              {["field", "irrigation", "pest", "harvest", "maintenance", "general"].map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            Priority
            <select
              value={form.priority}
              onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
              className="mt-1 w-full rounded-xl border px-3 py-2"
            >
              {["low", "medium", "high"].map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            Due date
            <input
              type="date"
              value={form.due_date}
              onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))}
              className="mt-1 w-full rounded-xl border px-3 py-2"
            />
          </label>
          <label className="text-sm">
            Assigned to
            <input
              value={form.assigned_to}
              onChange={(e) => setForm((f) => ({ ...f, assigned_to: e.target.value }))}
              className="mt-1 w-full rounded-xl border px-3 py-2"
            />
          </label>
          <label className="text-sm">
            Est. hours
            <input
              type="number"
              min={0}
              step="0.5"
              value={form.estimated_hours}
              onChange={(e) => setForm((f) => ({ ...f, estimated_hours: e.target.value }))}
              className="mt-1 w-full rounded-xl border px-3 py-2"
            />
          </label>
          <label className="text-sm sm:col-span-2">
            Description
            <textarea
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              rows={2}
              className="mt-1 w-full rounded-xl border px-3 py-2"
            />
          </label>
          <button type="submit" className="sm:col-span-2 rounded-xl bg-violet-600 py-2.5 text-sm font-bold text-white">
            Save task
          </button>
        </form>
      )}

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-violet-600" />
        </div>
      ) : (
        <ul className="space-y-2">
          {tasks.map((t) => (
            <li key={t.id} className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border bg-white p-4">
              <div>
                <p className="font-bold text-stone-800">{t.title}</p>
                <p className="text-xs text-stone-500">
                  {t.category} · due {t.due_date || "—"} · {t.assigned_to || "unassigned"}
                  {t.estimated_hours != null ? ` · ${t.estimated_hours}h` : ""}
                </p>
              </div>
              <div className="flex gap-2">
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ${priorityColor[t.priority] || ""}`}>
                  {t.priority}
                </span>
                <span className="rounded-full bg-violet-50 px-2 py-0.5 text-[11px] font-bold text-violet-800">
                  {t.status}
                </span>
              </div>
            </li>
          ))}
          {tasks.length === 0 && <p className="py-8 text-center text-stone-500">No tasks</p>}
        </ul>
      )}
    </div>
  );
}
