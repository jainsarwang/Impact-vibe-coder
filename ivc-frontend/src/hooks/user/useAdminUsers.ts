import { AdminUserService } from "@/services/user/adminUserService";
import { useUserState } from "./useUserState";
import { useUserActions } from "./useUserActions";

export const useAdminUsers = () => {
    const adminUserService = new AdminUserService();

    const {
        users,
        currentOrgId,
        setCurrentOrgId,
        updateUsers,
        toggleUserActiveStatus,
        updateUserTokensState,
        distributeTokensEquallyState,
        addUser: addUserToState,
    } = useUserState();

    const {
        toggleUserStatus,
        updateUserTokens,
        distributeTokensEqually,
        addUser,
        userCredentials,
        showCredentialsDialog,
        closeCredentialsDialog,
    } = useUserActions(users, currentOrgId, {
        toggleUserActiveStatus,
        updateUserTokensState,
        distributeTokensEquallyState,
        addUser: addUserToState,
    });

    const loadUsers = async () => {
        try {
            const { users: loadedUsers, orgId } =
                await adminUserService.loadUsers();
            if (loadedUsers && loadedUsers.length > 0) {
                updateUsers(loadedUsers);
                console.log("Users loaded from API:", loadedUsers);
                setCurrentOrgId(orgId);
            }
        } catch (error) {
            console.error("Failed to load users:", error);
        }
    };

    return {
        users,
        loadUsers,
        toggleUserStatus,
        updateUserTokens,
        distributeTokensEqually,
        addUser,
        userCredentials,
        showCredentialsDialog,
        closeCredentialsDialog,
    };
};
