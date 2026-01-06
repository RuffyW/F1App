"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ResultsTable } from "../../components/ResultsTable";
import { fetcher } from "../../lib/api";
import { LoadingSkeleton } from "../../components/LoadingSkeleton";

type Standing = { position: number; name: string; team?: string; points: number };
type Payload = { round: number; last_updated: string; entries: Standing[] };

export default function StandingsPage() {
  const [tab, setTab] = useState<"drivers" | "teams">("drivers");
  const { data, isLoading } = useQuery<Payload>({
    queryKey: ["standings", tab],
    queryFn: () => fetcher(`/standings/${tab}`),
    staleTime: 1000 * 60 * 30,
  });

  const rows =
    data?.entries.map((entry) => ({
      position: entry.position,
      driver: entry.name,
      team: entry.team || (tab === "teams" ? entry.name : "—"),
      time: `${entry.points} pts`,
    })) || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {["drivers", "teams"].map((item) => (
            <button
              key={item}
              onClick={() => setTab(item as "drivers" | "teams")}
              className={`rounded-full px-4 py-2 text-sm transition ${
                tab === item ? "bg-accent text-white" : "bg-surface text-slate-700"
              }`}
            >
              {item === "drivers" ? "Drivers" : "Teams"}
            </button>
          ))}
        </div>
        <div className="text-xs text-slate-500">
          Round {data?.round ?? "—"} · Updated{" "}
          {data?.last_updated
            ? new Date(data.last_updated).toLocaleString()
            : "soon"}
        </div>
      </div>

      {isLoading && <LoadingSkeleton lines={5} />}

      {!isLoading && data && (
        <ResultsTable title={`${tab} standings`} rows={rows} />
      )}
    </div>
  );
}
