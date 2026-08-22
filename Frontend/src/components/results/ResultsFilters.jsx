import React from "react";

export default function ResultsFilters({
  filters,
  onChange,
  onReset,
}) {
  return (
    <div className="rounded-xl border bg-white p-4 shadow-sm">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Search
          </label>

          <input
            type="text"
            value={filters.search}
            onChange={(event) =>
              onChange(
                "search",
                event.target.value
              )
            }
            placeholder="Search product, SKU, brand..."
            className="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Status
          </label>

          <select
            value={filters.status}
            onChange={(event) =>
              onChange(
                "status",
                event.target.value
              )
            }
            className="w-full rounded-lg border px-3 py-2 text-sm"
          >
            <option value="">All Statuses</option>
            <option value="HIGH">
              High
            </option>
            <option value="REVIEW">
              Review
            </option>
            <option value="MANUAL_REVIEW">
              Manual Review
            </option>
            <option value="FAILED">
              Failed
            </option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Minimum Confidence
          </label>

          <select
            value={filters.min_confidence}
            onChange={(event) =>
              onChange(
                "min_confidence",
                event.target.value
              )
            }
            className="w-full rounded-lg border px-3 py-2 text-sm"
          >
            <option value="">
              Any Confidence
            </option>
            <option value="0.5">
              50%+
            </option>
            <option value="0.7">
              70%+
            </option>
            <option value="0.8">
              80%+
            </option>
            <option value="0.9">
              90%+
            </option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Sort
          </label>

          <select
            value={filters.ordering}
            onChange={(event) =>
              onChange(
                "ordering",
                event.target.value
              )
            }
            className="w-full rounded-lg border px-3 py-2 text-sm"
          >
            <option value="-id">
              Newest
            </option>
            <option value="id">
              Oldest
            </option>
            <option value="-confidence">
              Highest Confidence
            </option>
            <option value="confidence">
              Lowest Confidence
            </option>
          </select>
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
}