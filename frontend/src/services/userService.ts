import apiClient from './api';
import { User, UserCreate, UserUpdate, PaginatedResponse } from '../types/user';

export class UserService {
  static async createUser(userData: UserCreate): Promise<User> {
    const response = await apiClient.post<User>('/users/', userData);
    return response.data;
  }

  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  }

  static async updateCurrentUser(userData: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>('/users/me', userData);
    return response.data;
  }

  static async getUsers(page: number = 1, size: number = 20): Promise<PaginatedResponse<User>> {
    const skip = (page - 1) * size;
    const response = await apiClient.get<PaginatedResponse<User>>('/users/', {
      params: { skip, limit: size },
    });
    return response.data;
  }

  static async getUserById(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`/users/${userId}`);
    return response.data;
  }

  static async updateUser(userId: string, userData: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>(`/users/${userId}`, userData);
    return response.data;
  }

  static async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/users/${userId}`);
  }

  static async activateUser(userId: string): Promise<User> {
    const response = await apiClient.patch<User>(`/users/${userId}/activate`);
    return response.data;
  }

  static async deactivateUser(userId: string): Promise<User> {
    const response = await apiClient.patch<User>(`/users/${userId}/deactivate`);
    return response.data;
  }
}