import { useToast } from "@/hooks/user/use-toast";
import { AdminUserService } from "@/services/user/adminUserService";
import type { User } from "@/types/user/admin";
import { useState } from "react";

export const useUserActions = (
    users: User[],
    currentOrgId: string,
    {
        toggleUserActiveStatus,
        updateUserTokensState,
        distributeTokensEquallyState,
        addUser,
    }: {
        toggleUserActiveStatus: (userId: string) => void;
        updateUserTokensState: (userId: string, tokens: number) => void;
        distributeTokensEquallyState: () => number;
        addUser: (user: User) => void;
    }
) => {
    const { toast } = useToast();
    const adminUserService = new AdminUserService();
    const [userCredentials, setUserCredentials] = useState<{
        username: string;
        password: string;
    } | null>(null);
    const [showCredentialsDialog, setShowCredentialsDialog] = useState(false);

    const toggleUserStatus = async (userId: string) => {
        try {
            await adminUserService.toggleUserStatus(userId);
            toggleUserActiveStatus(userId);

            const user = users.find((u) => u.id === userId);
            if (user) {
                toast({
                    title: "User Status Updated",
                    description: `${user.username} has been ${
                        user.isActive ? "deactivated" : "activated"
                    }.`,
                    duration: 3000,
                });
            }
        } catch (error) {
            console.error("Failed to toggle user status:", error);
            toast({
                title: "Error",
                description: "Failed to update user status. Please try again.",
                variant: "destructive",
            });
        }
    };

    const updateUserTokens = async (userId: string, newTokens: number) => {
        try {
            await adminUserService.updateUserTokens(userId, newTokens);
            updateUserTokensState(userId, newTokens);

            toast({
                title: "Tokens Updated",
                description: "User tokens have been updated successfully.",
                duration: 3000,
            });
        } catch (error) {
            console.error("Failed to update user tokens:", error);
            toast({
                title: "Error",
                description: "Failed to update user tokens. Please try again.",
                variant: "destructive",
            });
        }
    };

    const distributeTokensEqually = async () => {
        try {
            if (!currentOrgId) {
                throw new Error("Organization ID not available");
            }

            await adminUserService.distributeTokensEqually(currentOrgId);
            const tokensPerUser = distributeTokensEquallyState();

            toast({
                title: "Tokens Distributed",
                description: `${tokensPerUser} tokens distributed to each active user.`,
                duration: 3000,
            });
        } catch (error) {
            console.error("Failed to distribute tokens:", error);
            toast({
                title: "Error",
                description: "Failed to distribute tokens. Please try again.",
                variant: "destructive",
            });
        }
    };

    const createUser = async (newUser: {
        username: string;
        email: string;
        tokens: number;
    }) => {
        try {
            const createdUser = await adminUserService.createUser({
                name: newUser.username,
                email: newUser.email,
                tokens: newUser.tokens,
            });

            const user: User = {
                id: createdUser.user_id || (users.length + 1).toString(),
                username: createdUser.username || newUser.username,
                password: createdUser.password, // Password should be handled securely, not stored in plain text
                email: newUser.email,
                isActive: true,
                tokensLeft: newUser.tokens,
                tokensUsed: 0,
                totalTokens: newUser.tokens,
                lastLogin: "Never",
                projects: [],
            };

            addUser(user);

            // Set the credentials and show dialog
            setUserCredentials({
                username: createdUser.username,
                password: createdUser.password,
            });
            setShowCredentialsDialog(true);

            toast({
                title: "User Created",
                description: `User ${user.username} password ${user.password} has been created successfully.`,
                duration: 3000,
            });
        } catch (error) {
            console.error("Failed to create user:", error);
            toast({
                title: "Error",
                description: "Failed to create user. Please try again.",
                variant: "destructive",
            });
        }
    };

    const closeCredentialsDialog = () => {
        setShowCredentialsDialog(false);
    };

    return {
        toggleUserStatus,
        updateUserTokens,
        distributeTokensEqually,
        addUser: createUser,
        userCredentials,
        showCredentialsDialog,
        closeCredentialsDialog,
    };
};
