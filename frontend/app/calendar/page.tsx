"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { SessionCard } from "../../components/SessionCard";
import { fetcher } from "../../lib/api";
import { LoadingSkeleton } from "../../components/LoadingSkeleton";

type Event = {
  id: string;
  name: string;
  country: string;
  timezone: string;
  sessions: { id: string; name: string; start: string; end: string }[];
};

const filters = [
  { key: "upcoming", label: "Upcoming" },
  { key: "completed", label: "Completed" },
  { key: "all", label: "All" },
];

export default function CalendarPage() {
  const [status, setStatus] = useState("upcoming");
  const { data, isLoading } = useQuery<Event[]>({
    queryKey: ["calendar", status],
    queryFn: () => fetcher(`/calendar?status=${status}`),
    staleTime: 1000 * 60 * 60 * 24,
  });

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {filters.map((filter) => (
          <button
            key={filter.key}
            onClick={() => setStatus(filter.key)}
            className={`rounded-full px-4 py-2 text-sm transition ${
              status === filter.key
                ? "bg-accent text-white shadow-soft"
                : "bg-surface text-slate-700 shadow-sm"
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {isLoading && <LoadingSkeleton lines={5} />}

      <div className="grid gap-4 md:grid-cols-2">
        {data?.map((event) => (
          <div key={event.id} className="card space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500 uppercase tracking-wide">{event.country}</p>
                <h2 className="text-xl font-semibold">{event.name}</h2>
              </div>
              <span className="text-xs text-slate-500">{event.timezone}</span>
            </div>
            <div className="space-y-2">
              {event.sessions.map((session) => (
                <SessionCard
                  key={session.id}
                  title={session.name}
                  start={session.start}
                  end={session.end}
                  timezone={event.timezone}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
