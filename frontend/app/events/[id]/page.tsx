"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { SessionCard } from "../../../components/SessionCard";
import { fetcher } from "../../../lib/api";
import { LoadingSkeleton } from "../../../components/LoadingSkeleton";

type Event = {
  id: string;
  name: string;
  country: string;
  timezone: string;
  sessions: { id: string; name: string; start: string; end: string; type: string }[];
};

export default function EventDetailPage() {
  const params = useParams<{ id: string }>();
  const eventId = params?.id;

  const { data, isLoading } = useQuery<Event>({
    queryKey: ["event", eventId],
    queryFn: () => fetcher(`/events/${eventId}`),
    enabled: Boolean(eventId),
  });

  if (isLoading || !data) {
    return <LoadingSkeleton lines={6} />;
  }

  return (
    <div className="space-y-4">
      <div className="card flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500 uppercase tracking-wide">{data.country}</p>
          <h1 className="text-2xl font-semibold">{data.name}</h1>
          <p className="text-sm text-slate-500">{data.timezone}</p>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {data.sessions.map((session) => (
          <Link key={session.id} href={`/sessions/${session.id}`} className="block">
            <SessionCard
              title={`${session.name} (${session.type})`}
              start={session.start}
              end={session.end}
              timezone={data.timezone}
            />
          </Link>
        ))}
      </div>
    </div>
  );
}
