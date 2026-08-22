import client from "./client";
import endpoints from "./endpoints";

/**
 * Get all classification results.
 *
 * Supported backend query parameters:
 * - search
 * - status
 * - min_confidence
 * - ordering
 */
export async function getResults(params = {}) {
  const response = await client.get(endpoints.results.list, {
    params,
  });

  return response.data;
}

/**
 * Get one result by ClassificationResult ID.
 */
export async function getResultById(id) {
  const response = await client.get(
    endpoints.results.detail(id)
  );

  return response.data;
}

/**
 * Get classification result for a specific product.
 */
export async function getProductResult(productId) {
  const response = await client.get(
    endpoints.results.product(productId)
  );

  return response.data;
}

/**
 * Get Results dashboard summary.
 */
export async function getResultsSummary() {
  const response = await client.get(
    endpoints.results.summary
  );

  return response.data;
}

/**
 * Approve a result.
 *
 * NOTE:
 * The current backend ResultApproveView exists,
 * but its URL is not currently registered in urls.py.
 */
export async function approveResult(id, comment = "") {
  const response = await client.post(
    endpoints.results.approve(id),
    {
      comment,
    }
  );

  return response.data;
}