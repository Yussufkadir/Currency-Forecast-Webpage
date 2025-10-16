import axios, { type AxiosRequestConfig } from 'axios';

const DEFAULT_BASE_URL = 'http://localhost:8000/api';

const configuredBaseUrl = import.meta.env.VITE_API_URL ?? DEFAULT_BASE_URL;

export const API_URL = configuredBaseUrl.replace(/\/$/, '');

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export async function apiRequest<T = unknown>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.request<T>({
    url: endpoint,
    ...config
  });

  return response.data;
}