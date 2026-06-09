import Link from "next/link";

export default function TopBar() {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link
          href="/"
          className="flex items-center gap-2 rounded transition-opacity hover:opacity-80"
          aria-label="Go to home page"
        >
          <span className="text-xl" aria-hidden>🇬🇷</span>
          <span className="font-bold text-brand">Ask Greece for Business</span>
        </Link>
        <span className="hidden text-sm text-slate-500 sm:block">
          Public-Sector Digital Intelligence
        </span>
      </div>
    </header>
  );
}
