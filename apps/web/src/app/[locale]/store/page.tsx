"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";
import { api } from "@/lib/api";
import { FormField } from "@/components/ui/form-field";
import { Button } from "@/components/ui/button";

const storeApi = {
  list: () => api.get<{ items: Array<Record<string, unknown>>; total: number }>("/api/v1/store/"),
  create: (body: unknown) => api.post("/api/v1/store/", body),
};

export default function StorePage() {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("0");
  const qc = useQueryClient();

  const createMut = useMutation({
    mutationFn: storeApi.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["store"] });
      setShowForm(false);
      setName("");
    },
  });

  return (
    <ModuleDashboard
      config={MODULE_REGISTRY.store}
      onNew={() => setShowForm(true)}
      fetchData={async () => {
        const res = await storeApi.list();
        return {
          stats: [
            { title: "محصولات", value: res.total },
            { title: "فعال", value: res.items.length },
            { title: "API", value: 1 },
            { title: "فروشگاه", value: 1 },
          ],
          rows: res.items,
          chartData: res.items,
        };
      }}
    >
      {showForm && (
        <form
          className="grid sm:grid-cols-3 gap-3 p-4 border border-slate-800 rounded-xl"
          onSubmit={(e) => {
            e.preventDefault();
            createMut.mutate({ name, price: parseFloat(price), status: "active", stock: 10 });
          }}
        >
          <FormField id="n" label="نام" value={name} onChange={(e) => setName(e.target.value)} required />
          <FormField id="p" label="قیمت" value={price} onChange={(e) => setPrice(e.target.value)} />
          <Button type="submit" className="self-end bg-orange-600" disabled={createMut.isPending}>
            ثبت محصول
          </Button>
        </form>
      )}
    </ModuleDashboard>
  );
}
