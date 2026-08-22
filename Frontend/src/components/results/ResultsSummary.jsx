import React from "react";
import { formatConfidence } from "../../utils/results.utils";

export default function ResultsSummary({
  summary,
  loading,
}) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <div
            key={index}
            className="h-24 animate-pulse rounded-lg bg-gray-100"
          />
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: "Total Results",
      value: summary?.total_results ?? 0,
    },
    {
      label: "High Confidence",
      value: summary?.high_confidence ?? 0,
    },
    {
      label: "Review Required",
      value: summary?.review_required ?? 0,
    },
    {
      label: "Manual Review",
      value: summary?.manual_review ?? 0,
    },
    {
      label: "Failed",
      value: summary?.failed ?? 0,
    },
    {
      label: "Avg. Confidence",
      value: formatConfidence(
        summary?.average_confidence
      ),
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl border bg-white p-4 shadow-sm"
        >
          <p className="text-sm text-gray-500">
            {card.label}
          </p>

          <p className="mt-2 text-2xl font-semibold text-gray-900">
            {card.value}
          </p>
        </div>
      ))}
    </div>
  );
}