"use client";

import { useCallback, useState } from "react";
import { ModuleDashboard } from "@/components/modules/ModuleDashboard";
import { MODULE_REGISTRY } from "@/lib/modules";
import { farmerService } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function FarmersPage() {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchFarmers = useCallback(async () => {
    const res = await farmerService.list(0, 50);
    return {
      stats: [
        { title: "کل کشاورزان", value: res.total },
        { title: "در لیست", value: res.farmers.length },
        { title: "فعال", value: res.farmers.length },
        { title: "API", value: 1 },
      ],
      rows: res.farmers,
      chartData: res.farmers.map((f) => ({ id: f.id, name: f.name })),
    };
  }, [refreshKey]);

  const handleCreate = async () => {
    if (!name.trim()) return;
    await farmerService.create({ name, phone: phone || undefined });
    setName("");
    setPhone("");
    setRefreshKey((k) => k + 1);
  };

  return (
    <ModuleDashboard
      key={refreshKey}
      config={MODULE_REGISTRY.farmers}
      fetchData={fetchFarmers}
      onNew={() => document.getElementById("farmer-form")?.scrollIntoView({ behavior: "smooth" })}
    >
      <div id="farmer-form" className="flex flex-wrap gap-2 p-4 border border-slate-800 rounded-xl bg-slate-900/50">
        <Input
          placeholder="نام کشاورز"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="flex-1 min-w-[140px] border-slate-700"
        />
        <Input
          placeholder="تلفن"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          className="w-40 border-slate-700"
        />
        <Button onClick={handleCreate} className="bg-emerald-600 hover:bg-emerald-500">
          ثبت کشاورز
        </Button>
      </div>
    </ModuleDashboard>
  );
}
