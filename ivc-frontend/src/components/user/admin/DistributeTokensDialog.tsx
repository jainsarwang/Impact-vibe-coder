import React, { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { GitBranch } from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

interface User {
    id: string;
    username: string;
    email: string;
    isActive: boolean;
    tokensLeft: number;
    tokensUsed: number;
    totalTokens: number;
}

interface DistributeTokensDialogProps {
    users: User[];
    onDistributeTokensEqually: () => void;
}

const DistributeTokensDialog = ({
    users,
    onDistributeTokensEqually,
}: DistributeTokensDialogProps) => {
    const { toast } = useToast();
    const [open, setOpen] = useState(false);

    const activeUsers = users.filter((user) => user.isActive);
    const totalActiveUsers = activeUsers.length;
    const totalTokensToDistribute = activeUsers.reduce(
        (sum, user) => sum + user.totalTokens,
        0
    );
    const tokensPerUser = Math.floor(
        totalTokensToDistribute / totalActiveUsers
    );

    const handleDistributeTokens = () => {
        toast({
            title: "Tokens Distributed",
            description: `${tokensPerUser.toLocaleString()} tokens have been equally distributed to ${totalActiveUsers} active users.`,
            duration: 3000,
        });

        onDistributeTokensEqually();
        setOpen(false);
    };

    const handleCancel = () => {
        setOpen(false);
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    variant="outline"
                    className="border-purple-200 text-purple-700 hover:bg-purple-50"
                >
                    <GitBranch className="w-4 h-4 mr-2" />
                    Distribute Tokens
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Distribute Tokens Equally</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                    <p className="text-sm text-gray-600">
                        This will distribute tokens equally among all{" "}
                        {totalActiveUsers} active users.
                    </p>
                    <div className="flex justify-end space-x-3">
                        <Button variant="outline" onClick={handleCancel}>
                            Cancel
                        </Button>
                        <Button
                            onClick={handleDistributeTokens}
                            className="bg-purple-600 hover:bg-purple-700"
                        >
                            Distribute
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default DistributeTokensDialog;
