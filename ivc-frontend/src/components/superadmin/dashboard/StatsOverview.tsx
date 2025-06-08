import React from "react";
import { Card, CardContent } from "@/components/superadmin/ui/card";
import { Users, Building2, UserCheck, Activity } from "lucide-react";

interface StatsOverviewProps {
    totalStats: {
        organizations: number;
        admins: number;
        users: number;
        activeOrgs: number;
    };
}

const StatsOverview = ({ totalStats }: StatsOverviewProps) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs font-medium text-blue-600 mb-1">
                                Organizations
                            </p>
                            <p className="text-xl font-bold text-blue-900">
                                {totalStats.organizations}
                            </p>
                        </div>
                        <Building2 className="w-6 h-6 text-blue-600" />
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs font-medium text-green-600 mb-1">
                                Active Orgs
                            </p>
                            <p className="text-xl font-bold text-green-900">
                                {totalStats.activeOrgs}
                            </p>
                        </div>
                        <Activity className="w-6 h-6 text-green-600" />
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs font-medium text-purple-600 mb-1">
                                Admins
                            </p>
                            <p className="text-xl font-bold text-purple-900">
                                {totalStats.admins}
                            </p>
                        </div>
                        <UserCheck className="w-6 h-6 text-purple-600" />
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs font-medium text-orange-600 mb-1">
                                Total Users
                            </p>
                            <p className="text-xl font-bold text-orange-900">
                                {totalStats.users}
                            </p>
                        </div>
                        <Users className="w-6 h-6 text-orange-600" />
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default StatsOverview;
