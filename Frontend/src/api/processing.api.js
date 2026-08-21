import apiClient from "./client";
import { API_ENDPOINTS } from "./endpoints";

export async function getProcessingJobs(params = {}) {
  const response = await apiClient.get(
    API_ENDPOINTS.processing.list,
    {
      params
    }
  );

  return response.data;
}

export async function getProcessingJob(id) {
  const response = await apiClient.get(
    API_ENDPOINTS.processing.detail(id)
  );

  return response.data;
}

export async function createProcessingJob(payload) {
  const response = await apiClient.post(
    API_ENDPOINTS.processing.create,
    payload
  );

  return response.data;
}

export async function startProcessingJob(id) {
  const response = await apiClient.post(
    API_ENDPOINTS.processing.start(id)
  );

  return response.data;
}