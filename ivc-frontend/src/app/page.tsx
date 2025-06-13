"use client";

import { useEffect } from "react";
import { redirect } from "next/navigation";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "@/pages/ivc/Index";

const queryClient = new QueryClient();

export default function Home() {
    useEffect(() => {
        const session_id = crypto.randomUUID();
        redirect(`/${session_id}`);
    }, []);

    return null;
}
