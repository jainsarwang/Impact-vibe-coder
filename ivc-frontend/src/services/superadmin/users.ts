
import { baseURL, getAuthHeaders, handleApiError } from './base';

export const getUserByUsername = async (username: string): Promise<any> => {
  try {
    const response = await fetch(`${baseURL}/users/${username}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to fetch user');
    }

    return await response.json();
  } catch (error: any) {
    return handleApiError(error);
  }
};
