import apiClient from "./client";
import ENDPOINTS from "./endpoints";

/**
 * Get taxonomy categories.
 *
 * Supported backend query parameters:
 * - level
 * - root
 */
export async function getTaxonomyCategories({
  level = "",
  root = "",
} = {}) {
  return apiClient.get(ENDPOINTS.taxonomy.categories, {
    params: {
      level,
      root,
    },
  });
}

/**
 * Search taxonomy categories.
 *
 * Backend expects:
 * ?q=search-term
 */
export async function searchTaxonomy(query) {
  return apiClient.get(ENDPOINTS.taxonomy.search, {
    params: {
      q: query,
    },
  });
}

/**
 * Get taxonomy classification result for a product.
 */
export async function getProductTaxonomy(productId) {
  return apiClient.get(
    ENDPOINTS.taxonomy.product(productId)
  );
}

/**
 * Run taxonomy classification for a product.
 */
export async function classifyProduct(productId) {
  return apiClient.post(
    ENDPOINTS.taxonomy.classifyProduct(productId)
  );
}

/**
 * Run classification for multiple products.
 *
 * Backend accepts:
 * {
 *   limit: number
 * }
 */
export async function bulkClassifyProducts(limit = null) {
  const body = {};

  if (limit !== null && limit !== "") {
    body.limit = Number(limit);
  }

  return apiClient.post(
    ENDPOINTS.taxonomy.bulkClassify,
    body
  );
}