import client from "./client";

const classificationApi = {
  /**
   * Classify one product.
   */
  classifyProduct: async (productId) => {
    return client.post(
      `/classification/products/${productId}/classify/`
    );
  },

  /**
   * Get existing classification result.
   */
  getClassification: async (productId) => {
    return client.get(
      `/classification/classifications/${productId}/`
    );
  },

  /**
   * Classify all products belonging to an import.
   */
  classifyImport: async (importId) => {
    return client.post(
      `/classification/imports/${importId}/classify/`
    );
  },
};

export default classificationApi;