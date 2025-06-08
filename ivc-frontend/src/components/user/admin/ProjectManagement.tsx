import React from "react";
import { Code2 } from "lucide-react";
import ProjectStatsCards from "./ProjectStatsCards";
import ProjectCard from "./ProjectCard";
import type { User, Project } from "@/types/user/admin";

interface ProjectManagementProps {
    projects: Project[];
    users: User[];
    onAddProject: (project: {
        name: string;
        description: string;
        assignedUser: string;
        category: string;
    }) => void;
}

const ProjectManagement = ({
    projects,
    users,
    onAddProject,
}: ProjectManagementProps) => {
    return (
        <div className="space-y-6">
            {/* Project Stats */}
            <ProjectStatsCards projects={projects} />

            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-purple-600 rounded-lg">
                        <Code2 className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-slate-800">
                            Project Management
                        </h2>
                        <p className="text-sm text-slate-600">
                            Manage and track all development projects
                        </p>
                    </div>
                </div>
            </div>

            {/* Projects Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {projects.map((project) => (
                    <ProjectCard key={project.id} project={project} />
                ))}
            </div>
        </div>
    );
};

export default ProjectManagement;
