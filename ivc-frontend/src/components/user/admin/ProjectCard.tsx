import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Code2, Calendar } from "lucide-react";

interface Project {
    id: string;
    name: string;
    description: string;
    assignedUsers: string[];
    createdDate: string;
    status: "active" | "completed" | "paused" | "in-progress";
    category: string;
}

interface ProjectCardProps {
    project: Project;
}

const ProjectCard = ({ project }: ProjectCardProps) => {
    return (
        <Card className="border-0 shadow-md hover:shadow-lg transition-all duration-300 bg-white">
            <CardHeader className="pb-2 space-y-2">
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <CardTitle className="text-base font-semibold text-slate-800 leading-tight mb-1">
                            {project.name}
                        </CardTitle>
                        <Badge
                            variant="outline"
                            className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 border-blue-200"
                        >
                            {project.category}
                        </Badge>
                    </div>
                    <div className="p-1.5 bg-purple-100 rounded-lg ml-2">
                        <Code2 className="w-3 h-3 text-purple-600" />
                    </div>
                </div>
            </CardHeader>
            <CardContent className="pt-0 space-y-3">
                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                    {project.description}
                </p>

                <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center text-slate-500">
                        <Calendar className="w-3 h-3 mr-1" />
                        <span>{project.createdDate}</span>
                    </div>

                    <div className="text-slate-500 text-right">
                        Users: {project.assignedUsers.length}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default ProjectCard;
