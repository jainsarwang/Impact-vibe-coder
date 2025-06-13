import { AdminApiService } from "./adminApi";
import { OrganizationApiService } from "./organizationApi";
import type { User } from "@/types/user/admin";

export class AdminUserService {
    private adminApiService: AdminApiService;
    private organizationApiService: OrganizationApiService;

    constructor() {
        this.adminApiService = new AdminApiService();
        this.organizationApiService = new OrganizationApiService();
    }

    async loadUsers(): Promise<{ users: User[]; orgId: string }> {
        const dashboardData =
            await this.adminApiService.getAdminDashboardData();
        let orgId = "";

        if (dashboardData.settings?.organizationName) {
            try {
                const orgData =
                    await this.organizationApiService.getAllOrganizations();
                const org = orgData.organizations?.find(
                    (o: any) =>
                        o.organization_name ===
                        dashboardData.settings.organizationName
                );
                if (org) {
                    orgId = org.organization_id;
                }
            } catch (error) {
                console.warn("Could not fetch organization ID");
            }
        }

        return {
            users: dashboardData.users || [],
            orgId,
        };
    }

    async toggleUserStatus(userId: string): Promise<void> {
        await this.adminApiService.toggleUserStatus(userId);
    }

    async updateUserTokens(userId: string, tokens: number): Promise<void> {
        await this.adminApiService.updateUserTokens(userId, tokens);
    }

    async distributeTokensEqually(orgId: string): Promise<void> {
        await this.adminApiService.distributeTokensEqually(orgId);
    }

    async createUser(userData: {
        name: string;
        email: string;
        tokens: number;
    }): Promise<any> {
        return await this.adminApiService.createUser(userData);
    }
}
