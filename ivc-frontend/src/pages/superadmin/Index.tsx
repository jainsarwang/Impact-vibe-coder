"use client";

import React, { useState, useEffect } from "react";
import SuperAdminLogin from "@/components/superadmin/SuperAdminLogin";
import SuperAdminDashboard from "@/components/superadmin/SuperAdminDashboard";
import { adminApiService } from "@/services/superadmin/adminApi";
import { getCookie } from "cookies-next";

const Index = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            const token = getCookie("accessToken");
            const isTestSession =
                localStorage.getItem("isTestSession") === "true";

            console.log("Checking auth status:", {
                token: !!token,
                isTestSession,
            });

            // First check if backend is reachable
            try {
                await adminApiService.healthCheck();
            } catch (healthError) {
                console.warn("Backend health check failed:", healthError);
            }

            if (token) {
                if (isTestSession) {
                    console.log(
                        "Test session detected, authenticating without API call"
                    );
                    setIsAuthenticated(true);
                } else {
                    console.log("Verifying token with backend...");
                    try {
                        await adminApiService.verifySuperAdmin();
                        console.log("Token verified successfully");
                        setIsAuthenticated(true);
                    } catch (verifyError) {
                        console.log("Token verification failed:", verifyError);
                        adminApiService.logout();
                        localStorage.removeItem("isTestSession");
                        setIsAuthenticated(false);
                    }
                }
            } else {
                console.log("No token found");
            }
        } catch (error) {
            console.log("Authentication check failed:", error);
            adminApiService.logout();
            localStorage.removeItem("isTestSession");
            setIsAuthenticated(false);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogin = () => {
        console.log("handleLogin called, setting authenticated to true");
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        console.log("handleLogout called");
        setIsAuthenticated(false);
        adminApiService.logout();
        localStorage.removeItem("isTestSession");
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="relative mb-8">
                        <div className="w-20 h-20 mx-auto relative">
                            <div className="absolute inset-0 border-4 border-blue-200 rounded-full"></div>
                            <div className="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full animate-spin"></div>
                            <div
                                className="absolute inset-2 border-4 border-transparent border-t-indigo-500 rounded-full animate-spin"
                                style={{
                                    animationDirection: "reverse",
                                    animationDuration: "1.5s",
                                }}
                            ></div>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg"></div>
                            </div>
                        </div>
                    </div>
                    <div className="space-y-3">
                        <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent">
                            Loading...
                        </h2>
                        <div className="w-32 h-1 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mx-auto opacity-60"></div>
                    </div>
                </div>
            </div>
        );
    }

    console.log("Rendering Index component:", { isAuthenticated, isLoading });

    return (
        <>
            {!isAuthenticated ? (
                <SuperAdminLogin onLogin={handleLogin} />
            ) : (
                <SuperAdminDashboard onLogout={handleLogout} />
            )}
        </>
    );
};

export default Index;
