type Row = {
  position: number;
  driver: string;
  team: string;
  time?: string;
  delta?: string;
};

type Props = {
  title: string;
  rows: Row[];
};

export function ResultsTable({ title, rows }: Props) {
  return (
    <div className="card">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold">{title}</h3>
        <span className="text-xs text-slate-500">Stale-while-revalidate</span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-slate-500">
            <tr>
              <th className="py-2 pr-4">Pos</th>
              <th className="py-2 pr-4">Driver</th>
              <th className="py-2 pr-4">Team</th>
              <th className="py-2 pr-4">Time/Δ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-muted">
            {rows.map((row) => (
              <tr key={row.position} className="transition hover:bg-slate-50">
                <td className="py-2 pr-4 font-semibold">{row.position}</td>
                <td className="py-2 pr-4">{row.driver}</td>
                <td className="py-2 pr-4">{row.team}</td>
                <td className="py-2 pr-4 text-slate-600">
                  {row.time || row.delta || "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
