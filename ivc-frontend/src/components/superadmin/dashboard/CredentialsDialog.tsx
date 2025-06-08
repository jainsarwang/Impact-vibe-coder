import React, { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Copy, Check, Eye, EyeOff, AlertTriangle, Shield } from "lucide-react";
import { useToast } from "@/hooks/superadmin/use-toast";

interface CredentialsDialogProps {
    isOpen: boolean;
    onClose: () => void;
    username: string;
    password: string;
    organizationName: string;
}

const CredentialsDialog = ({
    isOpen,
    onClose,
    username,
    password,
    organizationName,
}: CredentialsDialogProps) => {
    const [copiedField, setCopiedField] = useState<string | null>(null);
    const [showPassword, setShowPassword] = useState(false);
    const { toast } = useToast();

    const copyToClipboard = async (text: string, field: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedField(field);
            toast({
                title: "Copied!",
                description: `${field} copied to clipboard`,
            });
            setTimeout(() => setCopiedField(null), 2000);
        } catch (error) {
            toast({
                title: "Copy Failed",
                description: "Failed to copy to clipboard",
                variant: "destructive",
            });
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader className="text-center pb-2">
                    <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
                        <Shield className="w-6 h-6 text-green-600" />
                    </div>
                    <DialogTitle className="text-xl font-semibold text-foreground">
                        Organization Created Successfully
                    </DialogTitle>
                    <p className="text-sm text-muted-foreground font-medium">
                        {organizationName}
                    </p>
                </DialogHeader>

                <div className="space-y-4">
                    {/* Security Warning */}
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                        <div className="flex items-center space-x-2">
                            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                            <p className="text-sm text-amber-800 font-medium">
                                Save these credentials now - they won't be shown
                                again
                            </p>
                        </div>
                    </div>

                    {/* Credentials */}
                    <div className="space-y-3">
                        {/* Username */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="username"
                                className="text-sm font-medium"
                            >
                                Username
                            </Label>
                            <div className="flex space-x-2">
                                <Input
                                    id="username"
                                    type="text"
                                    value={username}
                                    readOnly
                                    className="font-mono text-sm bg-muted"
                                />
                                <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() =>
                                        copyToClipboard(username, "Username")
                                    }
                                    className="px-3"
                                >
                                    {copiedField === "Username" ? (
                                        <Check className="h-4 w-4 text-green-600" />
                                    ) : (
                                        <Copy className="h-4 w-4" />
                                    )}
                                </Button>
                            </div>
                        </div>

                        {/* Password */}
                        <div className="space-y-2">
                            <Label
                                htmlFor="password"
                                className="text-sm font-medium"
                            >
                                Password
                            </Label>
                            <div className="flex space-x-2">
                                <div className="relative flex-1">
                                    <Input
                                        id="password"
                                        type={
                                            showPassword ? "text" : "password"
                                        }
                                        value={password}
                                        readOnly
                                        className="font-mono text-sm bg-muted pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() =>
                                            setShowPassword(!showPassword)
                                        }
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                                    >
                                        {showPassword ? (
                                            <EyeOff className="h-4 w-4" />
                                        ) : (
                                            <Eye className="h-4 w-4" />
                                        )}
                                    </button>
                                </div>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() =>
                                        copyToClipboard(password, "Password")
                                    }
                                    className="px-3"
                                >
                                    {copiedField === "Password" ? (
                                        <Check className="h-4 w-4 text-green-600" />
                                    ) : (
                                        <Copy className="h-4 w-4" />
                                    )}
                                </Button>
                            </div>
                        </div>
                    </div>

                    {/* Action Button */}
                    <div className="pt-2">
                        <Button onClick={onClose} className="w-full">
                            I've Saved the Credentials
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default CredentialsDialog;
