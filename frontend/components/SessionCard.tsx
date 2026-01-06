type Props = {
  title: string;
  status?: string;
  start: string;
  end: string;
  timezone?: string;
};

export function SessionCard({ title, status = "scheduled", start, end, timezone }: Props) {
  return (
    <div className="card flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{title}</h3>
        <span className="rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent capitalize">
          {status}
        </span>
      </div>
      <p className="text-sm text-slate-600">
        {new Date(start).toLocaleString(undefined, { timeZone: timezone })} →{" "}
        {new Date(end).toLocaleTimeString(undefined, { timeZone: timezone })}
      </p>
    </div>
  );
}
