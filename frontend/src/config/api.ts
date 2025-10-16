import axios, { type AxiosRequestConfig } from 'axios';

const DEFAULT_CORE_URL = 'http://localhost:8000/api';

const configuredCoreUrl =
  import.meta.env.VITE_CORE_API_URL ??
  import.meta.env.VITE_API_URL ??
  DEFAULT_CORE_URL;

const configuredModelUrl =
  import.meta.env.VITE_MODEL_API_URL ??
  configuredCoreUrl;

export const CORE_API_URL = configuredCoreUrl.replace(/\/$/, '');
export const MODEL_API_URL = configuredModelUrl.replace(/\/$/, '');

function createClient(baseURL: string) {
  return axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

export const coreApiClient = createClient(CORE_API_URL);
export const modelApiClient = createClient(MODEL_API_URL);

export async function apiRequest<T = unknown>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await coreApiClient.request<T>({
    url: endpoint,
    ...config
  });

  return response.data;
}

export async function modelRequest<T = unknown>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await modelApiClient.request<T>({
    url: endpoint,
    ...config
  });

  return response.data;
}