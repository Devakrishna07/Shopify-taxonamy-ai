export default function LoadingState({
  message = "Loading...",
}) {
  return (
    <div className="flex items-center justify-center py-10">
      <div className="flex items-center gap-3 text-gray-600">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />

        <span>{message}</span>
      </div>
    </div>
  );
}