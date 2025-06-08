import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Shield,
    User,
    Calendar,
    Plus,
    Mail,
    UserCheck,
    Clock,
    Key,
    Activity,
    Building2,
} from "lucide-react";
import { User as ApiUser } from "@/services/superadmin/adminApi";

interface PrimaryAdminSectionProps {
    primaryAdmin: ApiUser | undefined;
    organizationActive: boolean;
    onAddTokens: () => void;
}

const PrimaryAdminSection = ({
    primaryAdmin,
    organizationActive,
    onAddTokens,
}: PrimaryAdminSectionProps) => {
    if (!primaryAdmin) return null;

    return (
        <Card className="mb-3 shadow-sm border border-gray-200">
            <CardHeader className="pb-2 pt-3 px-4">
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center text-sm font-semibold">
                        <div className="w-5 h-5 bg-gradient-to-br from-blue-500 to-blue-600 rounded-md flex items-center justify-center mr-2">
                            <Shield className="w-3 h-3 text-white" />
                        </div>
                        Primary Administrator
                    </CardTitle>
                    <Button
                        onClick={onAddTokens}
                        size="sm"
                        disabled={!organizationActive}
                        className={`${
                            organizationActive
                                ? "bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700"
                                : "bg-gray-400 cursor-not-allowed"
                        } text-white text-xs px-2 py-1 h-7`}
                    >
                        <Plus className="w-3 h-3 mr-1" />
                        Add Tokens
                    </Button>
                </div>
            </CardHeader>
            <CardContent className="pt-0 px-4 pb-3">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-3 border border-blue-100">
                    <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center shadow-sm">
                                <User className="w-4 h-4 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="text-sm font-semibold text-gray-900 mb-1 truncate">
                                    {primaryAdmin.name}
                                </h3>
                                <div className="flex items-center text-xs text-gray-600 mb-2">
                                    <Mail className="w-3 h-3 mr-1 flex-shrink-0" />
                                    <span className="truncate">
                                        {primaryAdmin.email}
                                    </span>
                                </div>

                                {/* Status and Info Row */}
                                <div className="flex flex-wrap items-center gap-2 mb-2">
                                    <Badge
                                        variant={
                                            primaryAdmin.is_active
                                                ? "default"
                                                : "secondary"
                                        }
                                        className={`${
                                            primaryAdmin.is_active
                                                ? "bg-emerald-500 hover:bg-emerald-600"
                                                : ""
                                        } text-xs px-2 py-0.5`}
                                    >
                                        <UserCheck className="w-2 h-2 mr-1" />
                                        {primaryAdmin.is_active
                                            ? "Active"
                                            : "Inactive"}
                                    </Badge>

                                    <span className="text-xs text-gray-500 flex items-center">
                                        <Calendar className="w-2 h-2 mr-1" />
                                        {new Date(
                                            primaryAdmin.created_at || ""
                                        ).toLocaleDateString()}
                                    </span>
                                </div>

                                {/* Additional Info */}
                                <div className="grid grid-cols-2 gap-2 text-xs">
                                    <div className="flex items-center text-gray-600">
                                        <Key className="w-2 h-2 mr-1" />
                                        <span className="text-xs">
                                            Admin Role
                                        </span>
                                    </div>
                                    <div className="flex items-center text-gray-600">
                                        <Building2 className="w-2 h-2 mr-1" />
                                        <span className="text-xs">
                                            Primary Admin
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Organization Status Warning */}
                    {!organizationActive && (
                        <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
                            <p className="text-xs text-yellow-700 flex items-center">
                                <Activity className="w-2 h-2 mr-1" />
                                Organization is inactive - Token addition
                                disabled
                            </p>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
};

export default PrimaryAdminSection;
