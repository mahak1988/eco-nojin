import { useForm } from "react-hook-form";
import axios from "axios";
import { useWebSocket } from "../hooks/useWebSocket";
import { useState } from "react";

type FormValues = {
  query: string;
  region: string;
  crop: string;
  area: number;
  rainfall: number;
  pricePerTon: number;
  waterCost: number;
  laborCost: number;
};

export default function SimulatorPanel() {
  const { register, handleSubmit, reset } = useForm<FormValues>({
    defaultValues: {
      query: "تحلیل جامع اقتصادی و محیط‌زیستی",
      region: "خراسان",
      crop: "گندم",
      area: 10,
      rainfall: 250,
      pricePerTon: 12000,
      waterCost: 1500000,
      laborCost: 2000000,
    }
  });
  const { connect } = useWebSocket();
  const [loading, setLoading] = useState(false);

  const onSubmit = async (data: FormValues) => {
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/api/v1/analyze/stream", {
        query: data.query,
        region: data.region
      });
      connect(res.data.session_id);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="p-4 bg-slate-800 rounded-xl text-slate-100 space-y-3">
      <h3 className="text-lg font-bold text-sky-400">🧮 شبیه‌ساز اقتصادی-محیطی</h3>
      <input {...register("query")} className="w-full p-2 rounded bg-slate-700" placeholder="درخواست شما..." />
      <div className="grid grid-cols-2 gap-2">
        <select {...register("region")} className="p-2 rounded bg-slate-700">
          <option value="خراسان">خراسان</option>
          <option value="گرگان">گرگان</option>
          <option value="فارس">فارس</option>
        </select>
        <input {...register("crop")} className="p-2 rounded bg-slate-700" placeholder="محصول" />
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <label>سطح (هکتار) <input {...register("area", {valueAsNumber: true})} type="number" className="w-full p-1 rounded bg-slate-700" /></label>
        <label>بارش (mm) <input {...register("rainfall", {valueAsNumber: true})} type="number" className="w-full p-1 rounded bg-slate-700" /></label>
        <label>قیمت بازار (تومان/تن) <input {...register("pricePerTon", {valueAsNumber: true})} type="number" className="w-full p-1 rounded bg-slate-700" /></label>
        <label>هزینه آب (تومان) <input {...register("waterCost", {valueAsNumber: true})} type="number" className="w-full p-1 rounded bg-slate-700" /></label>
      </div>
      <button type="submit" disabled={loading} className="w-full bg-sky-600 hover:bg-sky-500 py-2 rounded font-medium transition">
        {loading ? "در حال اتصال..." : "🚀 اجرای شبیه‌سازی"}
      </button>
    </form>
  );
}