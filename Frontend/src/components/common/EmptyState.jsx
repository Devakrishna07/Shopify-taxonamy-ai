export default function EmptyState({
  title = "No results",
  message = "There is nothing to display.",
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-10 text-center">
      <h3 className="font-semibold text-gray-800">
        {title}
      </h3>

      <p className="mt-2 text-sm text-gray-500">
        {message}
      </p>
    </div>
  );
}