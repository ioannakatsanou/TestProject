interface Props {
  onRetry: () => void;
}

export default function ErrorState({ onRetry }: Props) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
      <p className="text-red-700">Something went wrong generating the answer.</p>
      <button
        onClick={onRetry}
        className="mt-4 rounded-lg bg-brand px-4 py-2 font-semibold text-white hover:bg-brand-dark"
      >
        Retry
      </button>
    </div>
  );
}
