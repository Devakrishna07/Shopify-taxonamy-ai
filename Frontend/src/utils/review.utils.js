export function normalizeListResponse(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

  return [];
}

export function getProductId(review) {
  return (
    review?.product ??
    review?.product_id ??
    review?.product?.id ??
    "-"
  );
}

export function getOldCategory(review) {
  return (
    review?.old_category_id ??
    review?.old_category ??
    review?.predicted_category_id ??
    "-"
  );
}

export function getNewCategory(review) {
  return (
    review?.new_category_id ??
    review?.new_category ??
    review?.approved_category_id ??
    "-"
  );
}

export function getAction(review) {
  return String(review?.action || "").toUpperCase();
}

export function getComment(review) {
  return review?.comment || "";
}

export function getCreatedAt(review) {
  if (!review?.created_at) {
    return "-";
  }

  const date = new Date(review.created_at);

  if (Number.isNaN(date.getTime())) {
    return review.created_at;
  }

  return date.toLocaleString();
}

export function getActionLabel(action) {
  switch (String(action).toUpperCase()) {
    case "APPROVE":
      return "Approved";

    case "EDIT":
      return "Edited";

    case "REJECT":
      return "Rejected";

    default:
      return action || "Pending";
  }
}

export function getActionClass(action) {
  switch (String(action).toUpperCase()) {
    case "APPROVE":
      return "review-status review-status-approved";

    case "EDIT":
      return "review-status review-status-edited";

    case "REJECT":
      return "review-status review-status-rejected";

    default:
      return "review-status review-status-pending";
  }
}