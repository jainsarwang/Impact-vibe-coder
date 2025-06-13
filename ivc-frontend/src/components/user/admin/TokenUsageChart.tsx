import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
} from "recharts";
import { TrendingUp } from "lucide-react";

interface User {
    id: string;
    username: string;
    email: string;
    isActive: boolean;
    tokensLeft: number;
    tokensUsed: number;
    totalTokens: number;
}

interface TokenUsageChartProps {
    users: User[];
}

const formatNumber = (num: number): string => {
    if (num >= 100000) {
        return `${(num / 100000).toFixed(1)}L`;
    }
    if (num >= 1000) {
        return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
};

const COLORS = [
    "#8b5cf6",
    "#06b6d4",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#ec4899",
];

const TokenUsageChart = ({ users }: TokenUsageChartProps) => {
    const barChartData = users
        .filter((user) => user.isActive)
        .map((user) => ({
            username:
                user.username.length > 8
                    ? user.username.substring(0, 8) + "..."
                    : user.username,
            tokensUsed: user.tokensUsed,
            tokensLeft: user.tokensLeft,
            totalTokens: user.totalTokens,
        }))
        .slice(0, 6);

    const pieChartData = users
        .filter((user) => user.isActive && user.tokensUsed > 0)
        .map((user) => ({
            name:
                user.username.length > 10
                    ? user.username.substring(0, 10) + "..."
                    : user.username,
            value: user.tokensUsed,
        }))
        .slice(0, 6);

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            {/* Bar Chart - Token Usage by User */}
            <Card className="border-0 shadow-lg">
                <CardHeader className="pb-4 bg-gradient-to-r from-slate-50 to-gray-50">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-purple-600 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <CardTitle className="text-lg text-slate-800">
                                Token Usage Distribution
                            </CardTitle>
                            <p className="text-sm text-slate-600">
                                Tokens used vs available by active users
                            </p>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={barChartData}>
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#e2e8f0"
                            />
                            <XAxis
                                dataKey="username"
                                tick={{ fontSize: 12 }}
                                stroke="#64748b"
                            />
                            <YAxis
                                tick={{ fontSize: 12 }}
                                stroke="#64748b"
                                tickFormatter={formatNumber}
                            />
                            <Tooltip
                                formatter={(value: number, name: string) => [
                                    formatNumber(value),
                                    name === "tokensUsed"
                                        ? "Tokens Used"
                                        : "Tokens Available",
                                ]}
                                labelStyle={{ color: "#334155" }}
                                contentStyle={{
                                    backgroundColor: "#f8fafc",
                                    border: "1px solid #e2e8f0",
                                    borderRadius: "8px",
                                }}
                            />
                            <Bar
                                dataKey="tokensUsed"
                                fill="#8b5cf6"
                                radius={[4, 4, 0, 0]}
                            />
                            <Bar
                                dataKey="tokensLeft"
                                fill="#e2e8f0"
                                radius={[4, 4, 0, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Pie Chart - Token Usage Distribution */}
            <Card className="border-0 shadow-lg">
                <CardHeader className="pb-4 bg-gradient-to-r from-slate-50 to-gray-50">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-indigo-600 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <CardTitle className="text-lg text-slate-800">
                                User Token Consumption
                            </CardTitle>
                            <p className="text-sm text-slate-600">
                                Proportional token usage by active users
                            </p>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={pieChartData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) =>
                                    `${name} ${(percent * 100).toFixed(0)}%`
                                }
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {pieChartData.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value: number) => [
                                    formatNumber(value),
                                    "Tokens Used",
                                ]}
                                contentStyle={{
                                    backgroundColor: "#f8fafc",
                                    border: "1px solid #e2e8f0",
                                    borderRadius: "8px",
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>
        </div>
    );
};

export default TokenUsageChart;
