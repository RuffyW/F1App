"use client";

import { useQuery } from "@tanstack/react-query";
import { CountdownTimer } from "../components/CountdownTimer";
import { ResultsTable } from "../components/ResultsTable";
import { TopStory } from "../components/TopStory";
import { fetcher } from "../lib/api";
import { LoadingSkeleton } from "../components/LoadingSkeleton";

type Event = {
  id: string;
  name: string;
  sessions: { id: string; name: string; start: string; end: string; local_start?: string }[];
};

export default function DashboardPage() {
  const { data: calendar, isLoading } = useQuery<Event[]>({
    queryKey: ["calendar", "upcoming"],
    queryFn: () => fetcher("/calendar?status=upcoming"),
  });

  const nextEvent = calendar?.[0];
  const nextSession = nextEvent?.sessions[0];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="md:col-span-2">
          {nextSession ? (
            <CountdownTimer
              target={nextSession.start}
              label={`Next: ${nextSession.name}`}
            />
          ) : (
            <LoadingSkeleton lines={3} />
          )}
        </div>
        <TopStory
          heading="Top story"
          body="Track the latest pace trends, tyre management, and strategy cues ahead of the next race weekend."
          meta="Insights"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <TopStory
          heading="Last race results"
          body="Leverage cached classification endpoints for instant recall even when offline."
          meta="Race wrap"
        />
        <TopStory
          heading="Top 5 drivers"
          body="Use the /standings/drivers endpoint with a 30m TTL to keep leaderboards fresh."
          meta="Standings"
        />
        <TopStory
          heading="Team rankings"
          body="Compare constructors using cached /standings/teams responses aligned to the last completed round."
          meta="Constructors"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="card">
          <h3 className="mb-3 text-lg font-semibold">Upcoming sessions</h3>
          {isLoading && <LoadingSkeleton lines={4} />}
          {!isLoading && (
            <ul className="space-y-3">
              {nextEvent?.sessions?.map((session) => (
                <li key={session.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{session.name}</p>
                    <p className="text-sm text-slate-500">
                      {new Date(session.local_start || session.start).toLocaleString()}
                    </p>
                  </div>
                  <span className="text-xs text-slate-500">Local time</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <ResultsTable
          title="Sprint to race comparison"
          rows={[
            { position: 1, driver: "Driver One", team: "Team A", delta: "-0.250s" },
            { position: 2, driver: "Driver Two", team: "Team B", delta: "+0.115s" },
            { position: 3, driver: "Driver Three", team: "Team C", delta: "+0.320s" },
          ]}
        />
      </div>
    </div>
  );
}
