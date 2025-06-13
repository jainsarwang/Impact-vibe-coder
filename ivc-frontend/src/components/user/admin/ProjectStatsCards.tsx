import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Code2, Play, AlertCircle, CheckCircle } from "lucide-react";

interface Project {
    id: string;
    name: string;
    description: string;
    assignedUsers: string[];
    createdDate: string;
    status: "active" | "completed" | "paused" | "in-progress";
    category: string;
}

interface ProjectStatsCardsProps {
    projects: Project[];
}

const ProjectStatsCards = ({ projects }: ProjectStatsCardsProps) => {
    const activeProjects = projects.filter((p) => p.status === "active").length;
    const completedProjects = projects.filter(
        (p) => p.status === "completed"
    ).length;
    const pausedProjects = projects.filter((p) => p.status === "paused").length;
    const inProgressProjects = projects.filter(
        (p) => p.status === "in-progress"
    ).length;

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <Card className="border-0 shadow-sm bg-gradient-to-br from-blue-50 to-blue-100">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-blue-600 text-xs font-medium">
                                Total Projects
                            </p>
                            <p className="text-xl font-bold text-blue-800">
                                {projects.length}
                            </p>
                        </div>
                        <div className="p-1.5 bg-blue-600 rounded-lg">
                            <Code2 className="w-4 h-4 text-white" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-0 shadow-sm bg-gradient-to-br from-green-50 to-green-100">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-green-600 text-xs font-medium">
                                Active
                            </p>
                            <p className="text-xl font-bold text-green-800">
                                {activeProjects}
                            </p>
                        </div>
                        <div className="p-1.5 bg-green-600 rounded-lg">
                            <Play className="w-4 h-4 text-white" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-0 shadow-sm bg-gradient-to-br from-orange-50 to-orange-100">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-orange-600 text-xs font-medium">
                                In Progress
                            </p>
                            <p className="text-xl font-bold text-orange-800">
                                {inProgressProjects}
                            </p>
                        </div>
                        <div className="p-1.5 bg-orange-600 rounded-lg">
                            <AlertCircle className="w-4 h-4 text-white" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-0 shadow-sm bg-gradient-to-br from-purple-50 to-purple-100">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-purple-600 text-xs font-medium">
                                Completed
                            </p>
                            <p className="text-xl font-bold text-purple-800">
                                {completedProjects}
                            </p>
                        </div>
                        <div className="p-1.5 bg-purple-600 rounded-lg">
                            <CheckCircle className="w-4 h-4 text-white" />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default ProjectStatsCards;
