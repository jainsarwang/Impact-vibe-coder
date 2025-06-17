import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Coins, FolderOpen, TrendingUp, CheckCircle } from "lucide-react";

interface Project {
    id: string;
    name: string;
    description: string;
    status: "In Progress" | "Completed" | "Planning";
    dueDate: string;
    category: string;
}

interface StatsOverviewProps {
    tokensLeft: number;
    tokensUsed: number;
    projects: Project[];
}

const StatsOverview = ({
    tokensLeft,
    tokensUsed,
    projects,
}: StatsOverviewProps) => {
    const activeProjects = projects.filter(
        (p) => p.status !== "Completed"
    ).length;
    const completedProjects = projects.filter(
        (p) => p.status === "Completed"
    ).length;

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-amber-500 to-orange-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <Coins className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-orange-100">
                                Tokens Available
                            </p>
                            <p className="text-xl font-bold text-white">
                                {tokensLeft}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-green-100">
                                Tokens Used
                            </p>
                            <p className="text-xl font-bold text-white">
                                {tokensUsed}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <FolderOpen className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-blue-100">
                                Active Projects
                            </p>
                            <p className="text-xl font-bold text-white">
                                {activeProjects}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <CheckCircle className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-purple-100">
                                Completed
                            </p>
                            <p className="text-xl font-bold text-white">
                                {completedProjects}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default StatsOverview;
