import { useState, useEffect } from "react";
import { useToast } from "@/hooks/user/use-toast";
import { useAdminUsers } from "./useAdminUsers";
import { useAdminProjects } from "./useAdminProjects";
import { useAdminSettings } from "./useAdminSettings";

export const useAdminData = () => {
    const { toast } = useToast();
    const [loading, setLoading] = useState(false);

    const {
        users,
        loadUsers,
        toggleUserStatus,
        updateUserTokens,
        distributeTokensEqually,
        addUser,
        userCredentials,
        showCredentialsDialog,
        closeCredentialsDialog,
    } = useAdminUsers();

    const { projects, loadProjects, addProject } = useAdminProjects();

    const { settings, setSettings } = useAdminSettings();

    const loadData = async () => {
        setLoading(true);
        try {
            console.log("Loading admin data from API...");

            await Promise.all([loadUsers(), loadProjects()]);
        } catch (error) {
            console.error("Failed to load data from API:", error);
            toast({
                title: "Warning",
                description: "Using demo data. Check API connection.",
                variant: "destructive",
                duration: 3000,
            });
        } finally {
            setLoading(false);
        }
    };

    return {
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
    };
};
