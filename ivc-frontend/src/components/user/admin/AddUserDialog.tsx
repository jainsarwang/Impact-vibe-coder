import React, { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UserPlus } from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

interface AddUserDialogProps {
    onAddUser: (user: {
        username: string;
        email: string;
        tokens: number;
    }) => void;
    defaultTokenAllocation: number;
}

const AddUserDialog = ({
    onAddUser,
    defaultTokenAllocation,
}: AddUserDialogProps) => {
    const { toast } = useToast();
    const [open, setOpen] = useState(false);
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        tokens: defaultTokenAllocation,
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.username || !formData.email || formData.tokens <= 0) {
            toast({
                title: "Validation Error",
                description: "Please fill in all fields with valid data.",
                variant: "destructive",
                duration: 3000,
            });
            return;
        }

        onAddUser(formData);

        toast({
            title: "User Created",
            description: `${formData.username} has been successfully added with ${formData.tokens} tokens.`,
            duration: 3000,
        });

        // Reset form and close dialog
        setFormData({
            username: "",
            email: "",
            tokens: defaultTokenAllocation,
        });
        setOpen(false);
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                    <UserPlus className="w-4 h-4 mr-2" />
                    Add User
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle>Add New User</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 pt-4">
                    <div className="space-y-2">
                        <Label htmlFor="username">Username</Label>
                        <Input
                            id="username"
                            value={formData.username}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    username: e.target.value,
                                })
                            }
                            placeholder="Enter username"
                            required
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="email">Email</Label>
                        <Input
                            id="email"
                            type="email"
                            value={formData.email}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    email: e.target.value,
                                })
                            }
                            placeholder="Enter email address"
                            required
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="tokens">Initial Tokens</Label>
                        <Input
                            id="tokens"
                            type="number"
                            value={formData.tokens}
                            onChange={(e) =>
                                setFormData({
                                    ...formData,
                                    tokens: Number(e.target.value),
                                })
                            }
                            placeholder="Enter token allocation"
                            min="1"
                            required
                        />
                    </div>

                    <div className="flex justify-end space-x-3 pt-4">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => setOpen(false)}
                        >
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            className="bg-blue-600 hover:bg-blue-700"
                        >
                            Create User
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
};

export default AddUserDialog;
