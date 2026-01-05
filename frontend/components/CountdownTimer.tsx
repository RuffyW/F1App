"use client";

import { useEffect, useState } from "react";

type Props = {
  target: string;
  label?: string;
};

export function CountdownTimer({ target, label }: Props) {
  const [remaining, setRemaining] = useState<string>("");

  useEffect(() => {
    const targetDate = new Date(target).getTime();
    const interval = setInterval(() => {
      const diff = targetDate - Date.now();
      if (diff <= 0) {
        setRemaining("Live now");
        clearInterval(interval);
        return;
      }
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / (1000 * 60)) % 60);
      setRemaining(`${days}d ${hours}h ${minutes}m`);
    }, 1000);
    return () => clearInterval(interval);
  }, [target]);

  return (
    <div className="card flex items-center justify-between gap-4">
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500">
          {label || "Next session starts in"}
        </p>
        <p className="text-3xl font-semibold text-slate-900">{remaining}</p>
      </div>
      <div className="rounded-full bg-accent/10 px-4 py-2 text-sm font-medium text-accent">
        {new Date(target).toLocaleString()}
      </div>
    </div>
  );
}
