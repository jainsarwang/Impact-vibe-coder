import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { fetchStream } from "@/lib/ivc/fetch-stream";
import { Message } from "@/lib/ivc/types";
import { useStore } from "@/hooks/ivc/useStore";
import Markdown from "markdown-to-jsx";

interface QuestionFlowProps {
    currentInput: string;
    setCurrentInput: React.Dispatch<React.SetStateAction<string>>;
    onBack: () => void;
    handleFormSubmit: (e?: React.FormEvent) => Promise<void>;
}

const QuestionFlow = ({
    currentInput,
    setCurrentInput,
    onBack,
    handleFormSubmit,
}: QuestionFlowProps) => {
    const form = useRef(null);
    const [isLoading, setIsLoading] = useState(true);
    const messages = useStore((state) => state.messages);
    const responding = useStore((state) => state.responding);
    const addMessage = useStore((state) => state.addMessage);

    useEffect(() => {
        const sendInitialMessage = async () => {
            if (!currentInput.trim()) {
                return;
            }

            console.log(
                "Initializing question flow with prompt:",
                currentInput
            );
            // Add initial bot message
            await handleFormSubmit();
        };

        sendInitialMessage();
        setIsLoading(false);
    }, []); // Empty dependency array since this is only for initialization

    useEffect(() => {
        const scrollToBottom = () => {
            const chatContainer = document.querySelector(
                "#chat_window"
            ) as HTMLElement;
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        };
        scrollToBottom();
    }, [messages]);

    // const handleFormSubmit = async (e?: React.FormEvent) => {
    //     e?.preventDefault();

    //     const userMessage: Message = {
    //         id: crypto.randomUUID(),
    //         role: "user",
    //         content: currentInput.trim(),
    //     };
    //     addMessage(userMessage);
    //     setCurrentInput("");

    //     await sendMessage(currentInput, {
    //         deepThinkingMode,
    //         searchBeforePlanning,
    //     });
    // };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();

            // form?.current?.submit();
            handleFormSubmit();
        }
    };

    if (isLoading) {
        return (
            <div className="w-full max-w-4xl mx-auto">
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl blur opacity-25"></div>
                    <div className="relative bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 p-8 shadow-2xl">
                        <div className="text-center">
                            <div className="flex items-center justify-center space-x-3 mb-6">
                                <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                    <Bot className="w-7 h-7 text-white animate-pulse" />
                                </div>
                                <h2 className="text-3xl font-bold text-white">
                                    Preparing Chat Assistant
                                </h2>
                            </div>

                            <p className="text-lg text-purple-200 mb-8">
                                Setting up personalized questions for your
                                project...
                            </p>
                            <div className="flex justify-center space-x-2">
                                <div className="w-3 h-3 bg-purple-400 rounded-full animate-bounce"></div>
                                <div className="w-3 h-3 bg-pink-400 rounded-full animate-bounce delay-100"></div>
                                <div className="w-3 h-3 bg-purple-400 rounded-full animate-bounce delay-200"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-4xl mx-auto">
            <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>

                <div className="relative bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 shadow-2xl overflow-hidden">
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-white/20">
                        <div className="flex items-center space-x-4">
                            <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                <Bot className="w-7 h-7 text-white" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-1">
                                    Project Assistant
                                </h2>
                                <p className="text-purple-200 font-medium">
                                    Let's configure your project together
                                </p>
                            </div>
                        </div>
                        <Button
                            onClick={onBack}
                            variant="outline"
                            className="bg-white/10 border-white/30 text-white hover:bg-white/20"
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back
                        </Button>
                    </div>

                    {/* Chat Messages */}
                    <div
                        id="chat_window"
                        className="h-96 scroll-smooth overflow-y-auto p-6 space-y-4"
                    >
                        {messages.map(
                            (message, idx) =>
                                message.content && (
                                    <div
                                        key={idx}
                                        className={`flex ${
                                            message.role === "user"
                                                ? "justify-end"
                                                : "justify-start"
                                        }`}
                                    >
                                        <div
                                            className={`flex items-start space-x-3 max-w-[80%] ${
                                                message.role === "user"
                                                    ? "flex-row-reverse space-x-reverse"
                                                    : ""
                                            }`}
                                        >
                                            <div
                                                className={`p-2 rounded-full ${
                                                    message.role === "user"
                                                        ? "bg-blue-500"
                                                        : "bg-gradient-to-r from-purple-500 to-pink-500"
                                                }`}
                                            >
                                                {message.role === "user" ? (
                                                    <User className="w-5 h-5 text-white" />
                                                ) : (
                                                    <Bot className="w-5 h-5 text-white" />
                                                )}
                                            </div>
                                            <div
                                                className={`p-4 rounded-2xl w-full ${
                                                    message.role === "user"
                                                        ? "bg-blue-500/20 border border-blue-400/50"
                                                        : "bg-white/10 border border-white/20"
                                                }`}
                                            >
                                                <Markdown className="text-white">
                                                    {message.content}
                                                </Markdown>
                                            </div>
                                        </div>
                                    </div>
                                )
                        )}

                        {responding && (
                            <div className="flex justify-start">
                                <div className="flex items-start space-x-3 max-w-3xl">
                                    <div className="p-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                    <div className="p-4 rounded-2xl bg-white/10 border border-white/20">
                                        <div className="flex space-x-1">
                                            <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-white rounded-full animate-bounce delay-100"></div>
                                            <div className="w-2 h-2 bg-white rounded-full animate-bounce delay-200"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input Area */}
                    <div className="p-6 border-t border-white/20">
                        <form onSubmit={handleFormSubmit} ref={form}>
                            <div className="flex space-x-3">
                                <textarea
                                    value={currentInput}
                                    onChange={(e) =>
                                        setCurrentInput(e.target.value)
                                    }
                                    onKeyDown={handleKeyPress}
                                    placeholder="Type Here..."
                                    className="flex-1 px-4 py-3 bg-black/30 border border-white/30 rounded-xl text-white placeholder-slate-300 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300"
                                    rows={2}
                                />
                                <Button
                                    disabled={!currentInput.trim()}
                                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6"
                                >
                                    <Send className="w-5 h-5" />
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QuestionFlow;
