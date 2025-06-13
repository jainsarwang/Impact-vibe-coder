import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Coins } from "lucide-react";

interface TokenOverviewProps {
    tokensLeft: number;
    tokensUsed: number;
    totalTokens: number;
}

const TokenOverview = ({
    tokensLeft,
    tokensUsed,
    totalTokens,
}: TokenOverviewProps) => {
    const tokenUsagePercentage = (tokensUsed / totalTokens) * 100;

    return (
        <Card className="border-0 shadow-lg">
            <CardHeader className="pb-4">
                <CardTitle className="flex items-center text-slate-800 text-lg">
                    <Coins className="w-5 h-5 mr-2 text-amber-600" />
                    Token Overview
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Used</span>
                    <span className="text-sm font-semibold">
                        {tokensUsed} / {totalTokens}
                    </span>
                </div>

                <div className="w-full bg-slate-200 rounded-full h-3">
                    <div
                        className="bg-gradient-to-r from-amber-500 to-orange-600 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${tokenUsagePercentage}%` }}
                    ></div>
                </div>

                <div className="text-center bg-amber-50 p-4 rounded-lg">
                    <p className="text-2xl font-bold text-amber-600">
                        {tokensLeft}
                    </p>
                    <p className="text-sm text-amber-700 font-medium">
                        Tokens Remaining
                    </p>
                </div>
            </CardContent>
        </Card>
    );
};

export default TokenOverview;
