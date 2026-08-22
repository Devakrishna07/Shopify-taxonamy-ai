const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      data?.error ||
      "Something went wrong";

    throw new Error(message);
  }

  return data;
}

/**
 * Get review records.
 *
 * GET /api/review/
 */
export async function getReviews(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, value);
    }
  });

  const query = searchParams.toString();

  return request(`/review/${query ? `?${query}` : ""}`);
}

/**
 * Get one review.
 *
 * GET /api/review/<id>/
 */
export async function getReview(id) {
  return request(`/review/${id}/`);
}

/**
 * Approve review.
 *
 * POST /api/review/<id>/approve/
 */
export async function approveReview(id, payload = {}) {
  return request(`/review/${id}/approve/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Edit review.
 *
 * POST /api/review/<id>/edit/
 */
export async function editReview(id, payload) {
  return request(`/review/${id}/edit/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Reject review.
 *
 * POST /api/review/<id>/reject/
 */
export async function rejectReview(id, payload = {}) {
  return request(`/review/${id}/reject/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Load taxonomy categories for the edit dialog.
 *
 * Existing taxonomy API:
 * GET /api/taxonomy/categories/
 */
export async function getTaxonomyCategories(params = {}) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.append(key, value);
    }
  });

  const query = searchParams.toString();

  return request(`/taxonomy/categories/${query ? `?${query}` : ""}`);
}