import ClassificationStatus from "./ClassificationStatus";

export default function ClassificationCandidates({
  candidates = [],
}) {
  if (!candidates.length) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-6 text-center">
        <p className="text-sm text-gray-500">
          No alternative categories available.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <div className="border-b bg-gray-50 px-4 py-3">
        <h3 className="font-semibold text-gray-900">
          Alternative Categories
        </h3>
      </div>

      <div className="divide-y">
        {candidates.map((candidate) => (
          <div
            key={candidate.id}
            className="flex items-center justify-between gap-4 px-4 py-4"
          >
            <div>
              <p className="font-medium text-gray-900">
                {candidate.category_name}
              </p>

              {candidate.category_full_name && (
                <p className="mt-1 text-xs text-gray-500">
                  {candidate.category_full_name}
                </p>
              )}

              <p className="mt-1 text-xs text-gray-500">
                Source: {candidate.source}
              </p>
            </div>

            <div className="text-right">
              <p className="font-semibold text-gray-900">
                {(Number(candidate.score) * 100).toFixed(1)}%
              </p>

              <p className="text-xs text-gray-500">
                Rank #{candidate.rank}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}