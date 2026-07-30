import { FormEvent, useState } from "react";
import { X, Loader2 } from "lucide-react";

export type WalletAction = "send" | "receive" | "stake";

interface Props {
  action: WalletAction;
  onClose: () => void;
  balance: number;
  onSend: (to: string, amount: number) => Promise<void> | void;
  onStake: (amount: number, tierId: number) => Promise<void> | void;
  address: string;
  labels: {
    send: string;
    receive: string;
    stake: string;
    to: string;
    amount: string;
    tier: string;
    submit: string;
    cancel: string;
    yourAddress: string;
    copied: string;
  };
}

export function WalletActionsModal({
  action,
  onClose,
  balance,
  onSend,
  onStake,
  address,
  labels,
}: Props) {
  const [to, setTo] = useState("");
  const [amount, setAmount] = useState("");
  const [tier, setTier] = useState(1);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const title =
    action === "send" ? labels.send : action === "receive" ? labels.receive : labels.stake;

  async function submit(e: FormEvent) {
    e.preventDefault();
    const n = Number(amount);
    if (!Number.isFinite(n) || n <= 0) return;
    if (n > balance && action !== "receive") {
      setMsg("!");
      return;
    }
    setBusy(true);
    setMsg(null);
    try {
      if (action === "send") await onSend(to || "0xPeer", n);
      if (action === "stake") await onStake(n, tier);
      onClose();
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "error");
    } finally {
      setBusy(false);
    }
  }

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(address);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center bg-stone-900/40 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-3xl border border-stone-200 bg-white p-5 shadow-2xl">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-display text-xl text-stone-800">{title}</h3>
          <button type="button" onClick={onClose} className="rounded-lg p-1 hover:bg-stone-100">
            <X className="h-5 w-5" />
          </button>
        </div>

        {action === "receive" ? (
          <div className="space-y-3">
            <p className="text-xs text-stone-500">{labels.yourAddress}</p>
            <p className="break-all rounded-xl bg-stone-50 p-3 font-mono text-xs">{address}</p>
            <button
              type="button"
              onClick={() => void copy()}
              className="w-full rounded-xl bg-emerald-600 py-2.5 text-sm font-bold text-white"
            >
              {copied ? labels.copied : labels.yourAddress}
            </button>
          </div>
        ) : (
          <form onSubmit={(e) => void submit(e)} className="space-y-3">
            {action === "send" && (
              <label className="block text-sm">
                <span className="font-medium text-stone-600">{labels.to}</span>
                <input
                  value={to}
                  onChange={(e) => setTo(e.target.value)}
                  className="mt-1 w-full rounded-xl border px-3 py-2 font-mono text-sm"
                  placeholder="0x…"
                />
              </label>
            )}
            <label className="block text-sm">
              <span className="font-medium text-stone-600">{labels.amount}</span>
              <input
                type="number"
                min={0}
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="mt-1 w-full rounded-xl border px-3 py-2 text-sm"
              />
            </label>
            {action === "stake" && (
              <label className="block text-sm">
                <span className="font-medium text-stone-600">{labels.tier}</span>
                <select
                  value={tier}
                  onChange={(e) => setTier(Number(e.target.value))}
                  className="mt-1 w-full rounded-xl border px-3 py-2 text-sm"
                >
                  {[1, 2, 3].map((id) => (
                    <option key={id} value={id}>
                      Tier {id}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {msg && <p className="text-sm text-rose-600">{msg}</p>}
            <div className="flex gap-2">
              <button type="button" onClick={onClose} className="flex-1 rounded-xl border py-2.5 text-sm font-bold">
                {labels.cancel}
              </button>
              <button
                type="submit"
                disabled={busy}
                className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 py-2.5 text-sm font-bold text-white disabled:opacity-60"
              >
                {busy && <Loader2 className="h-4 w-4 animate-spin" />}
                {labels.submit}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
