export default function ErrorState({
  message = "Something went wrong.",
  onRetry,
}) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-5">
      <h3 className="font-semibold text-red-800">
        Unable to load data
      </h3>

      <p className="mt-1 text-sm text-red-700">
        {message}
      </p>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
        >
          Retry
        </button>
      )}
    </div>
  );
}