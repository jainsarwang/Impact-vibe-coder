"use client";

import { useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { useStore } from "@/hooks/ivc/useStore";
import Header from "@/components/ivc/Header";
import HeroSection from "@/components/ivc/HeroSection";
import ProjectBuilder from "@/components/ivc/ProjectBuilder";
import { Toaster } from "@/components/ivc/ui/toaster";
import { Toaster as Sonner } from "@/components/ivc/ui/sonner";
import { TooltipProvider } from "@/components/ivc/ui/tooltip";

const queryClient = new QueryClient();

export default function SessionPage({
    params,
}: {
    params: { session_id: string };
}) {
    useEffect(() => {
        useStore.getState()["session_id"] = params.session_id;
    }, [params.session_id]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 relative overflow-hidden">
            {/* Animated background elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-0 right-1/4 w-72 h-72 bg-indigo-500/15 rounded-full blur-3xl animate-pulse delay-1000"></div>
                <div className="absolute top-1/2 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-2xl animate-pulse delay-500"></div>
            </div>

            {/* Content */}
            <div className="relative z-10">
                <Header />
                <HeroSection />
                <ProjectBuilder />
            </div>
        </div>
    );
}
