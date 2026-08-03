// apps/web/src/components/inventory/BarcodeGenerator.tsx
import { useState, useRef, useCallback } from "react";
import { Download, RefreshCw } from "lucide-react";
import { useLang } from "../eco/i18n";

interface Props {
  className?: string;
}

export default function BarcodeGenerator({ className = "" }: Props) {
  const { lang } = useLang();
  const [code, setCode] = useState("ECO-" + Date.now().toString(36).toUpperCase().slice(-8));
  const [prefix, setPrefix] = useState("ECO");
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const generateRandom = useCallback(() => {
    setCode(prefix + "-" + Date.now().toString(36).toUpperCase().slice(-8));
  }, [prefix]);

  // Simple code128-style barcode renderer
  const BARCODE_PATTERNS: Record<string, string> = {
    "0": "00110", "1": "10001", "2": "01001", "3": "11000", "4": "00101",
    "5": "10100", "6": "01100", "7": "00011", "8": "10010", "9": "01010",
  };

  // Basic barcode render (Code 39 style approximation)
  const renderBarcode = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = 400;
    canvas.height = 150;
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const text = code.replace(/[^A-Z0-9\-]/g, "").toUpperCase();
    if (text.length === 0) return;

    // Generate pattern: start + encoded + stop
    const patterns: string[] = [];
    patterns.push("1010"); // start marker
    for (const ch of text) {
      const idx = ch.charCodeAt(0) % 37;
      const bin = idx.toString(2).padStart(6, "0");
      patterns.push(bin);
    }
    patterns.push("1101"); // stop marker

    const allBits = patterns.join("");

    const barWidth = Math.max(1, Math.floor(canvas.width / (allBits.length + 10)));
    const totalWidth = allBits.length * barWidth;
    const startX = (canvas.width - totalWidth) / 2;
    const barY = 10;
    const barH = 100;

    ctx.fillStyle = "#000000";
    for (let i = 0; i < allBits.length; i++) {
      if (allBits[i] === "1") {
        ctx.fillRect(startX + i * barWidth, barY, barWidth, barH);
      }
    }

    // Text label
    ctx.fillStyle = "#000000";
    ctx.font = "bold 16px monospace";
    ctx.textAlign = "center";
    ctx.fillText(text, canvas.width / 2, barY + barH + 25);
  }, [code]);

  useState(() => { renderBarcode(); });

  const downloadBarcode = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const link = document.createElement("a");
    link.download = `barcode-${code}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  };

  return (
    <div className={className}>
      <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h3 className="mb-3 font-bold text-stone-900 dark:text-stone-100">
          {lang === "fa" ? "تولید بارکد" : "Barcode Generator"}
        </h3>

        <div className="mb-4 flex gap-2">
          <input
            type="text"
            value={prefix}
            onChange={(e) => setPrefix(e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, ""))}
            placeholder="Prefix"
            className="w-24 rounded-xl border border-stone-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
          />
          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 rounded-xl border border-stone-200 bg-white px-3 py-2 font-mono text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-stone-100"
          />
          <button
            onClick={generateRandom}
            className="rounded-xl border border-stone-200 bg-white px-3 py-2 text-stone-600 hover:bg-stone-50 dark:border-slate-700 dark:bg-slate-800 dark:text-stone-300"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>

        <div className="rounded-xl bg-stone-50 p-3 dark:bg-slate-900">
          <canvas ref={canvasRef} className="w-full" style={{ maxWidth: 400, margin: "0 auto" }} />
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={downloadBarcode}
            className="flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-bold text-white hover:bg-emerald-700 transition-colors"
          >
            <Download className="h-4 w-4" />
            {lang === "fa" ? "دانلود" : "Download"}
          </button>
        </div>
      </div>
    </div>
  );
}
