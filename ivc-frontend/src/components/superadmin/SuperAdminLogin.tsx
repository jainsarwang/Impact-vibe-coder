import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Lock, User, Shield, Eye, EyeOff } from "lucide-react";
import { adminApiService } from "@/services/superadmin/adminApi";

interface SuperAdminLoginProps {
    onLogin: () => void;
}

const SuperAdminLogin = ({ onLogin }: SuperAdminLoginProps) => {
    const [credentials, setCredentials] = useState({
        username: "",
        password: "",
    });
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            console.log("Attempting login with credentials:", {
                username: credentials.username,
            });

            // Try actual API login first
            await adminApiService.login(credentials);

            // Verify if user is a superadmin
            await adminApiService.verifySuperAdmin();

            console.log("Successfully authenticated as superadmin");
            onLogin();
        } catch (err) {
            console.error("Login error:", err);

            // Check for testing credentials as fallback
            // if (credentials.username === 'superadmin' && credentials.password === 'SuperStrongP@ssw0rd!') {
            //   console.log('Using default testing credentials - bypassing API');
            //   // Set a mock token for testing
            //   document.cookie = 'accessToken=test-token; path=/; max-age=86400; SameSite=Lax';
            //   // Add a flag to indicate this is a test session
            //   localStorage.setItem('isTestSession', 'true');
            //   console.log('Test session established, calling onLogin');
            //   onLogin();
            //   return;
            // }

            setError(
                err instanceof Error
                    ? err.message
                    : "Authentication failed. Please check your credentials and ensure the backend is running."
            );
            adminApiService.logout();
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-700"></div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
            </div>

            <div className="w-full max-w-md relative z-10">
                {/* Header Section */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 rounded-3xl mb-6 shadow-2xl relative">
                        <Shield className="w-10 h-10 text-white" />
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-600 rounded-3xl blur opacity-30 animate-pulse"></div>
                    </div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent mb-2">
                        Impact Vibe Coder
                    </h1>
                    <p className="text-xl text-gray-600 font-medium">
                        Super Admin Portal
                    </p>
                    <div className="w-24 h-1 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mx-auto mt-4"></div>
                </div>

                {/* Login Card */}
                <Card className="shadow-2xl border-0 bg-white/95 backdrop-blur-sm relative overflow-hidden">
                    {/* Card Glow Effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-lg"></div>

                    <CardHeader className="space-y-1 pb-8 pt-8 relative z-10">
                        <CardTitle className="text-3xl font-bold text-center text-gray-900 mb-2">
                            Welcome Back
                        </CardTitle>
                        <p className="text-center text-gray-600 text-lg">
                            Sign in to access the Super Admin Dashboard
                        </p>
                    </CardHeader>

                    <CardContent className="px-8 pb-8 relative z-10">
                        <form onSubmit={handleLogin} className="space-y-6">
                            {/* Username Field */}
                            <div className="space-y-2">
                                <Label
                                    htmlFor="username"
                                    className="text-sm font-semibold text-gray-700 flex items-center"
                                >
                                    <User className="w-4 h-4 mr-2 text-blue-600" />
                                    Username
                                </Label>
                                <div className="relative group">
                                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg blur opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                                    <Input
                                        id="username"
                                        type="text"
                                        placeholder="Enter your username"
                                        value={credentials.username}
                                        onChange={(e) =>
                                            setCredentials({
                                                ...credentials,
                                                username: e.target.value,
                                            })
                                        }
                                        className="relative z-10 h-12 text-base border-gray-200 focus:border-blue-500 focus:ring-blue-500 bg-white/90 backdrop-blur-sm transition-all duration-200"
                                        required
                                    />
                                </div>
                            </div>

                            {/* Password Field */}
                            <div className="space-y-2">
                                <Label
                                    htmlFor="password"
                                    className="text-sm font-semibold text-gray-700 flex items-center"
                                >
                                    <Lock className="w-4 h-4 mr-2 text-blue-600" />
                                    Password
                                </Label>
                                <div className="relative group">
                                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg blur opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                                    <Input
                                        id="password"
                                        type={
                                            showPassword ? "text" : "password"
                                        }
                                        placeholder="Enter your password"
                                        value={credentials.password}
                                        onChange={(e) =>
                                            setCredentials({
                                                ...credentials,
                                                password: e.target.value,
                                            })
                                        }
                                        className="relative z-10 h-12 text-base border-gray-200 focus:border-blue-500 focus:ring-blue-500 bg-white/90 backdrop-blur-sm pr-12 transition-all duration-200"
                                        required
                                    />
                                    <button
                                        type="button"
                                        onClick={() =>
                                            setShowPassword(!showPassword)
                                        }
                                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors z-20"
                                    >
                                        {showPassword ? (
                                            <EyeOff className="h-5 w-5" />
                                        ) : (
                                            <Eye className="h-5 w-5" />
                                        )}
                                    </button>
                                </div>
                            </div>

                            {/* Error Alert */}
                            {error && (
                                <Alert className="border-red-200 bg-red-50 animate-fade-in">
                                    <AlertDescription className="text-red-600 font-medium">
                                        {error}
                                    </AlertDescription>
                                </Alert>
                            )}

                            {/* Submit Button */}
                            <Button
                                type="submit"
                                className="w-full h-12 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 hover:from-blue-700 hover:via-blue-800 hover:to-indigo-800 text-white font-semibold text-base shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 relative overflow-hidden group"
                                disabled={isLoading}
                            >
                                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                                <span className="relative z-10">
                                    {isLoading ? (
                                        <div className="flex items-center justify-center">
                                            <div className="relative mr-3">
                                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                                <div
                                                    className="absolute inset-0 w-5 h-5 border-2 border-transparent border-t-blue-200 rounded-full animate-spin"
                                                    style={{
                                                        animationDirection:
                                                            "reverse",
                                                        animationDuration:
                                                            "1.5s",
                                                    }}
                                                ></div>
                                            </div>
                                            Signing in...
                                        </div>
                                    ) : (
                                        "Sign In"
                                    )}
                                </span>
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default SuperAdminLogin;
