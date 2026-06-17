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

export interface RefreshRequest {
  refresh_token: string;
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
  description: string;
  created_at: string;
}

// --- Event ---

export type EventStatus =
  | "pendente"
  | "aprovado"
  | "rejeitado"
  | "cancelado"
  | "encerrado";

export interface EventCreateRequest {
  title: string;
  description: string;
  date: string;
  start_time: string;
  end_time?: string | null;
  venue_name: string;
  address: string;
  neighborhood: string;
  city: string;
  category_id: number;
  image_url?: string | null;
}

export interface EventUpdateRequest {
  title?: string;
  description?: string;
  date?: string;
  start_time?: string;
  end_time?: string | null;
  venue_name?: string;
  address?: string;
  neighborhood?: string;
  city?: string;
  category_id?: number;
  image_url?: string | null;
}

export interface EventResponse {
  id: number;
  title: string;
  description: string;
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
  category_id: number;
  created_by: number;
  reviewed_by: number | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
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
