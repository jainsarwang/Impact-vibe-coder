import React from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Copy } from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

interface UserCredentialsDialogProps {
    isOpen: boolean;
    onClose: () => void;
    credentials: {
        username: string;
        password: string;
    } | null;
}

const UserCredentialsDialog = ({
    isOpen,
    onClose,
    credentials,
}: UserCredentialsDialogProps) => {
    const { toast } = useToast();

    const copyToClipboard = (text: string, label: string) => {
        navigator.clipboard.writeText(text);
        toast({
            title: `${label} Copied!`,
            description: `The ${label.toLowerCase()} has been copied to your clipboard.`,
            duration: 2000,
        });
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>User Created Successfully</DialogTitle>
                </DialogHeader>

                <div className="space-y-4 pt-2">
                    <div>
                        <p className="text-sm font-medium mb-2">
                            Here are the user credentials:
                        </p>
                    </div>

                    {credentials && (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between rounded-md border p-3">
                                <div>
                                    <p className="text-xs text-muted-foreground mb-1">
                                        Username
                                    </p>
                                    <p className="font-medium">
                                        {credentials.username}
                                    </p>
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        copyToClipboard(
                                            credentials.username,
                                            "Username"
                                        )
                                    }
                                >
                                    <Copy className="h-3.5 w-3.5" />
                                </Button>
                            </div>

                            <div className="flex items-center justify-between rounded-md border p-3">
                                <div>
                                    <p className="text-xs text-muted-foreground mb-1">
                                        Password
                                    </p>
                                    <p className="font-medium">
                                        {credentials.password}
                                    </p>
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        copyToClipboard(
                                            credentials.password,
                                            "Password"
                                        )
                                    }
                                >
                                    <Copy className="h-3.5 w-3.5" />
                                </Button>
                            </div>
                        </div>
                    )}

                    <div className="flex justify-end">
                        <Button onClick={onClose}>Done</Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default UserCredentialsDialog;
