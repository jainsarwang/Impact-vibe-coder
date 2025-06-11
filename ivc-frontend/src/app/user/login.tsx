"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/user/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Shield, User, Crown, Eye, EyeOff } from "lucide-react";
import { useToast } from "@/hooks/user/use-toast";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState<"admin" | "user">("admin");
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const urls = {
        admin: "/user/admin-dashboard",
        user: "/user/user-dashboard",
    };

    const { login, isAuthenticated, user } = useAuth();
    const router = useRouter();
    const { toast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!username || !password || !role) {
            toast({
                title: "Missing Information",
                description: "Please fill in all fields.",
                variant: "destructive",
            });
            return;
        }

        setIsLoading(true);

        try {
            const result = await login(username, password, role);

            if (result.success && result.role) {
                toast({
                    title: "Login Successful",
                    description: `Welcome back, ${username}!`,
                });

                if (result.role === "admin") {
                    router.push(urls.admin);
                } else {
                    router.push(urls.user);
                }
            } else {
                toast({
                    title: "Login Failed",
                    description: "Invalid credentials. Please try again.",
                    variant: "destructive",
                });
            }
        } catch (error) {
            console.error("Login error:", error);
            toast({
                title: "Login Error",
                description:
                    "An error occurred during login. Please try again.",
                variant: "destructive",
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (isAuthenticated) {
            if (user?.role === "admin") {
                router.push(urls.admin);
            } else {
                router.push(urls.user);
            }
        }
    }, [isAuthenticated]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Animated Background Elements */}
            <div className="absolute inset-0">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-3xl animate-pulse delay-500"></div>
            </div>

            <div className="w-full max-w-lg relative z-10">
                {/* Company Logo and Branding */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center mb-6">
                        <img
                            src="/logo.png"
                            alt="Impact Vibe Coder"
                            className="h-16 w-auto filter drop-shadow-2xl rounded"
                        />
                    </div>
                    <div className="space-y-3">
                        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
                            Impact Vibe Coder
                        </h1>
                        <p className="text-slate-300 font-medium">
                            Advanced Development Platform
                        </p>
                        <div className="w-24 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 mx-auto rounded-full"></div>
                    </div>
                </div>

                <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur-xl relative overflow-hidden">
                    {/* Card Accent */}
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500"></div>

                    <CardHeader className="space-y-2 pb-6 pt-8">
                        <CardTitle className="text-2xl font-bold text-center text-slate-800">
                            Access Portal
                        </CardTitle>
                        <p className="text-center text-slate-600">
                            Enter your credentials to continue
                        </p>
                    </CardHeader>

                    <CardContent className="pb-8 px-6">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-4">
                                <div className="space-y-3">
                                    <Label
                                        htmlFor="role"
                                        className="text-sm font-semibold text-slate-700 flex items-center"
                                    >
                                        <Crown className="w-4 h-4 mr-2 text-purple-600" />
                                        Login As
                                    </Label>
                                    <Select
                                        value={role}
                                        onValueChange={(
                                            value: "admin" | "user"
                                        ) => setRole(value)}
                                    >
                                        <SelectTrigger className="h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500 bg-white">
                                            <SelectValue placeholder="Select your role" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="admin">
                                                Administrator
                                            </SelectItem>
                                            <SelectItem value="user">
                                                User
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-3">
                                    <Label
                                        htmlFor="username"
                                        className="text-sm font-semibold text-slate-700 flex items-center"
                                    >
                                        <User className="w-4 h-4 mr-2 text-blue-600" />
                                        Username
                                    </Label>
                                    <Input
                                        id="username"
                                        type="text"
                                        value={username}
                                        onChange={(e) =>
                                            setUsername(e.target.value)
                                        }
                                        placeholder="Enter your username"
                                        className="h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500 bg-white"
                                        required
                                    />
                                </div>

                                <div className="space-y-3">
                                    <Label
                                        htmlFor="password"
                                        className="text-sm font-semibold text-slate-700 flex items-center"
                                    >
                                        <Shield className="w-4 h-4 mr-2 text-blue-600" />
                                        Password
                                    </Label>
                                    <div className="relative">
                                        <Input
                                            id="password"
                                            type={
                                                showPassword
                                                    ? "text"
                                                    : "password"
                                            }
                                            value={password}
                                            onChange={(e) =>
                                                setPassword(e.target.value)
                                            }
                                            placeholder="Enter your password"
                                            className="h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500 bg-white pr-12"
                                            required
                                        />
                                        <button
                                            type="button"
                                            onClick={() =>
                                                setShowPassword(!showPassword)
                                            }
                                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-slate-700"
                                        >
                                            {showPassword ? (
                                                <EyeOff className="w-5 h-5" />
                                            ) : (
                                                <Eye className="w-5 h-5" />
                                            )}
                                        </button>
                                    </div>
                                </div>

                                <Button
                                    type="submit"
                                    className="w-full h-12 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white font-semibold transition-all duration-300 transform hover:scale-[1.02] shadow-xl"
                                    disabled={isLoading}
                                >
                                    {isLoading ? (
                                        <div className="flex items-center">
                                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3" />
                                            Authenticating...
                                        </div>
                                    ) : (
                                        <div className="flex items-center">
                                            <Shield className="w-5 h-5 mr-3" />
                                            Access Platform
                                        </div>
                                    )}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Login;
