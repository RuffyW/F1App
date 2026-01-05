"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetcher } from "../../lib/api";
import { LoadingSkeleton } from "../../components/LoadingSkeleton";

type Profile = {
  id: string;
  name: string;
  nationality?: string;
  stats?: Record<string, unknown>;
};

export default function TeamsPage() {
  const { data, isLoading } = useQuery<Profile[]>({
    queryKey: ["teams"],
    queryFn: async () => {
      const base = ["teamA", "teamB", "teamC"];
      const profiles = await Promise.all(base.map((id) => fetcher(`/teams/${id}`)));
      return profiles;
    },
    staleTime: 1000 * 60 * 60 * 6,
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Teams</h1>
      {isLoading && <LoadingSkeleton lines={4} />}
      <div className="grid gap-4 md:grid-cols-3">
        {data?.map((team) => (
          <Link key={team.id} href={`/teams/${team.id}`} className="card group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase text-slate-500">{team.nationality}</p>
                <h3 className="text-lg font-semibold group-hover:text-accent transition">
                  {team.name}
                </h3>
              </div>
              <div className="rounded-full bg-accent/10 px-3 py-1 text-xs text-accent">
                Overview
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
