import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogDescription,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import {
    Settings,
    Save,
    Coins,
    Users,
    Shield,
    AlertTriangle,
    DollarSign,
    Clock,
    Database,
} from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

interface SystemSettingsProps {
    settings: {
        defaultTokenAllocation: number;
        autoDeactivateInactive: boolean;
        tokenDistributionMode: "equal" | "custom";
        maxTokensPerUser: number;
        sessionTimeout: number;
        allowUserRegistration: boolean;
        autoBackupEnabled: boolean;
        maintenanceMode: boolean;
    };
    onSettingsChange: (settings: any) => void;
}

const SystemSettings = ({
    settings,
    onSettingsChange,
}: SystemSettingsProps) => {
    const { toast } = useToast();
    const [pendingTokenAllocation, setPendingTokenAllocation] = useState(
        settings.defaultTokenAllocation.toString()
    );
    const [pendingMaxTokens, setPendingMaxTokens] = useState(
        (settings.maxTokensPerUser || 10000).toString()
    );

    const handleSaveSettings = () => {
        toast({
            title: "Settings Saved",
            description: "System settings have been updated successfully.",
        });
    };

    const updateSetting = (key: string, value: any) => {
        onSettingsChange({ ...settings, [key]: value });
    };

    const handleTokenAllocationChange = (value: string) => {
        const cleanValue = value.replace(/^0+/, "") || "0";
        if (/^\d*$/.test(cleanValue)) {
            setPendingTokenAllocation(cleanValue);
        }
    };

    const handleMaxTokensChange = (value: string) => {
        const cleanValue = value.replace(/^0+/, "") || "0";
        if (/^\d*$/.test(cleanValue)) {
            setPendingMaxTokens(cleanValue);
        }
    };

    const handleConfirmTokenAllocation = () => {
        const newValue = parseInt(pendingTokenAllocation) || 0;
        updateSetting("defaultTokenAllocation", newValue);
        toast({
            title: "Default Token Allocation Updated",
            description: `New users will now receive ${newValue.toLocaleString()} tokens by default.`,
        });
    };

    const handleConfirmMaxTokens = () => {
        const newValue = parseInt(pendingMaxTokens) || 0;
        updateSetting("maxTokensPerUser", newValue);
        toast({
            title: "Maximum Tokens Updated",
            description: `Users can now hold up to ${newValue.toLocaleString()} tokens.`,
        });
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <Card className="border-0 shadow-sm bg-gradient-to-r from-gray-50 to-slate-50">
                <CardHeader className="pb-4">
                    <div className="flex items-center space-x-4">
                        <div className="p-3 bg-gray-600 rounded-xl">
                            <Settings className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <CardTitle className="text-xl text-gray-900">
                                System Settings
                            </CardTitle>
                            <p className="text-sm text-gray-600">
                                Configure system-wide preferences and policies
                            </p>
                        </div>
                    </div>
                </CardHeader>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Token Management */}
                <Card className="border-0 shadow-sm">
                    <CardHeader className="pb-4">
                        <CardTitle className="flex items-center text-lg">
                            <div className="p-2 bg-amber-100 rounded-lg mr-3">
                                <Coins className="w-5 h-5 text-amber-600" />
                            </div>
                            Token Management
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div className="flex-1">
                                <h4 className="font-medium text-sm">
                                    Default Token Allocation
                                </h4>
                                <p className="text-xs text-gray-500">
                                    Tokens assigned to new users
                                </p>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Input
                                    className="w-24 h-8"
                                    type="text"
                                    value={pendingTokenAllocation}
                                    onChange={(e) =>
                                        handleTokenAllocationChange(
                                            e.target.value
                                        )
                                    }
                                />
                                <Dialog>
                                    <DialogTrigger asChild>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="h-8"
                                        >
                                            <DollarSign className="w-3 h-3" />
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-md">
                                        <DialogHeader>
                                            <DialogTitle className="flex items-center">
                                                <AlertTriangle className="w-5 h-5 mr-2 text-amber-600" />
                                                Confirm Token Allocation Change
                                            </DialogTitle>
                                            <DialogDescription>
                                                You are about to change the
                                                default token allocation from{" "}
                                                {settings.defaultTokenAllocation.toLocaleString()}{" "}
                                                to{" "}
                                                {parseInt(
                                                    pendingTokenAllocation
                                                ).toLocaleString()}{" "}
                                                tokens. This will affect all new
                                                users created after this change.
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="flex justify-end space-x-3 pt-4">
                                            <Button variant="outline" size="sm">
                                                Cancel
                                            </Button>
                                            <Button
                                                onClick={
                                                    handleConfirmTokenAllocation
                                                }
                                                size="sm"
                                                className="bg-amber-600 hover:bg-amber-700"
                                            >
                                                Confirm Change
                                            </Button>
                                        </div>
                                    </DialogContent>
                                </Dialog>
                            </div>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <div className="flex-1">
                                <h4 className="font-medium text-sm">
                                    Max Tokens Per User
                                </h4>
                                <p className="text-xs text-gray-500">
                                    Maximum tokens a user can hold
                                </p>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Input
                                    className="w-24 h-8"
                                    type="text"
                                    value={pendingMaxTokens}
                                    onChange={(e) =>
                                        handleMaxTokensChange(e.target.value)
                                    }
                                />
                                <Dialog>
                                    <DialogTrigger asChild>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="h-8"
                                        >
                                            <DollarSign className="w-3 h-3" />
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-md">
                                        <DialogHeader>
                                            <DialogTitle className="flex items-center">
                                                <AlertTriangle className="w-5 h-5 mr-2 text-amber-600" />
                                                Confirm Maximum Token Limit
                                            </DialogTitle>
                                            <DialogDescription>
                                                You are about to change the
                                                maximum token limit from{" "}
                                                {(
                                                    settings.maxTokensPerUser ||
                                                    10000
                                                ).toLocaleString()}{" "}
                                                to{" "}
                                                {parseInt(
                                                    pendingMaxTokens
                                                ).toLocaleString()}{" "}
                                                tokens. This will affect token
                                                allocation limits for all users.
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="flex justify-end space-x-3 pt-4">
                                            <Button variant="outline" size="sm">
                                                Cancel
                                            </Button>
                                            <Button
                                                onClick={handleConfirmMaxTokens}
                                                size="sm"
                                                className="bg-amber-600 hover:bg-amber-700"
                                            >
                                                Confirm Change
                                            </Button>
                                        </div>
                                    </DialogContent>
                                </Dialog>
                            </div>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="font-medium text-sm">
                                    Distribution Mode
                                </h4>
                                <p className="text-xs text-gray-500">
                                    How tokens are distributed
                                </p>
                            </div>
                            <Select
                                value={settings.tokenDistributionMode}
                                onValueChange={(value: "equal" | "custom") =>
                                    updateSetting(
                                        "tokenDistributionMode",
                                        value
                                    )
                                }
                            >
                                <SelectTrigger className="w-28 h-8">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="equal">Equal</SelectItem>
                                    <SelectItem value="custom">
                                        Custom
                                    </SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </CardContent>
                </Card>

                {/* User Management */}
                <Card className="border-0 shadow-sm">
                    <CardHeader className="pb-4">
                        <CardTitle className="flex items-center text-lg">
                            <div className="p-2 bg-blue-100 rounded-lg mr-3">
                                <Users className="w-5 h-5 text-blue-600" />
                            </div>
                            User Management
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="font-medium text-sm">
                                    Auto-deactivate Inactive
                                </h4>
                                <p className="text-xs text-gray-500">
                                    After 30 days of inactivity
                                </p>
                            </div>
                            <Switch
                                checked={settings.autoDeactivateInactive}
                                onCheckedChange={(checked) =>
                                    updateSetting(
                                        "autoDeactivateInactive",
                                        checked
                                    )
                                }
                            />
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="font-medium text-sm">
                                    Allow User Registration
                                </h4>
                                <p className="text-xs text-gray-500">
                                    Users can self-register
                                </p>
                            </div>
                            <Switch
                                checked={
                                    settings.allowUserRegistration || false
                                }
                                onCheckedChange={(checked) =>
                                    updateSetting(
                                        "allowUserRegistration",
                                        checked
                                    )
                                }
                            />
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="font-medium text-sm">
                                    Session Timeout
                                </h4>
                                <p className="text-xs text-gray-500">
                                    Minutes before auto-logout
                                </p>
                            </div>
                            <Input
                                className="w-20 h-8"
                                type="number"
                                value={settings.sessionTimeout || 30}
                                onChange={(e) =>
                                    updateSetting(
                                        "sessionTimeout",
                                        parseInt(e.target.value) || 30
                                    )
                                }
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* System Security */}
                <Card className="border-0 shadow-sm">
                    <CardHeader className="pb-4">
                        <CardTitle className="flex items-center text-lg">
                            <div className="p-2 bg-green-100 rounded-lg mr-3">
                                <Shield className="w-5 h-5 text-green-600" />
                            </div>
                            System Security
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="font-medium text-sm">
                                    Maintenance Mode
                                </h4>
                                <p className="text-xs text-gray-500">
                                    Restrict system access for maintenance
                                </p>
                            </div>
                            <Switch
                                checked={settings.maintenanceMode || false}
                                onCheckedChange={(checked) =>
                                    updateSetting("maintenanceMode", checked)
                                }
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* System Operations */}
                <Card className="border-0 shadow-sm">
                    <CardHeader className="pb-4">
                        <CardTitle className="flex items-center text-lg">
                            <div className="p-2 bg-purple-100 rounded-lg mr-3">
                                <Database className="w-5 h-5 text-purple-600" />
                            </div>
                            System Operations
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h4 className="font-medium text-sm">
                                    Auto Backup
                                </h4>
                                <p className="text-xs text-gray-500">
                                    Automatically backup system data daily
                                </p>
                            </div>
                            <Switch
                                checked={settings.autoBackupEnabled || false}
                                onCheckedChange={(checked) =>
                                    updateSetting("autoBackupEnabled", checked)
                                }
                            />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
                <Button
                    onClick={handleSaveSettings}
                    className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700"
                >
                    <Save className="w-4 h-4 mr-2" />
                    Save All Settings
                </Button>
            </div>
        </div>
    );
};

export default SystemSettings;
