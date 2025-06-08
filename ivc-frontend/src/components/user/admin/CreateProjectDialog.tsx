import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Plus } from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

interface User {
    id: string;
    username: string;
    email: string;
    isActive: boolean;
    tokensLeft: number;
    tokensUsed: number;
    totalTokens: number;
}

interface CreateProjectDialogProps {
    users: User[];
    onAddProject: (project: {
        name: string;
        description: string;
        assignedUser: string;
        category: string;
    }) => void;
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
    "Data Science",
    "DevOps",
    "Cloud Computing",
    "Blockchain",
    "IoT Development",
    "Game Development",
    "API Development",
    "Database Design",
    "Cybersecurity",
    "Quality Assurance",
];

const CreateProjectDialog = ({
    users,
    onAddProject,
}: CreateProjectDialogProps) => {
    const { toast } = useToast();
    const [newProject, setNewProject] = useState({
        name: "",
        description: "",
        assignedUser: "",
        category: "",
    });

    const handleAddProject = () => {
        if (
            !newProject.name ||
            !newProject.description ||
            !newProject.category
        ) {
            toast({
                title: "Validation Error",
                description: "Please fill in all required fields.",
                variant: "destructive",
                duration: 3000,
            });
            return;
        }

        onAddProject(newProject);
        setNewProject({
            name: "",
            description: "",
            assignedUser: "",
            category: "",
        });
        toast({
            title: "Project Created",
            description: `${newProject.name} has been created successfully.`,
            duration: 3000,
        });
    };

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-700 hover:to-violet-700">
                    <Plus className="w-4 h-4 mr-2" />
                    <a href="http://localhost:3000">Create Project</a>
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                    <DialogTitle className="text-xl font-semibold">
                        Create New Project
                    </DialogTitle>
                </DialogHeader>
                <div className="space-y-6 pt-4">
                    <div className="space-y-2">
                        <Label
                            htmlFor="projectName"
                            className="text-sm font-medium"
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
                            className="h-11"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label
                            htmlFor="projectDescription"
                            className="text-sm font-medium"
                        >
                            Description
                        </Label>
                        <Textarea
                            id="projectDescription"
                            value={newProject.description}
                            onChange={(e) =>
                                setNewProject({
                                    ...newProject,
                                    description: e.target.value,
                                })
                            }
                            placeholder="Describe the project goals and requirements"
                            rows={3}
                        />
                    </div>
                    <div className="space-y-2">
                        <Label
                            htmlFor="projectCategory"
                            className="text-sm font-medium"
                        >
                            Category
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
                            <SelectTrigger className="h-11">
                                <SelectValue placeholder="Select project category" />
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
                    <div className="space-y-2">
                        <Label
                            htmlFor="assignUser"
                            className="text-sm font-medium"
                        >
                            Assign to User (Optional)
                        </Label>
                        <Select
                            value={newProject.assignedUser}
                            onValueChange={(value) =>
                                setNewProject({
                                    ...newProject,
                                    assignedUser: value,
                                })
                            }
                        >
                            <SelectTrigger className="h-11">
                                <SelectValue placeholder="Select a user" />
                            </SelectTrigger>
                            <SelectContent>
                                {users
                                    .filter((user) => user.isActive)
                                    .map((user) => (
                                        <SelectItem
                                            key={user.id}
                                            value={user.username}
                                        >
                                            {user.username} - {user.email}
                                        </SelectItem>
                                    ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <Button
                        onClick={handleAddProject}
                        className="w-full h-11 bg-gradient-to-r from-purple-600 to-violet-600"
                    >
                        <a href="http://localhost:3000">Create Project</a>
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default CreateProjectDialog;
