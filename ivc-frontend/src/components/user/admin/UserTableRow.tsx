import React, { useState } from "react";
import { TableCell, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { User, Coins, Activity, Edit2, Check, X } from "lucide-react";
import PrimaryAdminWarningDialog from "./PrimaryAdminWarningDialog";

interface User {
    id: string;
    username: string;
    email: string;
    isActive: boolean;
    tokensLeft: number;
    tokensUsed: number;
    totalTokens: number;
    lastLogin?: string;
    isPrimaryAdmin?: boolean;
}

interface UserTableRowProps {
    user: User;
    index: number;
    onToggleUserStatus: (userId: string) => void;
    onUpdateUserTokens: (userId: string, newTokens: number) => void;
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

const UserTableRow = ({
    user,
    index,
    onToggleUserStatus,
    onUpdateUserTokens,
}: UserTableRowProps) => {
    const [isEditing, setIsEditing] = useState(false);
    const [newTokens, setNewTokens] = useState(user.tokensLeft);
    const [showPrimaryAdminWarning, setShowPrimaryAdminWarning] =
        useState(false);

    const handleUpdateTokens = () => {
        onUpdateUserTokens(user.id, newTokens);
        setIsEditing(false);
    };

    const handleTokenInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        // Remove leading zeros and ensure it's a valid number
        const cleanValue = value.replace(/^0+/, "") || "0";
        setNewTokens(Number(cleanValue));
    };

    const handleStatusToggle = () => {
        if (user.isPrimaryAdmin) {
            setShowPrimaryAdminWarning(true);
        } else {
            onToggleUserStatus(user.id);
        }
    };

    const handlePrimaryAdminConfirm = () => {
        setShowPrimaryAdminWarning(false);
        onToggleUserStatus(user.id);
    };

    const handlePrimaryAdminCancel = () => {
        setShowPrimaryAdminWarning(false);
    };

    const usagePercentage =
        user.totalTokens > 0 ? (user.tokensUsed / user.totalTokens) * 100 : 0;

    return (
        <>
            <TableRow
                className={`${
                    index % 2 === 0 ? "bg-white" : "bg-slate-50/50"
                } hover:bg-blue-50/50 transition-colors`}
            >
                <TableCell className="py-4 px-6">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-slate-100 rounded-full">
                            <User className="w-4 h-4 text-slate-600" />
                        </div>
                        <div>
                            <div className="flex items-center space-x-2">
                                <span className="font-semibold text-slate-800">
                                    {user.username}
                                </span>
                                {user.isPrimaryAdmin && (
                                    <Badge
                                        variant="outline"
                                        className="text-xs bg-blue-50 text-blue-700 border-blue-200"
                                    >
                                        Primary Admin
                                    </Badge>
                                )}
                            </div>
                            <div className="text-sm text-slate-500">
                                {user.email}
                            </div>
                            <div className="text-xs text-slate-400 mt-1">
                                Last login: {user.lastLogin || "Never"}
                            </div>
                        </div>
                    </div>
                </TableCell>

                <TableCell className="py-4">
                    <div className="space-y-3">
                        <div className="flex items-center space-x-3">
                            {isEditing ? (
                                <div className="flex items-center space-x-2">
                                    <Input
                                        type="number"
                                        value={newTokens || ""}
                                        onChange={handleTokenInputChange}
                                        className="w-24 h-8 text-sm"
                                        min="0"
                                    />
                                    <Button
                                        size="sm"
                                        onClick={handleUpdateTokens}
                                        className="h-8 w-8 p-0"
                                    >
                                        <Check className="w-3 h-3" />
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => setIsEditing(false)}
                                        className="h-8 w-8 p-0"
                                    >
                                        <X className="w-3 h-3" />
                                    </Button>
                                </div>
                            ) : (
                                <div className="flex items-center space-x-2">
                                    <div className="flex items-center space-x-1">
                                        <Coins className="w-4 h-4 text-green-600" />
                                        <span className="text-sm font-medium text-slate-700">
                                            {formatNumber(user.tokensLeft)}
                                        </span>
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        onClick={() => setIsEditing(true)}
                                        className="h-6 w-6 p-0 hover:bg-slate-100"
                                    >
                                        <Edit2 className="w-3 h-3" />
                                    </Button>
                                </div>
                            )}
                        </div>
                        <div className="text-xs text-slate-500">
                            Total: {formatNumber(user.totalTokens)} tokens
                        </div>
                    </div>
                </TableCell>

                <TableCell className="py-4">
                    <div className="space-y-3">
                        <div className="flex items-center space-x-2">
                            <Activity className="w-4 h-4 text-orange-600" />
                            <span className="text-sm font-medium text-slate-700">
                                {formatNumber(user.tokensUsed)}
                            </span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-2">
                            <div
                                className="bg-gradient-to-r from-orange-400 to-red-500 h-2 rounded-full transition-all duration-300"
                                style={{
                                    width: `${Math.min(usagePercentage, 100)}%`,
                                }}
                            ></div>
                        </div>
                        <div className="text-xs text-slate-500">
                            {usagePercentage.toFixed(1)}% used
                        </div>
                    </div>
                </TableCell>

                <TableCell className="py-4 text-center">
                    <Badge
                        variant={user.isActive ? "default" : "secondary"}
                        className={`cursor-pointer transition-all duration-200 ${
                            user.isActive
                                ? "bg-green-100 text-green-800 hover:bg-green-200 hover:text-green-900 border-green-200"
                                : "bg-red-100 text-red-800 hover:bg-red-200 hover:text-red-900 border-red-200"
                        }`}
                        onClick={handleStatusToggle}
                    >
                        {user.isActive ? "Active" : "Inactive"}
                    </Badge>
                </TableCell>
            </TableRow>

            <PrimaryAdminWarningDialog
                isOpen={showPrimaryAdminWarning}
                onConfirm={handlePrimaryAdminConfirm}
                onCancel={handlePrimaryAdminCancel}
                username={user.username}
            />
        </>
    );
};

export default UserTableRow;
