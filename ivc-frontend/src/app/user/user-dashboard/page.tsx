"use client";

import ProtectedRoute from "@/components/user/ProtectedRoute";
import UserDashboard from "@/pages/user/UserDashboard";

export default function UserDashboardPage() {
    return (
        <ProtectedRoute requiredRole="user">
            <UserDashboard />
        </ProtectedRoute>
    );
}
