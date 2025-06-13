import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Users } from "lucide-react";
import UserStatsCards from "./UserStatsCards";
import AddUserDialog from "./AddUserDialog";
import DistributeTokensDialog from "./DistributeTokensDialog";
import UserTableRow from "./UserTableRow";
import type { User } from "@/types/user/admin";

interface UserManagementProps {
    users: User[];
    onToggleUserStatus: (userId: string) => void;
    onUpdateUserTokens: (userId: string, newTokens: number) => void;
    onDistributeTokensEqually: () => void;
    onAddUser: (user: {
        username: string;
        email: string;
        tokens: number;
    }) => void;
    defaultTokenAllocation: number;
    organizationName?: string;
}

const UserManagement = ({
    users,
    onToggleUserStatus,
    onUpdateUserTokens,
    onDistributeTokensEqually,
    onAddUser,
    defaultTokenAllocation,
    organizationName,
}: UserManagementProps) => {
    return (
        <div className="space-y-6">
            {/* Header Stats */}
            <UserStatsCards users={users} organizationName={organizationName} />

            {/* Header Section */}
            <Card className="border-0 shadow-lg">
                <CardHeader className="pb-4 bg-gradient-to-r from-slate-50 to-gray-50">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                            <div className="p-3 bg-blue-600 rounded-xl">
                                <Users className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <CardTitle className="text-xl text-slate-800">
                                    User Management
                                </CardTitle>
                                <p className="text-sm text-slate-600">
                                    Manage users, tokens, and permissions
                                </p>
                            </div>
                        </div>

                        <div className="flex space-x-3">
                            <DistributeTokensDialog
                                users={users}
                                onDistributeTokensEqually={
                                    onDistributeTokensEqually
                                }
                            />

                            <AddUserDialog
                                onAddUser={onAddUser}
                                defaultTokenAllocation={defaultTokenAllocation}
                            />
                        </div>
                    </div>
                </CardHeader>
            </Card>

            {/* Users Table */}
            <Card className="border-0 shadow-lg">
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-gradient-to-r from-slate-50 to-gray-50 border-b border-slate-200">
                                    <TableHead className="font-semibold text-slate-700 py-4 px-6">
                                        User Details
                                    </TableHead>
                                    <TableHead className="font-semibold text-slate-700 py-4">
                                        Token Management
                                    </TableHead>
                                    <TableHead className="font-semibold text-slate-700 py-4">
                                        Usage Analytics
                                    </TableHead>
                                    <TableHead className="font-semibold text-slate-700 py-4 text-center">
                                        Status
                                    </TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {users.map((user, index) => (
                                    <UserTableRow
                                        key={user.id}
                                        user={user}
                                        index={index}
                                        onToggleUserStatus={onToggleUserStatus}
                                        onUpdateUserTokens={onUpdateUserTokens}
                                    />
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default UserManagement;
