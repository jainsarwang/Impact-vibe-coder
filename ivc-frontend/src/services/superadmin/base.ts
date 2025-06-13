import { getCookie } from "cookies-next";

export const baseURL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const getAuthHeaders = (): { [key: string]: string } => {
    const accessToken = getCookie("accessToken");
    return accessToken
        ? {
              "Content-Type": "application/json",
              Authorization: `Bearer ${accessToken}`,
          }
        : { "Content-Type": "application/json" };
};

export const handleApiError = (error: any): never => {
    console.error("API Error:", error);
    throw error;
};

export const healthCheck = async (): Promise<any> => {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

        const response = await fetch(`${baseURL}/health`, {
            method: "GET",
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(
                `Health check failed with status: ${response.status}`
            );
        }

        return await response.json();
    } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
            console.error("Health check timeout");
            throw new Error(
                "Health check timeout - backend may be unreachable"
            );
        }
        console.error("Health check error:", error);
        throw error;
    }
};
