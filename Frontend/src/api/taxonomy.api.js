import apiClient from "./client";


/*
 * ============================================================
 * TAXONOMY API BASE
 * ============================================================
 *
 * client.js already adds:
 *
 *     http://127.0.0.1:8000/api
 *
 * Therefore these endpoints must NOT contain /api again.
 *
 * Final URLs become:
 *
 * GET /api/taxonomy/categories/
 * GET /api/taxonomy/search/
 * GET /api/taxonomy/attributes/
 * GET /api/taxonomy/values/
 * GET /api/taxonomy/products/<id>/
 * POST /api/taxonomy/products/<id>/classify/
 * POST /api/taxonomy/products/classify/
 */

const TAXONOMY_BASE =
  "/taxonomy";


/**
 * ============================================================
 * GET TAXONOMY CATEGORIES
 * ============================================================
 *
 * GET:
 *
 * /api/taxonomy/categories/
 *
 * Optional:
 *
 * ?level=1
 * ?root=true
 * ?leaf=true
 * ?search=shirt
 */
export async function getTaxonomyCategories(
  {
    level = "",
    root = "",
    leaf = "",
    search = "",
  } = {}
) {
  return apiClient.get(
    `${TAXONOMY_BASE}/categories/`,
    {
      params: {
        level,
        root,
        leaf,
        search,
      },
    }
  );
}


/**
 * ============================================================
 * SEARCH TAXONOMY
 * ============================================================
 *
 * GET:
 *
 * /api/taxonomy/search/?q=shirt
 */
export async function searchTaxonomy(
  query
) {
  return apiClient.get(
    `${TAXONOMY_BASE}/search/`,
    {
      params: {
        q: query,
      },
    }
  );
}


/**
 * ============================================================
 * GET TAXONOMY ATTRIBUTES
 * ============================================================
 *
 * GET:
 *
 * /api/taxonomy/attributes/
 */
export async function getTaxonomyAttributes(
  {
    search = "",
  } = {}
) {
  return apiClient.get(
    `${TAXONOMY_BASE}/attributes/`,
    {
      params: {
        search,
      },
    }
  );
}


/**
 * ============================================================
 * GET TAXONOMY VALUES
 * ============================================================
 *
 * GET:
 *
 * /api/taxonomy/values/
 *
 * Optional:
 *
 * ?attribute=1
 * ?search=red
 */
export async function getTaxonomyValues(
  {
    attribute = "",
    search = "",
  } = {}
) {
  return apiClient.get(
    `${TAXONOMY_BASE}/values/`,
    {
      params: {
        attribute,
        search,
      },
    }
  );
}


/**
 * ============================================================
 * GET CATEGORY ATTRIBUTES
 * ============================================================
 *
 * GET:
 *
 * /api/taxonomy/categories/<category_id>/attributes/
 */
export async function getCategoryAttributes(
  categoryId
) {
  if (!categoryId) {
    throw new Error(
      "Category ID is required."
    );
  }

  return apiClient.get(
    `${TAXONOMY_BASE}/categories/${categoryId}/attributes/`
  );
}


/**
 * ============================================================
 * GET PRODUCT TAXONOMY
 * ============================================================
 *
 * GET:
 *
 * /api/taxonomy/products/<product_id>/
 */
export async function getProductTaxonomy(
  productId
) {
  if (!productId) {
    throw new Error(
      "Product ID is required."
    );
  }

  return apiClient.get(
    `${TAXONOMY_BASE}/products/${productId}/`
  );
}


/**
 * ============================================================
 * CLASSIFY PRODUCT
 * ============================================================
 *
 * POST:
 *
 * /api/taxonomy/products/<product_id>/classify/
 */
export async function classifyProduct(
  productId
) {
  if (!productId) {
    throw new Error(
      "Product ID is required."
    );
  }

  return apiClient.post(
    `${TAXONOMY_BASE}/products/${productId}/classify/`
  );
}


/**
 * ============================================================
 * BULK CLASSIFICATION
 * ============================================================
 *
 * POST:
 *
 * /api/taxonomy/products/classify/
 *
 * Body:
 *
 * {
 *     "limit": 10
 * }
 */
export async function bulkClassifyProducts(
  limit = null
) {
  const body = {};

  if (
    limit !== null &&
    limit !== undefined &&
    limit !== ""
  ) {
    const numericLimit =
      Number(limit);

    if (
      !Number.isInteger(
        numericLimit
      ) ||
      numericLimit <= 0
    ) {
      throw new Error(
        "Limit must be a positive integer."
      );
    }

    body.limit =
      numericLimit;
  }

  return apiClient.post(
    `${TAXONOMY_BASE}/products/classify/`,
    body
  );
}