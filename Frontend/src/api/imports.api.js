import apiClient from "./client";
import API_ENDPOINTS from "./endpoints";

/**
 * Upload a product file to the Django Imports API.
 *
 * @param {File} file - CSV/Excel file selected by the user
 * @returns {Promise} Axios response
 */
export async function uploadProducts(file) {
  if (!file) {
    throw new Error("No file selected.");
  }

  if (!(file instanceof File)) {
    throw new Error("Invalid file selected.");
  }

  const formData = new FormData();
  formData.append("file", file);

  // Debug: confirms this function is actually being called.
  console.log("[Imports] uploadProducts() called");
  console.log("[Imports] File:", {
    name: file.name,
    type: file.type,
    size: file.size,
  });

  // Debug: confirms the FormData contains the file.
  console.log(
    "[Imports] FormData file:",
    formData.get("file")
  );

  const endpoint = API_ENDPOINTS.imports.create;

  // Debug: shows the endpoint before Axios sends the request.
  console.log("[Imports] API endpoint:", endpoint);

  try {
    const response = await apiClient.post(endpoint, formData);

    console.log("[Imports] API response:", response);

    return response;
  } catch (error) {
    console.error("[Imports] API request failed:", error);

    if (error.response) {
      console.error("[Imports] Status:", error.response.status);
      console.error("[Imports] Response:", error.response.data);
    } else if (error.request) {
      console.error(
        "[Imports] Request was created but no response was received."
      );
    } else {
      console.error(
        "[Imports] Axios request could not be created:",
        error.message
      );
    }

    throw error;
  }
}

/**
 * Get a single import.
 *
 * @param {string|number} importId
 * @returns {Promise} Axios response
 */
export async function getImport(importId) {
  if (!importId) {
    throw new Error("Import ID is required.");
  }

  const endpoint = API_ENDPOINTS.imports.detail(importId);

  console.log("[Imports] Getting import:", importId);
  console.log("[Imports] API endpoint:", endpoint);

  try {
    const response = await apiClient.get(endpoint);

    console.log("[Imports] Import response:", response);

    return response;
  } catch (error) {
    console.error("[Imports] Get import failed:", error);

    if (error.response) {
      console.error("[Imports] Status:", error.response.status);
      console.error("[Imports] Response:", error.response.data);
    }

    throw error;
  }
}

/**
 * Get a list of past imports.
 *
 * @returns {Promise} Axios response
 */
export async function getImports() {
  const endpoint = API_ENDPOINTS.imports.list;
  console.log("[Imports] Getting list of imports:", endpoint);

  try {
    const response = await apiClient.get(endpoint);
    console.log("[Imports] Imports list response:", response);
    return response;
  } catch (error) {
    console.error("[Imports] Get imports list failed:", error);
    throw error;
  }
}