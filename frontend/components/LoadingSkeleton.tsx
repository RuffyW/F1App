type Props = {
  lines?: number;
};

export function LoadingSkeleton({ lines = 3 }: Props) {
  return (
    <div className="card">
      <div className="flex flex-col gap-2">
        {Array.from({ length: lines }).map((_, idx) => (
          <div
            key={idx}
            className="skeleton h-4"
            style={{ width: `${80 - idx * 10}%` }}
          />
        ))}
      </div>
    </div>
  );
}
