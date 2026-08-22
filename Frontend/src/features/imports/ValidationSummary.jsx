export default function ValidationSummary({
  result,
}) {
  if (!result) {
    return null;
  }

  const total =
    result.totalRows ?? 0;

  const processed =
    result.processedRows ?? 0;

  const failed =
    result.failedRows ?? 0;

  const successful =
    Math.max(processed - failed, 0);

  return (
    <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-slate-900">
          Import Validation Summary
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Summary derived from the backend
          ImportJob response.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard
          label="Total Rows"
          value={total}
        />

        <SummaryCard
          label="Processed Rows"
          value={processed}
        />

        <SummaryCard
          label="Successful"
          value={successful}
        />

        <SummaryCard
          label="Failed Rows"
          value={failed}
        />
      </div>

      {failed > 0 && (
        <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          {failed} row
          {failed === 1 ? "" : "s"} failed
          during import processing.
        </div>
      )}
    </section>
  );
}

function SummaryCard({
  label,
  value,
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-slate-900">
        {value}
      </p>
    </div>
  );
}