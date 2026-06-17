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

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

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
  const token = localStorage.getItem("access_token");
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
    throw new ApiError(res.status, text);
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
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
  }
  const query = qs.toString();
  return request<PaginatedResponse<EventResponse>>(
    `/events${query ? `?${query}` : ""}`,
  );
}

export function searchEvents(q: string, page = 1, per_page = 20) {
  const qs = new URLSearchParams({ q, page: String(page), per_page: String(per_page) });
  return request<PaginatedResponse<EventResponse>>(`/events/search?${qs}`);
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

export function uploadImage(file: File) {
  const form = new FormData();
  form.append("file", file);
  return request<UploadResponse>("/upload/image", {
    method: "POST",
    body: form,
  });
}

export { ApiError };
