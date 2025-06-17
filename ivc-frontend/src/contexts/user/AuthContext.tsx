"use client";

import React, {
    createContext,
    useContext,
    useState,
    ReactNode,
    useEffect,
} from "react";
import { AuthApiService } from "@/services/user/authApi";

interface User {
    username: string;
    role: "admin" | "user";
    email?: string;
    userId?: string;
    isAdmin?: boolean;
}

interface AuthContextType {
    user: User | null;
    login: (
        username: string,
        password: string,
        role: "admin" | "user"
    ) => Promise<{ success: boolean; role?: "admin" | "user" }>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);

    const login = async (
        username: string,
        password: string,
        selectedRole: "admin" | "user"
    ): Promise<{ success: boolean; role?: "admin" | "user" }> => {
        try {
            console.log("Attempting login with API...");

            const authService = new AuthApiService();

            // Try API authentication first
            const apiResponse = await authService.login(username, password);

            if (apiResponse.access_token) {
                console.log("Login successful, getting user details...");

                // Get user details to determine actual role
                const userDetails = await authService.getCurrentUser();
                console.log("User details:", userDetails);

                // saving user details to local storage
                localStorage.setItem("user", JSON.stringify(userDetails));

                // Try to verify admin role first
                let actualRole: "admin" | "user" = "user";
                try {
                    await authService.verifyRole("admin");
                    actualRole = "admin";
                    console.log("User verified as admin");
                } catch (error) {
                    // If admin verification fails, try user role
                    try {
                        await authService.verifyRole("user");
                        actualRole = "user";
                        console.log("User verified as user");
                    } catch (userError) {
                        console.warn(
                            "Could not verify role, defaulting to user"
                        );
                    }
                }

                setUser({
                    username,
                    role: actualRole,
                    email: userDetails.email,
                    userId: userDetails.user_id,
                    isAdmin: actualRole === "admin",
                });

                return { success: true, role: actualRole };
            }
        } catch (error) {
            console.error("API login failed:", error);
            throw error;
        }

        return { success: false };
    };

    const logout = async () => {
        try {
            const authService = new AuthApiService();
            await authService.logout();
        } catch (error) {
            console.error("Logout failed:", error);
        }
        localStorage.removeItem("user");
        setUser(null);
    };

    // TODO: Add redirect to dashboard if user is authenticated

    useEffect(() => {
        const getLoggedInUser = async () => {
            const user = localStorage.getItem("user");

            if (user) {
                const parsedUser = JSON.parse(user);

                const verifyRole = async (role: "admin" | "user") => {
                    const authService = new AuthApiService();
                    try {
                        await authService.verifyRole(role);
                        return role;
                    } catch (error) {
                        return "user";
                    }
                };

                const actualRole = await verifyRole(parsedUser.role);

                parsedUser.role = actualRole;
                setUser(parsedUser);
            }
        };

        getLoggedInUser();
    }, []);

    const value: AuthContextType = {
        user,
        login,
        logout,
        isAuthenticated: !!user,
    };

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
};
