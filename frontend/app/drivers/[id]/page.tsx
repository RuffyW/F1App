"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetcher } from "../../../lib/api";
import { LoadingSkeleton } from "../../../components/LoadingSkeleton";
import { ResultsTable } from "../../../components/ResultsTable";

type Profile = {
  id: string;
  name: string;
  team?: string;
  nationality?: string;
  stats?: Record<string, unknown>;
  recent_results?: { position: number; driver: string; team: string; time?: string }[];
};

export default function DriverProfilePage() {
  const params = useParams<{ id: string }>();
  const driverId = params?.id;
  const { data, isLoading } = useQuery<Profile>({
    queryKey: ["driver", driverId],
    queryFn: () => fetcher(`/drivers/${driverId}`),
    enabled: Boolean(driverId),
    staleTime: 1000 * 60 * 60 * 6,
  });

  if (isLoading || !data) {
    return <LoadingSkeleton lines={6} />;
  }

  return (
    <div className="space-y-4">
      <div className="card flex items-center justify-between">
        <div>
          <p className="text-xs uppercase text-slate-500">{data.nationality}</p>
          <h1 className="text-2xl font-semibold">{data.name}</h1>
          <p className="text-sm text-slate-600">{data.team}</p>
        </div>
        <div className="rounded-full bg-accent/10 px-3 py-1 text-xs text-accent">
          Season stats
        </div>
      </div>

      {data.recent_results && (
        <ResultsTable
          title="Recent results"
          rows={data.recent_results.map((result) => ({
            position: result.position,
            driver: result.driver,
            team: result.team,
            time: result.time,
          }))}
        />
      )}
    </div>
  );
}
