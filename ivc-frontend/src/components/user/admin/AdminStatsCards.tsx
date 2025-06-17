import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Building2, Coins, FolderOpen, TrendingUp } from "lucide-react";

interface AdminStatsCardsProps {
    totalOrganizations: number;
    totalTokensAvailable: number;
    totalTokensUsed: number;
    activeProjects: number;
}

const formatNumber = (num: number): string => {
    if (num >= 100000) {
        return `${(num / 100000).toFixed(1)}L`;
    }
    if (num >= 1000) {
        return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
};

const AdminStatsCards = ({
    totalOrganizations,
    totalTokensAvailable,
    totalTokensUsed,
    activeProjects,
}: AdminStatsCardsProps) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <Building2 className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-blue-100">
                                Total Organizations
                            </p>
                            <p className="text-xl font-bold text-white">
                                {totalOrganizations}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-emerald-500 to-green-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <Coins className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-green-100">
                                Available Tokens
                            </p>
                            <p className="text-xl font-bold text-white">
                                {formatNumber(totalTokensAvailable)}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-amber-500 to-orange-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-orange-100">
                                Used Tokens
                            </p>
                            <p className="text-xl font-bold text-white">
                                {formatNumber(totalTokensUsed)}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white border-0">
                <CardContent className="p-4">
                    <div className="flex items-center">
                        <div className="p-2 bg-white/20 rounded-lg">
                            <FolderOpen className="w-5 h-5 text-white" />
                        </div>
                        <div className="ml-3">
                            <p className="text-xs font-medium text-purple-100">
                                Active Projects
                            </p>
                            <p className="text-xl font-bold text-white">
                                {activeProjects}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default AdminStatsCards;
