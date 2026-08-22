export function formatConfidence(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return "—";
  }

  // Backend may return either 0–1 or 0–100.
  const percentage =
    number <= 1 ? number * 100 : number;

  return `${percentage.toFixed(1)}%`;
}

export function getStatusLabel(status) {
  if (!status) {
    return "Unknown";
  }

  return String(status)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}

export function getDecisionLabel(status) {
  if (!status) {
    return "No Decision";
  }

  return String(status)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}

export function isReviewRequired(result) {
  return (
    result?.decision?.requires_review === true ||
    String(result?.status || "").toUpperCase() === "REVIEW"
  );
}

export function getProductTitle(result) {
  return result?.product?.title || "Untitled Product";
}

export function getProductSku(result) {
  return result?.product?.sku || "—";
}

export function getProductBrand(result) {
  return result?.product?.brand || "—";
}