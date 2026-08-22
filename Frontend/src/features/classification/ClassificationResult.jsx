import ClassificationCandidates from "./ClassificationCandidate";
import ClassificationScores from "./ClassificationScores";
import ClassificationStatus from "./ClassificationStatus";

export default function ClassificationResult({
  result,
}) {
  if (!result) {
    return null;
  }

  return (
    <div className="space-y-6">

      {/* Main classification */}
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

          <div>
            <p className="text-sm font-medium text-gray-500">
              Predicted Category
            </p>

            <h2 className="mt-1 text-2xl font-bold text-gray-900">
              {result.category_name || "No category assigned"}
            </h2>

            {result.category_full_name && (
              <p className="mt-2 text-sm text-gray-500">
                {result.category_full_name}
              </p>
            )}
          </div>

          <ClassificationStatus
            status={result.status}
          />
        </div>

        {result.reason && (
          <div className="mt-5 rounded-lg bg-gray-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
              Classification Reason
            </p>

            <p className="mt-1 text-sm text-gray-700">
              {result.reason}
            </p>
          </div>
        )}
      </section>

      {/* Scores */}
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-6 text-lg font-semibold text-gray-900">
          Classification Confidence
        </h2>

        <ClassificationScores
          confidence={result.confidence}
          textScore={result.text_score}
          imageScore={result.image_score}
          attributeScore={result.attribute_score}
        />
      </section>

      {/* Alternatives */}
      <ClassificationCandidates
        candidates={result.candidates}
      />

      {/* Metadata */}
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Classification Details
        </h2>

        <dl className="grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-medium uppercase text-gray-500">
              Product ID
            </dt>

            <dd className="mt-1 text-sm text-gray-900">
              {result.product}
            </dd>
          </div>

          <div>
            <dt className="text-xs font-medium uppercase text-gray-500">
              Classification ID
            </dt>

            <dd className="mt-1 text-sm text-gray-900">
              {result.id}
            </dd>
          </div>

          <div>
            <dt className="text-xs font-medium uppercase text-gray-500">
              Created
            </dt>

            <dd className="mt-1 text-sm text-gray-900">
              {result.created_at
                ? new Date(result.created_at).toLocaleString()
                : "-"}
            </dd>
          </div>

          <div>
            <dt className="text-xs font-medium uppercase text-gray-500">
              Updated
            </dt>

            <dd className="mt-1 text-sm text-gray-900">
              {result.updated_at
                ? new Date(result.updated_at).toLocaleString()
                : "-"}
            </dd>
          </div>
        </dl>
      </section>
    </div>
  );
}