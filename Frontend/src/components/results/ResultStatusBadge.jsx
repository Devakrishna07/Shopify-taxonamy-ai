import React from "react";
import { getStatusLabel } from "../../utils/results.utils";

export default function ResultStatusBadge({ status }) {
  const normalized = String(status || "").toUpperCase();

  let className =
    "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium";

  if (normalized === "HIGH") {
    className +=
      " bg-green-100 text-green-700";
  } else if (normalized === "REVIEW") {
    className +=
      " bg-yellow-100 text-yellow-700";
  } else if (normalized === "MANUAL_REVIEW") {
    className +=
      " bg-blue-100 text-blue-700";
  } else if (normalized === "FAILED") {
    className +=
      " bg-red-100 text-red-700";
  } else {
    className +=
      " bg-gray-100 text-gray-700";
  }

  return (
    <span className={className}>
      {getStatusLabel(status)}
    </span>
  );
}