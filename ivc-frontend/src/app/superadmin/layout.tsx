"use client";

import "./page.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/superadmin/ui/toaster";
import { Toaster as Sonner } from "@/components/superadmin/ui/sonner";
import { TooltipProvider } from "@/components/superadmin/ui/tooltip";

const queryClient = new QueryClient();

export default function SuperAdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <QueryClientProvider client={queryClient}>
            <TooltipProvider>
                <Toaster />
                <Sonner />
                {children}
            </TooltipProvider>
        </QueryClientProvider>
    );
}
