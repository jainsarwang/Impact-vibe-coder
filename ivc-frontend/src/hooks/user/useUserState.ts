import { useState } from "react";
import type { User } from "@/types/user/admin";

export const useUserState = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [currentOrgId, setCurrentOrgId] = useState<string>("");

    const updateUsers = (newUsers: User[]) => {
        setUsers(newUsers);
    };

    const updateUser = (userId: string, updates: Partial<User>) => {
        setUsers(
            users.map((user) =>
                user.id === userId ? { ...user, ...updates } : user
            )
        );
    };

    const addUser = (user: User) => {
        setUsers([...users, user]);
    };

    const toggleUserActiveStatus = (userId: string) => {
        setUsers(
            users.map((user) =>
                user.id === userId
                    ? { ...user, isActive: !user.isActive }
                    : user
            )
        );
    };

    const updateUserTokensState = (userId: string, newTokens: number) => {
        setUsers(
            users.map((user) =>
                user.id === userId
                    ? {
                          ...user,
                          tokensLeft: newTokens,
                          totalTokens: newTokens + user.tokensUsed,
                      }
                    : user
            )
        );
    };

    const distributeTokensEquallyState = () => {
        const activeUsers = users.filter((user) => user.isActive);
        const totalAvailableTokens = activeUsers.reduce(
            (sum, user) => sum + user.tokensLeft,
            0
        );
        const tokensPerUser = Math.floor(
            totalAvailableTokens / activeUsers.length
        );

        setUsers(
            users.map((user) => {
                if (user.isActive) {
                    return {
                        ...user,
                        tokensLeft: tokensPerUser,
                        totalTokens: tokensPerUser + user.tokensUsed,
                    };
                }
                return user;
            })
        );

        return tokensPerUser;
    };

    return {
        users,
        currentOrgId,
        setCurrentOrgId,
        updateUsers,
        updateUser,
        addUser,
        toggleUserActiveStatus,
        updateUserTokensState,
        distributeTokensEquallyState,
    };
};
