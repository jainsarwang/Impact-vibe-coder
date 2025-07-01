"use client";
import React from 'react'
import "./page.css";
import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

const queryClient = new QueryClient();

export default function SessionLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const [isOpen, setIsOpen] = React.useState(false);
    return (
        <QueryClientProvider client={queryClient}>
            <TooltipProvider>
                <div className="min-h-screen flex relative overflow-hidden">
                    <div
                        className={`absolute h-screen w-72 bg-slate-900/50 backdrop-blur-xl border-r border-slate-700/30 p-6 flex flex-col gap-6 z-[100] shadow-[0_8px_32px_rgba(31,41,55,0.4)] transition-transform duration-300 ${
                            isOpen ? "translate-x-0" : "-translate-x-full"
                        } overflow-hidden`}
                    >
                        <div className="space-y-3">
                            <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-blue-400"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                >
                                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                                </svg>
                                Model Selection
                            </h3>
                            <select className="w-full bg-slate-800/80 text-slate-200 rounded-lg border border-slate-600/50 p-3 transition-all hover:border-blue-500/50 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none backdrop-blur-sm">
                                <option value="gpt-4">GPT-4</option>
                                <option value="gpt-3.5-turbo">
                                    GPT-3.5 Turbo
                                </option>
                                <option value="claude-2">Claude 2</option>
                            </select>
                        </div>

                        <div className="space-y-3">
                            <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5 text-blue-400"
                                    viewBox="0 0 20 20"
                                    fill="currentColor"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                                API Configuration
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm font-medium text-slate-300 block mb-2">
                                        API Key
                                    </label>
                                    <input
                                        type="password"
                                        className="w-full bg-slate-800/80 text-slate-200 rounded-lg border border-slate-600/50 p-3 transition-all hover:border-blue-500/50 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none backdrop-blur-sm"
                                        placeholder="Enter your API key"
                                    />
                                </div>
                            </div>
                        </div>

                        <button className="mt-auto bg-gradient-to-br from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold rounded-lg py-3 px-4 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-lg hover:shadow-blue-500/25 active:scale-[0.98] backdrop-blur-sm">
                            Apply Settings
                        </button>
                    </div>

                    <div className="fixed bottom-4 left-0 z-[100]">
                        <button
                            className="bg-slate-800/60 backdrop-blur-sm hover:bg-slate-700/70 text-slate-200 rounded-r-full px-5 py-3.5 shadow-[0_8px_32px_rgba(0,0,0,0.2)] border border-slate-700/50 transition-all duration-300 hover:scale-105 hover:shadow-[0_8px_40px_rgba(31,41,55,0.3)] group"
                            onClick={() => setIsOpen(!isOpen)}
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-6 w-6 transition-transform duration-300"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M4 6h16M4 12h16m-7 6h7"
                                />
                            </svg>
                        </button>
                    </div>

                    <Toaster />
                    <Sonner />
                    {children}
                </div>
            </TooltipProvider>
        </QueryClientProvider>
    );
}
