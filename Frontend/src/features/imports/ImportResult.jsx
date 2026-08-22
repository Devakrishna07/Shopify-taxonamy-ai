export default function ImportResult({
  result,
  onRefresh,
  refreshing = false,
}) {
  if (!result) {
    return null;
  }

  const status =
    result.status?.toUpperCase() ||
    "UNKNOWN";

  const isFailed =
    status === "FAILED";

  const isCompleted =
    status === "COMPLETED" ||
    status === "SUCCESS" ||
    status === "SUCCEEDED";

  const statusClass = isFailed
    ? "bg-red-100 text-red-700"
    : isCompleted
      ? "bg-green-100 text-green-700"
      : "bg-blue-100 text-blue-700";

  return (
    <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">
            Import Job
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Backend import job status and progress.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span
            className={[
              "rounded-full px-3 py-1 text-xs font-semibold",
              statusClass,
            ].join(" ")}
          >
            {status}
          </span>

          {onRefresh && result.id && (
            <button
              type="button"
              onClick={onRefresh}
              disabled={refreshing}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {refreshing
                ? "Refreshing..."
                : "Refresh"}
            </button>
          )}
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Import ID"
          value={result.id}
        />

        <Stat
          label="Total Rows"
          value={result.totalRows}
        />

        <Stat
          label="Processed"
          value={result.processedRows}
        />

        <Stat
          label="Failed"
          value={result.failedRows}
        />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <Info
          label="File"
          value={result.fileName || "—"}
        />

        <Info
          label="Created"
          value={formatDate(
            result.createdAt
          )}
        />

        <Info
          label="Completed"
          value={formatDate(
            result.completedAt
          )}
        />

        <Info
          label="Processing State"
          value={status}
        />
      </div>

      {result.error && (
        <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <p className="font-semibold">
            Backend Error
          </p>

          <p className="mt-1">
            {result.error}
          </p>
        </div>
      )}

      {isFailed && !result.error && (
        <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          The backend marked this import as
          FAILED.
        </div>
      )}
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 p-4">
      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-2xl font-bold text-slate-900">
        {value ?? 0}
      </p>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 p-4">
      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 break-words font-medium text-slate-900">
        {value}
      </p>
    </div>
  );
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}