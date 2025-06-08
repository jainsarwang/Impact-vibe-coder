import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Plus, Save, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

interface NewProject {
    name: string;
    description: string;
    dueDate: string;
    category: string;
}

interface CreateProjectProps {
    onCreateProject: (project: NewProject) => void;
}

const PROJECT_CATEGORIES = [
    "Frontend Development",
    "Backend Development",
    "Full-Stack Development",
    "Mobile App Development",
    "UI/UX Design",
    "Machine Learning",
    "Artificial Intelligence",
    "Generative AI",
    "Deep Learning",
    "Computer Vision",
    "Natural Language Processing",
    "Data Science",
    "Data Analytics",
    "DevOps",
    "Cloud Computing",
    "Blockchain",
    "Web3 Development",
    "IoT Development",
    "Game Development",
    "API Development",
    "Database Design",
    "Cybersecurity",
    "Quality Assurance",
    "Automation Testing",
    "Microservices",
    "Serverless Computing",
    "Edge Computing",
    "Augmented Reality",
    "Virtual Reality",
    "Quantum Computing",
];

const CreateProject = ({ onCreateProject }: CreateProjectProps) => {
    const { toast } = useToast();
    const [showCreateProject, setShowCreateProject] = useState(false);
    const [newProject, setNewProject] = useState<NewProject>({
        name: "",
        description: "",
        dueDate: "",
        category: "",
    });

    const handleCreateProject = () => {
        window.location.href = "http://localhost:3000";
        if (!newProject.name || !newProject.description) {
            toast({
                title: "Missing Information",
                description: "Please fill in project name and description.",
                variant: "destructive",
            });
            return;
        }

        onCreateProject(newProject);

        toast({
            title: "Project Created",
            description: `${newProject.name} has been created successfully!`,
        });

        setNewProject({ name: "", description: "", dueDate: "", category: "" });
        setShowCreateProject(false);
    };

    return (
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardHeader className="pb-4">
                <CardTitle className="flex items-center justify-between text-slate-800 text-lg">
                    <div className="flex items-center">
                        <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                        New Project
                    </div>
                    <Button
                        onClick={() => setShowCreateProject(!showCreateProject)}
                        size="sm"
                        className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700"
                    >
                        <Plus className="w-4 h-4" />
                    </Button>
                </CardTitle>
            </CardHeader>
            {showCreateProject && (
                <CardContent className="space-y-4">
                    <div>
                        <Label
                            htmlFor="projectName"
                            className="text-sm font-medium text-slate-700"
                        >
                            Project Name
                        </Label>
                        <Input
                            id="projectName"
                            value={newProject.name}
                            onChange={(e) =>
                                setNewProject({
                                    ...newProject,
                                    name: e.target.value,
                                })
                            }
                            placeholder="Enter project name"
                            className="mt-1 h-9 border-slate-300 focus:border-blue-500"
                        />
                    </div>

                    <div>
                        <Label
                            htmlFor="projectDesc"
                            className="text-sm font-medium text-slate-700"
                        >
                            Description
                        </Label>
                        <Textarea
                            id="projectDesc"
                            value={newProject.description}
                            onChange={(e) =>
                                setNewProject({
                                    ...newProject,
                                    description: e.target.value,
                                })
                            }
                            placeholder="Describe your project goals and requirements"
                            className="mt-1 border-slate-300 focus:border-blue-500"
                            rows={3}
                        />
                    </div>

                    <div>
                        <Label
                            htmlFor="projectCategory"
                            className="text-sm font-medium text-slate-700"
                        >
                            Technology Category
                        </Label>
                        <Select
                            value={newProject.category}
                            onValueChange={(value) =>
                                setNewProject({
                                    ...newProject,
                                    category: value,
                                })
                            }
                        >
                            <SelectTrigger className="mt-1 h-9 border-slate-300 focus:border-blue-500">
                                <SelectValue placeholder="Select technology stack" />
                            </SelectTrigger>
                            <SelectContent className="max-h-60">
                                {PROJECT_CATEGORIES.map((category) => (
                                    <SelectItem key={category} value={category}>
                                        {category}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div>
                        <Label
                            htmlFor="projectDue"
                            className="text-sm font-medium text-slate-700"
                        >
                            Target Completion Date
                        </Label>
                        <Input
                            id="projectDue"
                            type="date"
                            value={newProject.dueDate}
                            onChange={(e) =>
                                setNewProject({
                                    ...newProject,
                                    dueDate: e.target.value,
                                })
                            }
                            className="mt-1 h-9 border-slate-300 focus:border-blue-500"
                        />
                    </div>

                    <Button
                        onClick={handleCreateProject}
                        className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 h-9"
                    >
                        <Save className="w-4 h-4 mr-2" />
                        Create Project
                    </Button>
                </CardContent>
            )}
        </Card>
    );
};

export default CreateProject;
