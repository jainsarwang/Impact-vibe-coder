import React from "react";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

interface UserHeaderProps {
    username: string;
    onLogout: () => void;
}

const UserHeader = ({ username, onLogout }: UserHeaderProps) => {
    return (
        <header className="bg-white shadow-sm border-b border-slate-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex h-full items-center">
                        <img
                            src="/logo.png"
                            alt="Impact Vibe Coder"
                            className="h-14 rounded-md w-auto mr-4"
                        />
                        <div>
                            <h1 className="text-xl font-bold bg-gradient-to-r from-amber-600 to-red-600 bg-clip-text text-transparent">
                                Impact Vibe Coder
                            </h1>
                            <p className="text-sm text-slate-500">
                                Developer Workspace
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="text-right">
                            <p className="text-sm font-semibold text-slate-900">
                                Welcome, {username}
                            </p>
                            <p className="text-xs text-slate-500">
                                Professional Developer
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

export default UserHeader;
