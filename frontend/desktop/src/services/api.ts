import type {
  AccessTokenResponse,
  CategoryResponse,
  DashboardResponse,
  EventResponse,
  EventUpdateRequest,
  LoginRequest,
  PaginatedResponse,
  TokenResponse,
  UserResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("admin_access_token");
  const headers = new Headers(options.headers);

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && path !== "/auth/login") {
    localStorage.removeItem("admin_access_token");
    localStorage.removeItem("admin_refresh_token");
    window.location.hash = "#/login";
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData.detail || "Erro na requisição");
  }

  return response.json();
}

// --- Auth ---

export function login(data: LoginRequest) {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function refreshAccessToken(refreshToken: string) {
  return request<AccessTokenResponse>("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export function getProfile() {
  return request<UserResponse>("/users/me");
}

// --- Admin Dashboard ---

export function getDashboardStats() {
  return request<DashboardResponse>("/admin/dashboard");
}

// --- Admin Events ---

export function listPendingEvents(page = 1) {
  return request<PaginatedResponse<EventResponse>>(`/admin/events/pending?page=${page}`);
}

export function listAllEvents(page = 1, status?: string) {
  const params = new URLSearchParams({ page: page.toString() });
  if (status) params.append("status", status);
  return request<PaginatedResponse<EventResponse>>(`/admin/events?${params}`);
}

export function approveEvent(id: number) {
  return request<EventResponse>(`/admin/events/${id}/approve`, {
    method: "PATCH",
  });
}

export function rejectEvent(id: number, reason: string) {
  return request<EventResponse>(`/admin/events/${id}/reject`, {
    method: "PATCH",
    body: JSON.stringify({ reason }),
  });
}

export function updateAdminEvent(id: number, data: EventUpdateRequest) {
  return request<EventResponse>(`/admin/events/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export function deleteAdminEvent(id: number) {
  return request<void>(`/admin/events/${id}`, {
    method: "DELETE",
  });
}

// --- Admin Users ---

export function listUsers(page = 1) {
  return request<PaginatedResponse<UserResponse>>(`/admin/users?page=${page}`);
}

export function promoteUser(id: number) {
  return request<UserResponse>(`/admin/users/${id}/promote`, {
    method: "PATCH",
  });
}

// --- Public ---
export function listCategories() {
  return request<CategoryResponse[]>("/categories");
}

export { ApiError };
