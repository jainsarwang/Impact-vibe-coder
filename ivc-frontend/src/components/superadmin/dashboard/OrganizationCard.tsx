import React, { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
    Coins,
    Eye,
    Users,
    Calendar,
    Building2,
    Activity,
    Clock,
} from "lucide-react";
import { Organization } from "@/services/superadmin/adminApi";
import { updateOrganizationStatus } from "@/services/superadmin/organizations";
import { useToast } from "@/hooks/superadmin/use-toast";

interface OrganizationCardProps {
    org: Organization;
    onViewOrganization: (orgId: string) => void;
    onStatusUpdated: () => void;
}

const OrganizationCard = ({
    org,
    onViewOrganization,
    onStatusUpdated,
}: OrganizationCardProps) => {
    const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
    const { toast } = useToast();

    // Check if organization is active - default to true if not set
    const isActive = org.is_active !== undefined ? org.is_active : true;
    const adminCount =
        org.users?.filter(
            (user) => user.role_id && !user.role_id.includes("user")
        ).length || 0;

    const handleStatusToggle = async () => {
        setIsUpdatingStatus(true);
        try {
            const newStatus = !isActive;
            console.log(
                "Toggling status for organization:",
                org.organization_name,
                "from",
                isActive,
                "to",
                newStatus
            );

            await updateOrganizationStatus(org.organization_name, newStatus);

            toast({
                title: "Status Updated",
                description: `Organization ${
                    newStatus ? "activated" : "deactivated"
                } successfully`,
            });

            // Trigger parent refresh to get updated data
            onStatusUpdated();
        } catch (error) {
            console.error("Error updating organization status:", error);
            toast({
                title: "Error",
                description: "Failed to update organization status",
                variant: "destructive",
            });
        } finally {
            setIsUpdatingStatus(false);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    };

    const tokensUsed = org.total_tokens - (org.tokens_remaining || 0);
    const usagePercentage =
        org.total_tokens > 0 ? (tokensUsed / org.total_tokens) * 100 : 0;

    return (
        <Card className="group hover:shadow-lg transition-all duration-200 border border-gray-200 bg-white overflow-hidden hover:-translate-y-1">
            {/* Status Indicator */}
            <div
                className={`h-1 ${
                    isActive
                        ? "bg-gradient-to-r from-emerald-500 to-emerald-600"
                        : "bg-gradient-to-r from-gray-400 to-gray-500"
                }`}
            ></div>

            <CardHeader className="pb-1 pt-2 px-2">
                <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2 min-w-0 flex-1">
                        <div
                            className={`w-5 h-5 ${
                                isActive
                                    ? "bg-gradient-to-br from-blue-500 to-indigo-600"
                                    : "bg-gradient-to-br from-gray-400 to-gray-500"
                            } rounded-md flex items-center justify-center shadow-sm`}
                        >
                            <Building2 className="w-2 h-2 text-white" />
                        </div>
                        <div className="min-w-0 flex-1">
                            <h3 className="font-semibold text-xs text-gray-900 truncate leading-tight mb-0.5">
                                {org.organization_name}
                            </h3>
                            <p className="text-xs text-gray-500 flex items-center">
                                <Calendar className="w-2 h-2 mr-1" />
                                {formatDate(org.created_at)}
                            </p>
                        </div>
                    </div>

                    <div className="flex flex-col items-end space-y-1 ml-2">
                        <Badge
                            variant={isActive ? "default" : "secondary"}
                            className={`px-1.5 py-0.5 text-xs font-medium flex items-center space-x-1 ${
                                isActive
                                    ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                                    : "bg-gray-100 text-gray-600 border border-gray-200"
                            }`}
                        >
                            <Activity className="w-2 h-2" />
                            <span className="text-xs">
                                {isActive ? "Active" : "Inactive"}
                            </span>
                        </Badge>

                        <div className="flex items-center space-x-1 bg-gray-50 px-1.5 py-0.5 rounded-md">
                            <span className="text-xs text-gray-600 font-medium">
                                Status
                            </span>
                            <Switch
                                checked={isActive}
                                onCheckedChange={handleStatusToggle}
                                disabled={isUpdatingStatus}
                                className="data-[state=checked]:bg-emerald-500 scale-75"
                            />
                        </div>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="px-2 pb-2">
                {/* Compact Stats Grid */}
                <div className="grid grid-cols-2 gap-1.5 mb-2">
                    <div className="text-center p-1.5 bg-gradient-to-br from-blue-50 to-blue-100 rounded-md border border-blue-200">
                        <div className="flex items-center justify-center mb-0.5">
                            <Users className="w-2 h-2 text-blue-600" />
                        </div>
                        <p className="text-xs text-blue-700 font-medium mb-0.5">
                            Users
                        </p>
                        <p className="text-xs font-bold text-blue-900">
                            {org.user_count?.toLocaleString() || 0}
                        </p>
                    </div>

                    <div className="text-center p-1.5 bg-gradient-to-br from-yellow-50 to-amber-100 rounded-md border border-yellow-200">
                        <div className="flex items-center justify-center mb-0.5">
                            <Coins className="w-2 h-2 text-amber-600" />
                        </div>
                        <p className="text-xs text-amber-700 font-medium mb-0.5">
                            Tokens
                        </p>
                        <p className="text-xs font-bold text-amber-900">
                            {org.total_tokens?.toLocaleString() || 0}
                        </p>
                    </div>
                </div>

                {/* Compact Token Usage Progress */}
                <div className="mb-2">
                    <div className="flex justify-between items-center mb-0.5">
                        <span className="text-xs font-medium text-gray-700">
                            Token Usage
                        </span>
                        <span className="text-xs text-gray-500">
                            {usagePercentage.toFixed(1)}%
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1">
                        <div
                            className={`${
                                isActive
                                    ? "bg-gradient-to-r from-blue-500 to-indigo-600"
                                    : "bg-gray-400"
                            } h-1 rounded-full transition-all duration-300`}
                            style={{
                                width: `${Math.min(usagePercentage, 100)}%`,
                            }}
                        ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-0.5">
                        <span>{tokensUsed.toLocaleString()}</span>
                        <span>
                            {(org.tokens_remaining || 0).toLocaleString()}
                        </span>
                    </div>
                </div>

                {/* Additional Info */}
                <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                    <span className="flex items-center">
                        <Clock className="w-2 h-2 mr-1" />
                        Admins: {adminCount}
                    </span>
                    <span className="text-xs font-medium text-gray-600">
                        ID: {org.organization_id.slice(-6)}
                    </span>
                </div>

                {/* Compact Action Button */}
                <Button
                    onClick={() => onViewOrganization(org.organization_id)}
                    className={`w-full ${
                        isActive
                            ? "bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800"
                            : "bg-gray-500 hover:bg-gray-600"
                    } text-white font-medium py-1 rounded-md transition-all duration-200 shadow-sm hover:shadow-md transform hover:-translate-y-0.5 group text-xs h-6`}
                >
                    <Eye className="w-3 h-3 mr-1 group-hover:scale-110 transition-transform" />
                    View Details
                </Button>
            </CardContent>
        </Card>
    );
};

export default OrganizationCard;
