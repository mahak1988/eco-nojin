"use client";

import { useState } from "react";
import { MainLayout } from "@/components/layout/main-layout";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { simulationService } from "@/lib/api";
import { useTranslations } from "next-intl";
import { MediaHero } from "@/components/ui/media-hero";
import { motion } from "framer-motion";
import { FlaskConical } from "lucide-react";

export default function SimulationPage() {
  const t = useTranslations();
  const [result, setResult] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  const runRothc = async () => {
    setLoading(true);
    try {
      const res = await simulationService.rothc({
        initial_soc: 50,
        clay_percent: 28,
        mean_temp_c: 16,
        annual_rain_mm: 280,
        years: 5,
      });
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  const runAqua = async () => {
    setLoading(true);
    try {
      const res = await simulationService.aquacrop({
        crop: "wheat",
        area_ha: 10,
        irrigation_mm: 300,
        rainfall_mm: 250,
      });
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-8 page-enter">
        <MediaHero
          title="شبیه‌ساز علمی"
          subtitle="RothC · AquaCrop · Coupling — فرمول‌های جهانی"
          imageSrc="https://images.unsplash.com/photo-1574943326832-8f8a0d149f73?w=1200&q=80"
          accentColor="#14b8a6"
        />
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="border-slate-800 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-100">
                <FlaskConical className="h-5 w-5 text-teal-400" />
                RothC (کربن خاک)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <FormField id="soc" label="SOC اولیه" defaultValue="50" readOnly />
              <Button onClick={runRothc} disabled={loading} className="w-full bg-teal-600">
                {t("simulation.run")}
              </Button>
            </CardContent>
          </Card>
          <Card className="border-slate-800 bg-slate-900/50">
            <CardHeader>
              <CardTitle className="text-slate-100">AquaCrop</CardTitle>
            </CardHeader>
            <CardContent>
              <Button onClick={runAqua} disabled={loading} className="w-full bg-amber-600">
                {t("simulation.run")}
              </Button>
            </CardContent>
          </Card>
        </div>
        {result && (
          <motion.pre
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xs p-4 rounded-xl bg-slate-950 border border-slate-800 overflow-auto max-h-96"
          >
            {JSON.stringify(result, null, 2)}
          </motion.pre>
        )}
      </div>
    </MainLayout>
  );
}
