import React, { useEffect, useState } from "react";
import {
    Send,
    Sparkles,
    Loader2,
    Lightbulb,
    MessageSquare,
    Image,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Toggle } from "@/components/ui/toggle";
import ImageUpload from "./ImageUpload";
import { useStore } from "@/hooks/ivc/useStore";

interface PromptInputProps {
    onGenerate: (prompt?: string, imageFile?: File) => void;
    isGenerating: boolean;
}

const PromptInput = ({ onGenerate, isGenerating }: PromptInputProps) => {
    const [prompt, setPrompt] = useState("");
    const [inputMode, setInputMode] = useState<"text" | "image">("text");
    const clearMessages = useStore((state) => state.clearMessages);

    useEffect(() => {
        clearMessages();
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        e.stopPropagation();

        console.log("prompt", prompt);

        if (prompt.trim() && !isGenerating) {
            onGenerate(prompt.trim());
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            const form = e.target as HTMLElement;
            form.closest("form")?.dispatchEvent(
                new Event("submit", { bubbles: true })
            );
            // handleSubmit();
        }
    };

    const examplePrompts = [
        "Create a modern e-commerce website with React and TypeScript",
        "Build a task management app with drag and drop functionality",
        "Develop a social media dashboard with charts and analytics",
        "Design a portfolio website with animated components",
    ];

    return (
        <div className="w-full max-w-5xl mx-auto mb-12">
            {/* Mode Toggle */}
            <div className="flex justify-center mb-8">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 p-2 shadow-lg">
                    <div className="flex space-x-2">
                        <Toggle
                            pressed={inputMode === "text"}
                            onPressedChange={() => setInputMode("text")}
                            className="flex items-center space-x-2 px-6 py-3 rounded-xl data-[state=on]:bg-blue-500/30 data-[state=on]:text-blue-200 text-slate-300 hover:text-white transition-all duration-300"
                        >
                            <MessageSquare className="w-5 h-5" />
                            <span className="font-medium">Text Prompt</span>
                        </Toggle>
                        <Toggle
                            pressed={inputMode === "image"}
                            onPressedChange={() => setInputMode("image")}
                            className="flex items-center space-x-2 px-6 py-3 rounded-xl data-[state=on]:bg-purple-500/30 data-[state=on]:text-purple-200 text-slate-300 hover:text-white transition-all duration-300"
                        >
                            <Image className="w-5 h-5" />
                            <span className="font-medium">Image Upload</span>
                        </Toggle>
                    </div>
                </div>
            </div>

            {/* Conditional Rendering based on mode */}
            {inputMode === "image" ? (
                <ImageUpload
                    onGenerate={onGenerate}
                    isGenerating={isGenerating}
                />
            ) : (
                <div className="relative group">
                    {/* Glow effect */}
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>

                    <div className="relative bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 p-8 shadow-2xl">
                        <div className="text-center mb-8">
                            <div className="flex items-center justify-center space-x-3 mb-4">
                                <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg">
                                    <Lightbulb className="w-6 h-6 text-white" />
                                </div>
                                <h2 className="text-3xl font-bold text-white">
                                    Describe Your Vision
                                </h2>
                            </div>
                            <p className="text-lg text-slate-200 font-light">
                                Tell us what you want to build and we'll bring
                                it to life
                            </p>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-8">
                            <div className="relative group">
                                <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl opacity-30 group-focus-within:opacity-60 transition duration-300"></div>
                                <textarea
                                    value={prompt}
                                    onKeyDown={handleKeyPress}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="Enter your project description here... (e.g., Create a modern todo app with React, TypeScript, and Tailwind CSS)"
                                    className="relative w-full h-40 px-6 py-4 bg-black/30 border border-white/30 rounded-2xl text-white placeholder-slate-300 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 font-medium"
                                    disabled={isGenerating}
                                />
                                <div className="absolute top-4 right-4">
                                    <Sparkles className="w-6 h-6 text-blue-400 animate-pulse" />
                                </div>
                            </div>

                            <Button
                                type="submit"
                                disabled={!prompt.trim() || isGenerating}
                                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-2xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg hover:shadow-xl text-lg"
                            >
                                {isGenerating ? (
                                    <div className="flex items-center justify-center space-x-3">
                                        <Loader2 className="w-6 h-6 animate-spin" />
                                        <span>Generating Your Project...</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center space-x-3">
                                        <Send className="w-6 h-6" />
                                        <span>Generate Project</span>
                                    </div>
                                )}
                            </Button>
                        </form>

                        <div className="mt-8">
                            <div className="flex items-center space-x-2 mb-4">
                                <Sparkles className="w-5 h-5 text-blue-400" />
                                <p className="text-sm text-slate-300 font-medium">
                                    Try these inspiring examples:
                                </p>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {examplePrompts.map((example, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setPrompt(example)}
                                        disabled={isGenerating}
                                        className="text-left text-sm bg-white/10 hover:bg-white/20 text-blue-200 p-4 rounded-xl border border-white/20 transition-all duration-300 hover:border-blue-400/50 disabled:opacity-50 disabled:cursor-not-allowed hover:transform hover:scale-105 group"
                                    >
                                        <div className="flex items-start space-x-2">
                                            <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 group-hover:animate-pulse"></div>
                                            <span className="flex-1">
                                                {example}
                                            </span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PromptInput;
