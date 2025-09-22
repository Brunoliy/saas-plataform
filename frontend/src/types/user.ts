export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  account_type: 'CLIENT' | 'PROFESSIONAL';
  active: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface UserCreate {
  email: string;
  full_name: string;
  phone?: string;
  account_type: 'CLIENT' | 'PROFESSIONAL';
  password: string;
}

export interface UserUpdate {
  full_name?: string;
  phone?: string;
  active?: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}