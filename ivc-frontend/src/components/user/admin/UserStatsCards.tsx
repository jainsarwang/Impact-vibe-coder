import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Users, UserCheck, Coins, Building2 } from "lucide-react";

interface User {
    id: string;
    username: string;
    email: string;
    isActive: boolean;
    tokensLeft: number;
    tokensUsed: number;
    totalTokens: number;
}

interface UserStatsCardsProps {
    users: User[];
    organizationName?: string;
}

const UserStatsCards = ({ users, organizationName }: UserStatsCardsProps) => {
    const totalUsers = users.length;
    const activeUsers = users.filter((user) => user.isActive).length;
    const totalTokens = users.reduce((sum, user) => sum + user.totalTokens, 0);
    const tokensUsed = users.reduce((sum, user) => sum + user.tokensUsed, 0);

    const formatNumber = (num: number): string => {
        if (num >= 100000) {
            return `${(num / 100000).toFixed(1)}L`;
        }
        if (num >= 1000) {
            return `${(num / 1000).toFixed(1)}K`;
        }
        return num.toLocaleString();
    };

    return (
        <div className="space-y-4">
            {/* Organization Name Display */}
            {organizationName && (
                <Card className="border-0 shadow-md bg-gradient-to-r from-blue-50 to-indigo-50">
                    <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-blue-100 rounded-lg">
                                <Building2 className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-slate-800">
                                    {organizationName}
                                </h2>
                                <p className="text-sm text-slate-600">
                                    Organization Dashboard
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-600">
                                    Total Users
                                </p>
                                <p className="text-3xl font-bold text-slate-800 mt-2">
                                    {totalUsers}
                                </p>
                            </div>
                            <div className="p-3 bg-blue-100 rounded-xl">
                                <Users className="w-6 h-6 text-blue-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-600">
                                    Active Users
                                </p>
                                <p className="text-3xl font-bold text-green-700 mt-2">
                                    {activeUsers}
                                </p>
                            </div>
                            <div className="p-3 bg-green-100 rounded-xl">
                                <UserCheck className="w-6 h-6 text-green-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-600">
                                    Total Tokens
                                </p>
                                <p className="text-3xl font-bold text-purple-700 mt-2">
                                    {formatNumber(totalTokens)}
                                </p>
                            </div>
                            <div className="p-3 bg-purple-100 rounded-xl">
                                <Coins className="w-6 h-6 text-purple-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-600">
                                    Tokens Used
                                </p>
                                <p className="text-3xl font-bold text-orange-700 mt-2">
                                    {formatNumber(tokensUsed)}
                                </p>
                            </div>
                            <div className="p-3 bg-orange-100 rounded-xl">
                                <Coins className="w-6 h-6 text-orange-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default UserStatsCards;
