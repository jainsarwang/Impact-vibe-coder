import { useState } from "react";
import { AdminApiService } from "@/services/user/adminApi";
import type { Project } from "@/types/user/admin";

export const useAdminProjects = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const adminApiService = new AdminApiService();

    const loadProjects = async () => {
        try {
            const dashboardData = await adminApiService.getAdminDashboardData();
            if (dashboardData.projects) {
                setProjects(dashboardData.projects);
                console.log(
                    "Projects loaded from API:",
                    dashboardData.projects
                );
            }
        } catch (error) {
            console.warn("Failed to load projects from API:", error);
        }
    };

    const addProject = async (newProject: {
        name: string;
        description: string;
        assignedUser: string;
        category: string;
    }) => {
        try {
            const createdProject = await adminApiService.createProject({
                name: newProject.name,
                description: newProject.description,
                assignedUser: newProject.assignedUser,
                category: newProject.category,
                status: "active",
            });

            const project: Project = {
                id:
                    createdProject.project_id ||
                    (projects.length + 1).toString(),
                name: newProject.name,
                description: newProject.description,
                assignedUsers: newProject.assignedUser
                    ? [newProject.assignedUser]
                    : [],
                createdDate: new Date().toISOString().split("T")[0],
                status: "active",
                category: newProject.category,
            };

            setProjects([...projects, project]);
        } catch (error) {
            console.error("Failed to create project:", error);
            const project: Project = {
                id: (projects.length + 1).toString(),
                name: newProject.name,
                description: newProject.description,
                assignedUsers: newProject.assignedUser
                    ? [newProject.assignedUser]
                    : [],
                createdDate: new Date().toISOString().split("T")[0],
                status: "active",
                category: newProject.category,
            };

            setProjects([...projects, project]);
        }
    };

    return {
        projects,
        loadProjects,
        addProject,
    };
};
