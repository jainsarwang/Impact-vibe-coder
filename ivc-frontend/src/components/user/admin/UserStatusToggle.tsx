import React from "react";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";

interface UserStatusToggleProps {
    userId: string;
    isActive: boolean;
    username: string;
    onToggle: (userId: string) => void;
}

const UserStatusToggle = ({
    userId,
    isActive,
    username,
    onToggle,
}: UserStatusToggleProps) => {
    return (
        <div className="flex items-center space-x-2">
            <Badge variant={isActive ? "default" : "secondary"}>
                {isActive ? "Active" : "Inactive"}
            </Badge>
            <Switch
                checked={isActive}
                onCheckedChange={() => onToggle(userId)}
                aria-label={`Toggle status for ${username}`}
            />
        </div>
    );
};

export default UserStatusToggle;
