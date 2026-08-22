import React from "react";
import ResultStatusBadge from "./ResultStatusBadge";
import {
  formatConfidence,
  getProductTitle,
  getProductSku,
  getProductBrand,
  getDecisionLabel,
} from "../../utils/results.utils";

export default function ResultsTable({
  results,
  loading,
  onSelect,
}) {
  if (loading) {
    return (
      <div className="rounded-xl border bg-white p-8 text-center text-gray-500">
        Loading results...
      </div>
    );
  }

  if (!results.length) {
    return (
      <div className="rounded-xl border bg-white p-8 text-center text-gray-500">
        No classification results found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                Product
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                SKU
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                Brand
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                Confidence
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                Status
              </th>

              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                Decision
              </th>

              <th className="px-4 py-3 text-right text-xs font-semibold uppercase text-gray-500">
                Action
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200">
            {results.map((result) => (
              <tr
                key={result.id}
                className="hover:bg-gray-50"
              >
                <td className="px-4 py-4">
                  <div className="font-medium text-gray-900">
                    {getProductTitle(result)}
                  </div>

                  <div className="text-xs text-gray-500">
                    ID: {result.product?.id ?? "—"}
                  </div>
                </td>

                <td className="px-4 py-4 text-sm text-gray-600">
                  {getProductSku(result)}
                </td>

                <td className="px-4 py-4 text-sm text-gray-600">
                  {getProductBrand(result)}
                </td>

                <td className="px-4 py-4 text-sm font-medium">
                  {formatConfidence(
                    result.confidence
                  )}
                </td>

                <td className="px-4 py-4">
                  <ResultStatusBadge
                    status={result.status}
                  />
                </td>

                <td className="px-4 py-4 text-sm text-gray-600">
                  {getDecisionLabel(
                    result.decision?.decision_status
                  )}
                </td>

                <td className="px-4 py-4 text-right">
                  <button
                    type="button"
                    onClick={() =>
                      onSelect(result)
                    }
                    className="rounded-lg border px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50"
                  >
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}