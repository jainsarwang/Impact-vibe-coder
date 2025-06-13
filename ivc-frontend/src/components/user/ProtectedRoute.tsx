"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/user/AuthContext";

interface ProtectedRouteProps {
    children: React.ReactNode;
    requiredRole?: "admin" | "user";
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    requiredRole,
}) => {
    const loginUrl = "/user";
    const router = useRouter();
    const { user, isAuthenticated } = useAuth();

    useEffect(() => {
        if (!isAuthenticated) {
            router.replace(loginUrl);
            return;
        }

        if (requiredRole && user?.role !== requiredRole) {
            router.replace(loginUrl);
            return;
        }
    }, [isAuthenticated, user, requiredRole, router]);

    if (!isAuthenticated || (requiredRole && user?.role !== requiredRole)) {
        return null;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
