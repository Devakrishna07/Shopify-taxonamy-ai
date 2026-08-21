export const API_ENDPOINTS = {
  processing: {
    list: "/processing/",
    create: "/processing/",
    detail: (id) => `/processing/${id}/`,
    start: (id) => `/processing/${id}/start/`
  },

  results: {
    list: "/results/",
    detail: (id) => `/results/${id}/`,
    approve: (id) => `/results/${id}/approve/`,
    reject: (id) => `/results/${id}/reject/`,
    reclassify: (id) => `/results/${id}/reclassify/`
  },

  imports: {
    list: "/imports/",
    create: "/imports/"
  },

  taxonomy: {
    list: "/taxonomy/"
  },

  classification: {
    list: "/classification/"
  },

  attributes: {
    list: "/attributes/"
  },

  reviews: {
    list: "/reviews/"
  }
};