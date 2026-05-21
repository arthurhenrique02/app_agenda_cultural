import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import type {
  AccessTokenResponse,
  CategoryResponse,
  EventCreateRequest,
  EventResponse,
  EventUpdateRequest,
  LoginRequest,
  PaginatedResponse,
  RegisterRequest,
  TokenResponse,
  UploadResponse,
  UserResponse,
  UserUpdateRequest,
} from "../types/api";

// For development: use your machine's IP address if testing on a real device
// Android emulator uses 10.0.2.2 to access localhost
const API_BASE = Platform.OS === 'android' 
  ? 'http://10.0.2.2:8000/api' 
  : 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = await SecureStore.getItemAsync("access_token");
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Only set Content-Type for JSON bodies (not FormData)
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const text = await res.text();
    let detail = text;
    try {
      const json = JSON.parse(text);
      detail = json.detail || text;
    } catch (e) {}
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

// --- Auth ---

export function register(data: RegisterRequest) {
  return request<UserResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(data: LoginRequest) {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function refreshToken(refresh_token: string) {
  return request<AccessTokenResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}

// --- User ---

export function getProfile() {
  return request<UserResponse>("/users/me");
}

export function updateProfile(data: UserUpdateRequest) {
  return request<UserResponse>("/users/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// --- Categories ---

export function listCategories() {
  return request<CategoryResponse[]>("/categories");
}

// --- Public Events ---

export interface EventListParams {
  page?: number;
  per_page?: number;
  category_id?: number;
  date_from?: string;
  date_to?: string;
  neighborhood?: string;
}

export function listEvents(params: EventListParams = {}) {
  const paramsArray: string[] = [];
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") {
      paramsArray.push(`${k}=${encodeURIComponent(String(v))}`);
    }
  }
  const query = paramsArray.join('&');
  return request<PaginatedResponse<EventResponse>>(
    `/events${query ? `?${query}` : ""}`,
  );
}

export function searchEvents(q: string, page = 1, per_page = 20) {
  const query = `q=${encodeURIComponent(q)}&page=${page}&per_page=${per_page}`;
  return request<PaginatedResponse<EventResponse>>(`/events/search?${query}`);
}

export function getEvent(id: number) {
  return request<EventResponse>(`/events/${id}`);
}

// --- Authenticated Events ---

export function createEvent(data: EventCreateRequest) {
  return request<EventResponse>("/events", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getMyEvents(page = 1, per_page = 20) {
  return request<PaginatedResponse<EventResponse>>(
    `/events/me?page=${page}&per_page=${per_page}`,
  );
}

export function updateEvent(id: number, data: EventUpdateRequest) {
  return request<EventResponse>(`/events/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteEvent(id: number) {
  return request<EventResponse>(`/events/${id}`, {
    method: "DELETE",
  });
}

// --- Upload ---

export function uploadImage(uri: string, type: string, name: string) {
  const form = new FormData();
  // @ts-ignore - React Native FormData expects an object with uri, type, and name
  form.append("file", {
    uri,
    type,
    name,
  });
  return request<UploadResponse>("/upload/image", {
    method: "POST",
    body: form,
  });
}

export { ApiError };
