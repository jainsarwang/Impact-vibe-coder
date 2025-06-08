import React from "react";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface PrimaryAdminWarningDialogProps {
    isOpen: boolean;
    onConfirm: () => void;
    onCancel: () => void;
    username: string;
}

const PrimaryAdminWarningDialog = ({
    isOpen,
    onConfirm,
    onCancel,
    username,
}: PrimaryAdminWarningDialogProps) => {
    return (
        <AlertDialog open={isOpen}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>
                        Warning: Primary Admin Status Change
                    </AlertDialogTitle>
                    <AlertDialogDescription className="space-y-2">
                        <p>
                            You are about to change the status of{" "}
                            <strong>{username}</strong>, who is the primary
                            admin.
                        </p>
                        <p className="text-red-600 font-medium">
                            ⚠️ If you proceed:
                        </p>
                        <ul className="list-disc list-inside text-sm space-y-1 text-red-600">
                            <li>
                                You will not be able to change this status again
                            </li>
                            <li>
                                You will lose the ability to change other users'
                                status
                            </li>
                            <li>This action cannot be undone</li>
                        </ul>
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel onClick={onCancel}>
                        Cancel
                    </AlertDialogCancel>
                    <AlertDialogAction
                        onClick={onConfirm}
                        className="bg-red-600 hover:bg-red-700"
                    >
                        Continue Anyway
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};

export default PrimaryAdminWarningDialog;
