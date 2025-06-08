const API_BASE_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export class BaseApiService {
    protected baseURL: string;
    protected token: string | null = null;

    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = localStorage.getItem("authToken");
    }

    protected getAuthHeaders() {
        // Ensure we have the latest token
        this.token = localStorage.getItem("authToken");

        return {
            "Content-Type": "application/json",
            ...(this.token && { Authorization: `Bearer ${this.token}` }),
        };
    }

    protected async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;

        const config: RequestInit = {
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers,
            },
            ...options,
        };

        try {
            console.log(`Making API request to: ${url}`, {
                method: config.method || "GET",
            });

            const response = await fetch(url, config);

            console.log(`API response status: ${response.status}`);

            if (!response.ok) {
                if (response.status === 401) {
                    console.error("Authentication failed - clearing token");
                    this.clearToken();
                    // Redirect to login or throw specific auth error
                    window.location.href = "/";
                    throw new Error(
                        "Authentication failed - please log in again"
                    );
                }
                if (response.status === 403) {
                    console.warn("Access forbidden - insufficient permissions");
                    throw new Error(
                        "Access forbidden - insufficient permissions"
                    );
                }
                const errorData = await response.text();
                throw new Error(
                    `HTTP error! status: ${response.status}, message: ${errorData}`
                );
            }

            const data = await response.json();
            console.log("API response data:", data);
            return data;
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    protected setToken(token: string) {
        this.token = token;
        localStorage.setItem("authToken", token);
        console.log("Token set in localStorage");
    }

    protected clearToken() {
        this.token = null;
        localStorage.removeItem("authToken");
        console.log("Token cleared from localStorage");
    }
}
