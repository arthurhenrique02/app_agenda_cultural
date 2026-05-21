// Shared API types matching backend Pydantic schemas

// --- Auth ---

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AccessTokenResponse {
  access_token: string;
  token_type: string;
}

// --- User ---

export type UserRole = "user" | "admin";

export interface UserResponse {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface UserUpdateRequest {
  name?: string;
  email?: string;
}

// --- Category ---

export interface CategoryResponse {
  id: number;
  name: string;
}

// --- Event ---

export type EventStatus = "pendente" | "aprovado" | "rejeitado" | "cancelado";

export interface EventResponse {
  id: number;
  title: string;
  description: string;
  category_id: number;
  date: string;
  start_time: string;
  end_time: string | null;
  venue_name: string;
  address: string;
  neighborhood: string;
  city: string;
  image_url: string | null;
  status: EventStatus;
  rejection_reason: string | null;
  created_by: number;
  created_at: string;
  reviewed_by: number | null;
  reviewed_at: string | null;
}

export interface EventCreateRequest {
  title: string;
  description: string;
  category_id: number;
  date: string;
  start_time: string;
  end_time: string | null;
  venue_name: string;
  address: string;
  neighborhood: string;
  city: string;
  image_url: string | null;
}

export interface EventUpdateRequest extends Partial<EventCreateRequest> {}

// --- Admin ---

export interface RejectEventRequest {
  reason: string;
}

export interface DashboardResponse {
  total_events: number;
  pendente: number;
  aprovado: number;
  rejeitado: number;
  cancelado: number;
  total_users: number;
}

// --- Pagination ---

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// --- Upload ---

export interface UploadResponse {
  url: string;
}
