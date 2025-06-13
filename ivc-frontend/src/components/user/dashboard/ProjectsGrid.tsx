import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    FolderOpen,
    Code,
    Calendar,
    Play,
    Pause,
    CheckCircle,
} from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

interface Project {
    id: string;
    name: string;
    description: string;
    status: "In Progress" | "Completed" | "Planning";
    dueDate: string;
    category: string;
}

interface ProjectsGridProps {
    projects: Project[];
    onUpdateProjectStatus?: (
        projectId: string,
        status: "In Progress" | "Completed" | "Planning"
    ) => void;
}

const ProjectsGrid = ({
    projects,
    onUpdateProjectStatus,
}: ProjectsGridProps) => {
    const { toast } = useToast();

    const handleStatusChange = (
        projectId: string,
        newStatus: "In Progress" | "Completed" | "Planning"
    ) => {
        if (onUpdateProjectStatus) {
            onUpdateProjectStatus(projectId, newStatus);
            toast({
                title: "Status Updated",
                description: "Project status has been updated successfully.",
            });
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "In Progress":
                return <Play className="w-3 h-3" />;
            case "Completed":
                return <CheckCircle className="w-3 h-3" />;
            case "Planning":
                return <Pause className="w-3 h-3" />;
            default:
                return <Code className="w-3 h-3" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "In Progress":
                return "bg-green-50 text-green-700 border-green-200";
            case "Completed":
                return "bg-blue-50 text-blue-700 border-blue-200";
            case "Planning":
                return "bg-orange-50 text-orange-700 border-orange-200";
            default:
                return "bg-gray-50 text-gray-700 border-gray-200";
        }
    };

    return (
        <Card className="border-0 shadow-lg">
            <CardHeader className="pb-4">
                <CardTitle className="flex items-center text-slate-800 text-xl">
                    <FolderOpen className="w-6 h-6 mr-3 text-blue-600" />
                    My Projects ({projects.length})
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {projects.map((project) => (
                        <div
                            key={project.id}
                            className="border border-slate-200 rounded-xl p-4 hover:shadow-md transition-all duration-200 bg-white"
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center flex-1">
                                    <Code className="w-4 h-4 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
                                    <h3 className="font-semibold text-slate-900 text-sm leading-tight">
                                        {project.name}
                                    </h3>
                                </div>

                                {onUpdateProjectStatus ? (
                                    <Select
                                        value={project.status}
                                        onValueChange={(
                                            value:
                                                | "In Progress"
                                                | "Completed"
                                                | "Planning"
                                        ) =>
                                            handleStatusChange(
                                                project.id,
                                                value
                                            )
                                        }
                                    >
                                        <SelectTrigger className="w-auto h-6 text-xs border-0 bg-transparent p-0">
                                            <Badge
                                                variant="outline"
                                                className={`${getStatusColor(
                                                    project.status
                                                )} text-xs px-2 py-1 flex items-center space-x-1 cursor-pointer hover:opacity-80`}
                                            >
                                                {getStatusIcon(project.status)}
                                                <span>{project.status}</span>
                                            </Badge>
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="Planning">
                                                <div className="flex items-center space-x-2">
                                                    <Pause className="w-4 h-4 text-orange-600" />
                                                    <span>Planning</span>
                                                </div>
                                            </SelectItem>
                                            <SelectItem value="In Progress">
                                                <div className="flex items-center space-x-2">
                                                    <Play className="w-4 h-4 text-green-600" />
                                                    <span>In Progress</span>
                                                </div>
                                            </SelectItem>
                                            <SelectItem value="Completed">
                                                <div className="flex items-center space-x-2">
                                                    <CheckCircle className="w-4 h-4 text-blue-600" />
                                                    <span>Completed</span>
                                                </div>
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>
                                ) : (
                                    <Badge
                                        variant="outline"
                                        className={`${getStatusColor(
                                            project.status
                                        )} text-xs px-2 py-1 flex items-center space-x-1`}
                                    >
                                        {getStatusIcon(project.status)}
                                        <span>{project.status}</span>
                                    </Badge>
                                )}
                            </div>

                            <p className="text-xs text-slate-600 mb-3 line-clamp-2">
                                {project.description}
                            </p>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-xs text-slate-500">
                                    <div className="flex items-center">
                                        <Calendar className="w-3 h-3 mr-1" />
                                        <span>Due: {project.dueDate}</span>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between text-xs">
                                    <span className="text-slate-500">
                                        Category:
                                    </span>
                                    <Badge
                                        variant="outline"
                                        className="text-xs px-2 py-0 bg-blue-50 text-blue-700 border-blue-200"
                                    >
                                        {project.category}
                                    </Badge>
                                </div>
                            </div>
                        </div>
                    ))}

                    {projects.length === 0 && (
                        <div className="col-span-full text-center py-12">
                            <Code className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-slate-600 mb-2">
                                No Projects Yet
                            </h3>
                            <p className="text-slate-500">
                                Create your first project to get started!
                            </p>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
};

export default ProjectsGrid;
