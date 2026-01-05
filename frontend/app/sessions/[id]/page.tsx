"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { ResultsTable } from "../../../components/ResultsTable";
import { fetcher } from "../../../lib/api";
import { LoadingSkeleton } from "../../../components/LoadingSkeleton";

const tabs = ["Results", "Stints", "Tyres", "Pitstops"];

export default function SessionViewPage() {
  const params = useParams<{ id: string }>();
  const [tab, setTab] = useState("Results");

  const sessionId = params?.id;
  const endpoint = useMemo(() => {
    switch (tab) {
      case "Stints":
        return "stints";
      case "Tyres":
        return "tyres";
      case "Pitstops":
        return "pitstops";
      default:
        return "classification";
    }
  }, [tab]);

  const { data, isLoading } = useQuery({
    queryKey: ["session", sessionId, endpoint],
    queryFn: () => fetcher(`/sessions/${sessionId}/${endpoint}`),
    enabled: Boolean(sessionId),
    staleTime: 1000 * 60 * 10,
  });

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {tabs.map((item) => (
          <button
            key={item}
            onClick={() => setTab(item)}
            className={`rounded-full px-4 py-2 text-sm transition ${
              tab === item ? "bg-accent text-white shadow-soft" : "bg-surface text-slate-700"
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {isLoading && <LoadingSkeleton lines={5} />}

      {!isLoading && data && (
        <ResultsTable
          title={`${tab} for ${sessionId}`}
          rows={data}
        />
      )}
    </div>
  );
}
