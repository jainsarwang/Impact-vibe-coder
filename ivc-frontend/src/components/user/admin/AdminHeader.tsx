import React from "react";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

interface AdminHeaderProps {
    username: string;
    onLogout: () => void;
    organizationName: string;
}

const AdminHeader = ({
    username,
    onLogout,
    organizationName,
}: AdminHeaderProps) => {
    return (
        <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center">
                        <img
                            src="/lovable-uploads/91162cee-1851-4344-a4c0-97d49c0debca.png"
                            alt="Impact Vibe Coder"
                            className="h-8 w-auto mr-4"
                        />
                        <div>
                            <h1 className="text-xl font-semibold bg-gradient-to-r from-amber-600 to-red-600 bg-clip-text text-transparent">
                                Impact Vibe Coder
                            </h1>
                            <p className="text-sm text-gray-500">
                                Admin Dashboard
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">
                                Welcome, {username}
                            </p>
                            <p className="text-xs text-gray-500">
                                Administrator
                            </p>
                        </div>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onLogout}
                            className="border-red-200 text-red-600 hover:bg-red-50"
                        >
                            <LogOut className="w-4 h-4 mr-2" />
                            Logout
                        </Button>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default AdminHeader;
