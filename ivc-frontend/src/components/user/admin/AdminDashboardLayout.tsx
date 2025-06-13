import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AdminHeader from "./AdminHeader";
import UserManagement from "./UserManagement";
import ProjectManagement from "./ProjectManagement";
import type { User, Project, Settings } from "@/types/user/admin";

interface AdminDashboardLayoutProps {
    username: string;
    onLogout: () => void;
    users: User[];
    projects: Project[];
    settings: Settings;
    onToggleUserStatus: (userId: string) => void;
    onUpdateUserTokens: (userId: string, newTokens: number) => void;
    onDistributeTokensEqually: () => void;
    onAddUser: (user: {
        username: string;
        email: string;
        tokens: number;
    }) => void;
    onAddProject: (project: {
        name: string;
        description: string;
        assignedUser: string;
        category: string;
        status?: string;
    }) => void;
    onSettingsChange: (settings: Settings) => void;
}

const AdminDashboardLayout = ({
    username,
    onLogout,
    users,
    projects,
    settings,
    onToggleUserStatus,
    onUpdateUserTokens,
    onDistributeTokensEqually,
    onAddUser,
    onAddProject,
    onSettingsChange,
}: AdminDashboardLayoutProps) => {
    const [activeTab, setActiveTab] = useState("users");

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-orange-50">
            <AdminHeader
                username={username}
                onLogout={onLogout}
                organizationName={settings.organizationName}
            />

            <main className="container mx-auto px-4 py-8">
                <Tabs
                    value={activeTab}
                    onValueChange={setActiveTab}
                    className="w-full"
                >
                    <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
                        <TabsTrigger
                            value="users"
                            className="text-sm font-medium"
                        >
                            Users
                        </TabsTrigger>
                        <TabsTrigger
                            value="projects"
                            className="text-sm font-medium"
                        >
                            Projects
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="users" className="space-y-6">
                        <UserManagement
                            users={users}
                            onToggleUserStatus={onToggleUserStatus}
                            onUpdateUserTokens={onUpdateUserTokens}
                            onDistributeTokensEqually={
                                onDistributeTokensEqually
                            }
                            onAddUser={onAddUser}
                            defaultTokenAllocation={
                                settings.defaultTokenAllocation
                            }
                            organizationName={settings.organizationName}
                        />
                    </TabsContent>

                    <TabsContent value="projects" className="space-y-6">
                        <ProjectManagement
                            projects={projects}
                            users={users}
                            onAddProject={onAddProject}
                        />
                    </TabsContent>
                </Tabs>
            </main>
        </div>
    );
};

export default AdminDashboardLayout;
