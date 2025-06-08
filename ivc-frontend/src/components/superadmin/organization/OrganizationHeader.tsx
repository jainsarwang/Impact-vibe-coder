import React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Building2, Activity } from "lucide-react";
import { Organization } from "@/services/superadmin/adminApi";

interface OrganizationHeaderProps {
    organization: Organization;
    onBack: () => void;
}

const OrganizationHeader = ({
    organization,
    onBack,
}: OrganizationHeaderProps) => {
    const isActive =
        organization.is_active !== undefined ? organization.is_active : true;

    return (
        <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-6 py-4">
                <div className="flex items-center space-x-4">
                    <Button
                        variant="outline"
                        onClick={onBack}
                        className="hover:bg-gray-50 text-sm h-8 px-3"
                    >
                        <ArrowLeft className="w-3 h-3 mr-2" />
                        Back to Dashboard
                    </Button>
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                            <Building2 className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <div className="flex items-center space-x-2">
                                <h1 className="text-xl font-bold text-gray-900">
                                    {organization.organization_name}
                                </h1>
                                <Badge
                                    variant={isActive ? "default" : "secondary"}
                                    className={`${
                                        isActive
                                            ? "bg-emerald-500"
                                            : "bg-gray-400"
                                    } text-xs`}
                                >
                                    <Activity className="w-3 h-3 mr-1" />
                                    {isActive ? "Active" : "Inactive"}
                                </Badge>
                            </div>
                            <p className="text-sm text-gray-600">
                                Organization Management
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default OrganizationHeader;
