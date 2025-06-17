import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    ArrowLeft,
    User,
    Mail,
    Phone,
    Calendar,
    MapPin,
    Activity,
    Globe,
    Smartphone,
} from "lucide-react";

interface UserDetailsProps {
    userId: string;
    onBack: () => void;
}

const UserDetails = ({ userId, onBack }: UserDetailsProps) => {
    const [userDetails, setUserDetails] = useState({
        name: `User ${userId.split("-")[2]}`,
        email: `user${userId.split("-")[2]}@organization.com`,
        phone: "+1-555-1234",
        isActive: true,
        location: "New York, NY",
        joinedDate: "2024-01-15",
        lastLogin: "2024-05-27",
        activityScore: 85,
        totalSessions: 342,
        deviceType: "Desktop",
        browser: "Chrome",
        ipAddress: "192.168.1.100",
        timeZone: "EST",
        subscription: "Premium",
        tokensUsed: 1250,
        tokensRemaining: 750,
    });

    const [activityLog, setActivityLog] = useState([
        {
            date: "2024-05-27",
            action: "Logged in",
            details: "Desktop session started",
        },
        {
            date: "2024-05-26",
            action: "Updated profile",
            details: "Changed phone number",
        },
        {
            date: "2024-05-25",
            action: "Used tokens",
            details: "50 tokens used for API calls",
        },
        {
            date: "2024-05-24",
            action: "Logged in",
            details: "Mobile session started",
        },
        {
            date: "2024-05-23",
            action: "Feature access",
            details: "Accessed premium feature",
        },
    ]);

    return (
        <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center space-x-4">
                        <Button variant="outline" onClick={onBack}>
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back to Admin
                        </Button>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">
                                {userDetails.name}
                            </h1>
                            <p className="text-sm text-gray-600">
                                User Profile & Activity
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* User Profile */}
                    <div className="lg:col-span-2">
                        <Card className="mb-6">
                            <CardHeader>
                                <CardTitle>User Profile</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                                <User className="w-6 h-6 text-blue-600" />
                                            </div>
                                            <div>
                                                <h3 className="font-semibold text-lg">
                                                    {userDetails.name}
                                                </h3>
                                                <Badge
                                                    variant={
                                                        userDetails.isActive
                                                            ? "default"
                                                            : "secondary"
                                                    }
                                                    className={
                                                        userDetails.isActive
                                                            ? "bg-green-500"
                                                            : ""
                                                    }
                                                >
                                                    {userDetails.isActive
                                                        ? "Active"
                                                        : "Inactive"}
                                                </Badge>
                                            </div>
                                        </div>

                                        <div className="space-y-3">
                                            <div className="flex items-center space-x-2">
                                                <Mail className="w-4 h-4 text-gray-400" />
                                                <span className="text-sm">
                                                    {userDetails.email}
                                                </span>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Phone className="w-4 h-4 text-gray-400" />
                                                <span className="text-sm">
                                                    {userDetails.phone}
                                                </span>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <MapPin className="w-4 h-4 text-gray-400" />
                                                <span className="text-sm">
                                                    {userDetails.location}
                                                </span>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Calendar className="w-4 h-4 text-gray-400" />
                                                <span className="text-sm">
                                                    Joined:{" "}
                                                    {new Date(
                                                        userDetails.joinedDate
                                                    ).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="text-center p-3 bg-blue-50 rounded-lg">
                                                <p className="text-sm text-gray-600">
                                                    Activity Score
                                                </p>
                                                <p className="text-2xl font-bold text-blue-600">
                                                    {userDetails.activityScore}
                                                </p>
                                            </div>
                                            <div className="text-center p-3 bg-green-50 rounded-lg">
                                                <p className="text-sm text-gray-600">
                                                    Total Sessions
                                                </p>
                                                <p className="text-2xl font-bold text-green-600">
                                                    {userDetails.totalSessions}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="space-y-2">
                                            <div className="flex items-center space-x-2">
                                                <Smartphone className="w-4 h-4 text-gray-400" />
                                                <span className="text-sm">
                                                    Device:{" "}
                                                    {userDetails.deviceType}
                                                </span>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Globe className="w-4 h-4 text-gray-400" />
                                                <span className="text-sm">
                                                    Browser:{" "}
                                                    {userDetails.browser}
                                                </span>
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Activity className="w-4 h-4 text-gray-400" />
                                                <span className="text-sm">
                                                    Last Login:{" "}
                                                    {new Date(
                                                        userDetails.lastLogin
                                                    ).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Activity Log */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Recent Activity</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {activityLog.map((activity, index) => (
                                        <div
                                            key={index}
                                            className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                                        >
                                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                                            <div>
                                                <p className="font-medium text-sm">
                                                    {activity.action}
                                                </p>
                                                <p className="text-xs text-gray-600">
                                                    {activity.details}
                                                </p>
                                                <p className="text-xs text-gray-500">
                                                    {new Date(
                                                        activity.date
                                                    ).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Sidebar Stats */}
                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Token Usage</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                                        <p className="text-sm text-gray-600">
                                            Tokens Used
                                        </p>
                                        <p className="text-2xl font-bold text-orange-600">
                                            {userDetails.tokensUsed}
                                        </p>
                                    </div>
                                    <div className="text-center p-4 bg-green-50 rounded-lg">
                                        <p className="text-sm text-gray-600">
                                            Tokens Remaining
                                        </p>
                                        <p className="text-2xl font-bold text-green-600">
                                            {userDetails.tokensRemaining}
                                        </p>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full"
                                            style={{
                                                width: `${
                                                    (userDetails.tokensUsed /
                                                        (userDetails.tokensUsed +
                                                            userDetails.tokensRemaining)) *
                                                    100
                                                }%`,
                                            }}
                                        ></div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Technical Details</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    <div>
                                        <p className="text-sm font-medium">
                                            Subscription
                                        </p>
                                        <Badge
                                            variant="default"
                                            className="bg-purple-500"
                                        >
                                            {userDetails.subscription}
                                        </Badge>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">
                                            IP Address
                                        </p>
                                        <p className="text-sm text-gray-600">
                                            {userDetails.ipAddress}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">
                                            Time Zone
                                        </p>
                                        <p className="text-sm text-gray-600">
                                            {userDetails.timeZone}
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDetails;
