"use client";

import ProtectedRoute from "@/components/user/ProtectedRoute";
import AdminDashboard from "@/pages/user/AdminDashboard";

export default function AdminDashboardPage() {
    return (
        <ProtectedRoute requiredRole="admin">
            <AdminDashboard />
        </ProtectedRoute>
    );
}
