// API service for Super Admin Portal
// This service handles all API communications

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

interface ApiResponse<T> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

interface LoginCredentials {
    username: string;
    password: string;
}

interface Organization {
    id: string;
    name: string;
    isActive: boolean;
    adminCount: number;
    userCount: number;
    tokens: number;
    createdAt: string;
}

interface Admin {
    id: string;
    name: string;
    email: string;
    phone: string;
    isActive: boolean;
    linkedUsers: number;
    lastLogin: string;
    role: string;
    organizationId: string;
}

interface User {
    id: string;
    name: string;
    email: string;
    phone: string;
    isActive: boolean;
    lastLogin: string;
    location: string;
    joinedDate: string;
    activityScore: number;
    adminId: string;
}

// Authentication API
export const authApi = {
    login: async (
        credentials: LoginCredentials
    ): Promise<ApiResponse<{ token: string; user: any }>> => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(credentials),
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Login API error:", error);
            return { success: false, error: "Network error occurred" };
        }
    },

    logout: async (): Promise<ApiResponse<void>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            localStorage.removeItem("authToken");
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Logout API error:", error);
            return { success: false, error: "Network error occurred" };
        }
    },
};

// Organization API
export const organizationApi = {
    getAll: async (): Promise<ApiResponse<Organization[]>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(`${API_BASE_URL}/organizations`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Get organizations API error:", error);
            return { success: false, error: "Failed to fetch organizations" };
        }
    },

    getById: async (id: string): Promise<ApiResponse<Organization>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(
                `${API_BASE_URL}/organizations/${id}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Get organization API error:", error);
            return {
                success: false,
                error: "Failed to fetch organization details",
            };
        }
    },

    create: async (orgData: {
        name: string;
        tokens: number;
    }): Promise<ApiResponse<Organization>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(`${API_BASE_URL}/organizations`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(orgData),
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Create organization API error:", error);
            return { success: false, error: "Failed to create organization" };
        }
    },

    updateStatus: async (
        id: string,
        isActive: boolean
    ): Promise<ApiResponse<Organization>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(
                `${API_BASE_URL}/organizations/${id}/status`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({ isActive }),
                }
            );

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Update organization status API error:", error);
            return {
                success: false,
                error: "Failed to update organization status",
            };
        }
    },

    assignTokens: async (
        id: string,
        tokens: number
    ): Promise<ApiResponse<Organization>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(
                `${API_BASE_URL}/organizations/${id}/tokens`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify({ tokens }),
                }
            );

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Assign tokens API error:", error);
            return { success: false, error: "Failed to assign tokens" };
        }
    },
};

// Admin API
export const adminApi = {
    getByOrganization: async (
        organizationId: string
    ): Promise<ApiResponse<Admin[]>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(
                `${API_BASE_URL}/organizations/${organizationId}/admins`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Get admins API error:", error);
            return { success: false, error: "Failed to fetch admins" };
        }
    },

    getById: async (id: string): Promise<ApiResponse<Admin>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(`${API_BASE_URL}/admins/${id}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Get admin API error:", error);
            return { success: false, error: "Failed to fetch admin details" };
        }
    },
};

// User API
export const userApi = {
    getByAdmin: async (adminId: string): Promise<ApiResponse<User[]>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(
                `${API_BASE_URL}/admins/${adminId}/users`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Get users API error:", error);
            return { success: false, error: "Failed to fetch users" };
        }
    },

    getById: async (id: string): Promise<ApiResponse<User>> => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(`${API_BASE_URL}/users/${id}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Get user API error:", error);
            return { success: false, error: "Failed to fetch user details" };
        }
    },
};

// Analytics API
export const analyticsApi = {
    getDashboardStats: async (): Promise<
        ApiResponse<{
            totalOrganizations: number;
            totalAdmins: number;
            totalUsers: number;
            activeOrganizations: number;
            tokensUsed: number;
            tokensRemaining: number;
        }>
    > => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch(
                `${API_BASE_URL}/analytics/dashboard`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Get dashboard stats API error:", error);
            return {
                success: false,
                error: "Failed to fetch dashboard statistics",
            };
        }
    },
};

// Utility function to handle API errors
export const handleApiError = (error: any): string => {
    if (error?.response?.data?.message) {
        return error.response.data.message;
    }
    if (error?.message) {
        return error.message;
    }
    return "An unexpected error occurred";
};

// Request interceptor for adding auth token
export const setupApiInterceptors = () => {
    // This would be implemented with axios interceptors in a real application
    console.log("API interceptors setup completed");
};
