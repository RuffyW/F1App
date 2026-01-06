type Props = {
  heading: string;
  body: string;
  meta?: string;
};

export function TopStory({ heading, body, meta }: Props) {
  return (
    <article className="card h-full">
      <p className="text-xs uppercase tracking-wide text-slate-500">{meta}</p>
      <h3 className="mt-2 text-xl font-semibold text-slate-900">{heading}</h3>
      <p className="mt-3 text-sm text-slate-600 leading-relaxed">{body}</p>
    </article>
  );
}
