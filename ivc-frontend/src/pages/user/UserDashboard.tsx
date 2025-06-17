import React, { useState, useEffect } from "react";
import { useAuth } from "@/contexts/user/AuthContext";
import { apiService } from "@/services/user/api";
import { useToast } from "@/hooks/user/use-toast";
import UserHeader from "@/components/user/dashboard/UserHeader";
import StatsOverview from "@/components/user/dashboard/StatsOverview";
import TokenOverview from "@/components/user/dashboard/TokenOverview";
import CreateProject from "@/components/user/dashboard/CreateProject";
import ProjectsGrid from "@/components/user/dashboard/ProjectsGrid";

interface Project {
    id: string;
    name: string;
    description: string;
    status: "In Progress" | "Completed" | "Planning";
    dueDate: string;
    category: string;
}

interface NewProject {
    name: string;
    description: string;
    dueDate: string;
    category: string;
}

interface UserData {
    username: string;
    email: string;
    tokensLeft: number;
    tokensUsed: number;
    totalTokens: number;
    projects: Project[];
}

const UserDashboard = () => {
    const { user, logout } = useAuth();
    const { toast } = useToast();
    const [loading, setLoading] = useState(true);
    const [userData, setUserData] = useState<UserData>({
        username: user?.username || "User",
        email: "user@example.com",
        tokensLeft: 750,
        tokensUsed: 250,
        totalTokens: 1000,
        projects: [],
    });

    const loadUserData = async () => {
        setLoading(true);
        try {
            console.log("Loading user dashboard data...");
            const dashboardData = await apiService.getUserDashboardData();
            console.log("Dashboard data loaded:", dashboardData);

            const formattedProjects: Project[] = dashboardData.projects.map(
                (proj: any) => ({
                    id: proj.project_id || proj.id || Math.random().toString(),
                    name: proj.project_name || proj.name,
                    description: proj.description,
                    status: proj.is_deployed ? "Completed" : "In Progress",
                    dueDate:
                        proj.created_at?.split("T")[0] ||
                        new Date().toISOString().split("T")[0],
                    category: "General",
                })
            );

            setUserData({
                username: dashboardData.user.username,
                email: dashboardData.user.email,
                tokensLeft: dashboardData.user.tokensLeft,
                tokensUsed: dashboardData.user.tokensUsed,
                totalTokens: dashboardData.user.totalTokens,
                projects: formattedProjects,
            });

            toast({
                title: "Dashboard Loaded",
                description: "Successfully connected to API.",
                variant: "default",
            });
        } catch (error) {
            console.error("Failed to load user data:", error);
            toast({
                title: "API Connection Issue",
                description: "Using demo data. API connection failed.",
                variant: "destructive",
            });

            // Enhanced demo data with more realistic projects
            setUserData((prev) => ({
                ...prev,
                projects: [
                    {
                        id: "1",
                        name: "E-commerce Platform",
                        description:
                            "Building a comprehensive e-commerce solution with React, Node.js, and MongoDB",
                        status: "In Progress",
                        dueDate: "2024-06-15",
                        category: "Full-Stack Development",
                    },
                    {
                        id: "2",
                        name: "AI Chatbot Interface",
                        description:
                            "Developing an intelligent chatbot using GPT API and modern UI components",
                        status: "Completed",
                        dueDate: "2024-05-20",
                        category: "Artificial Intelligence",
                    },
                    {
                        id: "3",
                        name: "Data Analytics Dashboard",
                        description:
                            "Creating interactive dashboards for business intelligence and data visualization",
                        status: "Planning",
                        dueDate: "2024-07-01",
                        category: "Data Science",
                    },
                    {
                        id: "4",
                        name: "Machine Learning Model",
                        description:
                            "Training and deploying ML models for predictive analytics",
                        status: "In Progress",
                        dueDate: "2024-08-15",
                        category: "Machine Learning",
                    },
                ],
            }));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadUserData();
    }, []);

    const handleCreateProject = async (newProject: NewProject) => {
        try {
            const createdProject = await apiService.createProject({
                name: newProject.name,
                description: newProject.description,
                category: newProject.category,
            });

            const project: Project = {
                id:
                    createdProject.project_id ||
                    (userData.projects.length + 1).toString(),
                name: newProject.name,
                description: newProject.description,
                status: "Planning",
                dueDate:
                    newProject.dueDate ||
                    new Date().toISOString().split("T")[0],
                category: newProject.category || "General",
            };

            setUserData((prev) => ({
                ...prev,
                projects: [...prev.projects, project],
            }));

            toast({
                title: "Project Created",
                description: `${newProject.name} has been created successfully.`,
            });
        } catch (error) {
            console.error("Failed to create project:", error);

            // Fallback: Add project locally for demo
            const project: Project = {
                id: (userData.projects.length + 1).toString(),
                name: newProject.name,
                description: newProject.description,
                status: "Planning",
                dueDate:
                    newProject.dueDate ||
                    new Date().toISOString().split("T")[0],
                category: newProject.category || "General",
            };

            setUserData((prev) => ({
                ...prev,
                projects: [...prev.projects, project],
            }));

            toast({
                title: "Project Created (Demo)",
                description: `${newProject.name} has been created locally.`,
            });
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
            <UserHeader username={userData.username} onLogout={logout} />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <StatsOverview
                    tokensLeft={userData.tokensLeft}
                    tokensUsed={userData.tokensUsed}
                    projects={userData.projects}
                />

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    <div className="lg:col-span-1 space-y-6">
                        <TokenOverview
                            tokensLeft={userData.tokensLeft}
                            tokensUsed={userData.tokensUsed}
                            totalTokens={userData.totalTokens}
                        />
                        <CreateProject onCreateProject={handleCreateProject} />
                    </div>

                    <div className="lg:col-span-3">
                        <ProjectsGrid projects={userData.projects} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDashboard;
