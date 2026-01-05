"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetcher } from "../../../lib/api";
import { LoadingSkeleton } from "../../../components/LoadingSkeleton";
import { ResultsTable } from "../../../components/ResultsTable";

type Profile = {
  id: string;
  name: string;
  nationality?: string;
  stats?: Record<string, unknown>;
  recent_results?: { position: number; driver: string; team: string; time?: string }[];
};

export default function TeamProfilePage() {
  const params = useParams<{ id: string }>();
  const teamId = params?.id;
  const { data, isLoading } = useQuery<Profile>({
    queryKey: ["team", teamId],
    queryFn: () => fetcher(`/teams/${teamId}`),
    enabled: Boolean(teamId),
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
        </div>
        <div className="rounded-full bg-accent/10 px-3 py-1 text-xs text-accent">
          Team stats
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
