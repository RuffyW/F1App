"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetcher } from "../../lib/api";
import { LoadingSkeleton } from "../../components/LoadingSkeleton";

type Profile = {
  id: string;
  name: string;
  team?: string;
  nationality?: string;
  stats?: Record<string, unknown>;
};

export default function DriversPage() {
  const { data, isLoading } = useQuery<Profile[]>({
    queryKey: ["drivers"],
    queryFn: async () => {
      const base = ["drv1", "drv2", "drv3"];
      const profiles = await Promise.all(base.map((id) => fetcher(`/drivers/${id}`)));
      return profiles;
    },
    staleTime: 1000 * 60 * 60 * 6,
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Drivers</h1>
      {isLoading && <LoadingSkeleton lines={4} />}
      <div className="grid gap-4 md:grid-cols-3">
        {data?.map((driver) => (
          <Link key={driver.id} href={`/drivers/${driver.id}`} className="card group">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase text-slate-500">{driver.nationality}</p>
                <h3 className="text-lg font-semibold group-hover:text-accent transition">
                  {driver.name}
                </h3>
                <p className="text-sm text-slate-600">{driver.team}</p>
              </div>
              <div className="rounded-full bg-accent/10 px-3 py-1 text-xs text-accent">
                Profile
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
