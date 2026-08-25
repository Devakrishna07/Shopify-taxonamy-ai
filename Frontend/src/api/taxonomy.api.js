
import apiClient from "./client";

const TAXONOMY_BASE = "/taxonomy";


export async function getTaxonomyCategories({
  level = "",
  root = "",
  leaf = "",
  search = "",
} = {}) {
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


export async function searchTaxonomy(query) {
  return apiClient.get(
    `${TAXONOMY_BASE}/search/`,
    {
      params: {
        q: query,
      },
    }
  );
}


export async function getTaxonomyAttributes({
  search = "",
} = {}) {
  return apiClient.get(
    `${TAXONOMY_BASE}/attributes/`,
    {
      params: {
        search,
      },
    }
  );
}


export async function getTaxonomyValues({
  attribute = "",
  search = "",
} = {}) {
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


export async function getProductTaxonomyResults({
  search = "",
  status = "",
  classification = "",
  category = "",
  level = "",
  page = 1,
  pageSize = 50,
} = {}) {
  return apiClient.get(
    `${TAXONOMY_BASE}/products/`,
    {
      params: {
        search,
        status,
        classification,
        category,
        level,
        page,
        page_size: pageSize,
      },
    }
  );
}


export async function getTaxonomyStats() {
  return apiClient.get(
    `${TAXONOMY_BASE}/stats/`
  );
}


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


export async function bulkClassifyProducts({
  limit = 10,
  onlyUnclassified = true,
} = {}) {
  return apiClient.post(
    `${TAXONOMY_BASE}/products/classify/`,
    {
      limit: Number(limit),
      only_unclassified:
        onlyUnclassified,
    }
  );
}


export async function approveProductTaxonomy(
  productId,
  categoryId
) {
  if (!productId) {
    throw new Error(
      "Product ID is required."
    );
  }

  if (!categoryId) {
    throw new Error(
      "Category ID is required."
    );
  }

  return apiClient.post(
    `${TAXONOMY_BASE}/products/${productId}/approve/`,
    {
      category_id: categoryId,
    }
  );
}


export async function rejectProductTaxonomy(
  productId,
  reason = ""
) {
  if (!productId) {
    throw new Error(
      "Product ID is required."
    );
  }

  return apiClient.post(
    `${TAXONOMY_BASE}/products/${productId}/reject/`,
    {
      reason,
    }
  );
}


export default {
  getTaxonomyCategories,
  searchTaxonomy,
  getTaxonomyAttributes,
  getTaxonomyValues,
  getCategoryAttributes,

  getProductTaxonomy,
  getProductTaxonomyResults,

  getTaxonomyStats,

  classifyProduct,
  bulkClassifyProducts,

  approveProductTaxonomy,
  rejectProductTaxonomy,
};
