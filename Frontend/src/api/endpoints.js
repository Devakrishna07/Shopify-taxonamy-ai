export const API_ENDPOINTS = {
  processing: {
    list: "/processing/",
    create: "/processing/",
    detail: (id) => `/processing/${id}/`,
    start: (id) => `/processing/${id}/start/`,
  },

  results: {
    list: "/results/",
    detail: (id) => `/results/${id}/`,
    product: (productId) => `/results/product/${productId}/`,
    summary: "/results/summary/",
    approve: (id) => `/results/${id}/approve/`,
  },

  imports: {
    list: "/imports/",
    create: "/imports/",
    detail: (id) => `/imports/${id}/`,
  },

  taxonomy: {
    categories: "/taxonomy/categories/",
    search: "/taxonomy/search/",
    product: (productId) => `/taxonomy/products/${productId}/`,
    classifyProduct: (productId) => `/taxonomy/products/${productId}/classify/`,
    bulkClassify: "/taxonomy/products/classify/",
  },

  classification: {
    list: "/classification/",
    detail: (id) => `/products/${id}/classification/`,
  },

  attributes: {
    list: "/attributes/",
  },

  reviews: {
    list: "/reviews/",
  },
};

export default API_ENDPOINTS;

export const CLASSIFICATION_ENDPOINTS = {
  classifyProduct: (productId) => `/classification/products/${productId}/classify/`,

  getClassification: (productId) => `/classification/classifications/${productId}/`,

  classifyImport: (importId) => `/classification/imports/${importId}/classify/`,
};

