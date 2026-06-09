export default function EmptyState() {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
      <p className="text-slate-700">
        I couldn&apos;t find decisions in scope that answer this.
      </p>
      <p className="mt-2 text-sm text-slate-500">
        This prototype covers IT &amp; digital spending for 15 municipalities over
        the last 12 months. Try one of the suggested questions.
      </p>
    </div>
  );
}
