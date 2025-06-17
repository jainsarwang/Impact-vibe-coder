import React, { useEffect } from "react";
import { useAuth } from "@/contexts/user/AuthContext";
import { useAdminData } from "@/hooks/user/useAdminData";
import AdminDashboardLayout from "@/components/user/admin/AdminDashboardLayout";
import UserCredentialsDialog from "@/components/user/admin/UserCredentialsDialog";

const AdminDashboard = () => {
    const { user, logout } = useAuth();
    const {
        users,
        projects,
        settings,
        loading,
        setSettings,
        loadData,
        toggleUserStatus,
        updateUserTokens,
        distributeTokensEqually,
        addUser,
        addProject,
        userCredentials,
        showCredentialsDialog,
        closeCredentialsDialog,
    } = useAdminData();

    useEffect(() => {
        loadData();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-orange-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <>
            <AdminDashboardLayout
                username={user?.username || ""}
                onLogout={logout}
                users={users}
                projects={projects}
                settings={settings}
                onToggleUserStatus={toggleUserStatus}
                onUpdateUserTokens={updateUserTokens}
                onDistributeTokensEqually={distributeTokensEqually}
                onAddUser={addUser}
                onAddProject={addProject}
                onSettingsChange={setSettings}
            />
            <UserCredentialsDialog
                isOpen={showCredentialsDialog}
                onClose={closeCredentialsDialog}
                credentials={userCredentials}
            />
        </>
    );
};

export default AdminDashboard;
