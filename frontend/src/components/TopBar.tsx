export default function TopBar() {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-xl" aria-hidden>🇬🇷</span>
          <span className="font-bold text-brand">Ask Greece for Business</span>
        </div>
        <span className="hidden text-sm text-slate-500 sm:block">
          Public-Sector Digital Intelligence
        </span>
      </div>
    </header>
  );
}
