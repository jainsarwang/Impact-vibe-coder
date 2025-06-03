import React, { useEffect, useState } from "react";
import PromptInput from "./PromptInput";
import QuestionFlow from "./QuestionFlow";
import FileProgress from "./FileProgress";
import {
    impactVibeAPI,
    type AgentUpdate,
    type FileUpdate,
} from "../services/impactVibeAPI";
import { useStore } from "@/hooks/useStore";
import { Message } from "@/lib/types";
import { sendChat } from "@/services/chat";

export interface FileStatus {
    name: string;
    status: "pending" | "generating" | "completed";
    content?: string;
    agent?: string;
    task?: string;
}

export interface AgentStatus {
    name: string;
    status: "idle" | "working" | "completed";
    currentTask?: string;
    progress?: number;
}

type BuilderStep = "prompt" | "requirementGathering" | "building";

const ProjectBuilder = () => {
    const [prompt, setPrompt] = useState<string>(null);
    const [currentStep, setCurrentStep] = useState<BuilderStep>("prompt");
    const [isGenerating, setIsGenerating] = useState(false);
    const [files, setFiles] = useState<FileStatus[]>([]);
    const [currentInput, setCurrentInput] = useState("");
    const [agents, setAgents] = useState<AgentStatus[]>([]);
    const [sessionId, setSessionId] = useState<string>("");
    const [uploadedImage, setUploadedImage] = useState<File | null>(null);

    const agentWorking = useStore((state) => state.agentWorking);
    const messages = useStore((state) => state.messages);
    const clearMessages = useStore((state) => state.clearMessages);
    const addMessage = useStore((state) => state.addMessage);
    const workflowStarted = useStore((state) => state.workflowStarted);
    const clearWorkflowStarted = useStore(
        (state) => state.clearWorkflowStarted
    );

    useEffect(() => {
        if (workflowStarted) handleReqGatheringComplete();
    }, [workflowStarted]);

    // setting initial prompt
    const handlePromptSubmit = async (
        userPrompt?: string,
        imageFile?: File
    ) => {
        console.log("Prompt submitted:", userPrompt);
        console.log("Image file:", imageFile);

        setPrompt(userPrompt);
        setCurrentInput(userPrompt);
        setUploadedImage(imageFile || null);

        setCurrentStep("requirementGathering");
        setIsGenerating(false);
    };

    const sendMessage = async (
        msg: string,
        params: {
            deepThinkingMode: boolean;
            searchBeforePlanning: boolean;
        }
    ) => {
        console.log("Sending message:", messages);

        const userMessage: Message = {
            id: crypto.randomUUID(),
            content: msg,
            role: "user",
        };
        try {
            sendChat(userMessage, messages, params);
        } catch (error) {
            console.error("Error sending message:", error);
            // Optionally, you can show an error message to the user
        }
    };

    // executed when requirement gathering is complete
    const handleReqGatheringComplete = async () => {
        setCurrentStep("building");

        await startRealProjectGeneration();
    };

    // WHEN USER CLICK BACK
    const handleBackToPrompt = () => {
        console.log("Going back to prompt");
        setCurrentStep("prompt");

        setFiles([]);

        clearMessages();
        setCurrentInput("");
        setAgents([]);
        setUploadedImage(null);
        clearWorkflowStarted();
        setIsGenerating(false);
    };

    const startRealProjectGeneration = async () => {
        console.log("Starting real project generation with Impact Vibe Coder");
        setIsGenerating(true);

        try {
            // Prepare the request data
            const requestData = {
                prompt,
                ...(uploadedImage && { hasImage: true }),
            };

            // Start project generation with your backend
            // const response = await impactVibeAPI.startProjectGeneration(
            //     requestData
            // );

            // setSessionId(response.session_id);

            // // Subscribe to real-time updates
            // impactVibeAPI.subscribeToProgress(
            //     response.session_id,
            //     handleAgentUpdate,
            //     handleFileUpdate,
            //     handleGenerationComplete,
            //     handleGenerationError
            // );
        } catch (error) {
            console.error("Error starting project generation:", error);
            setIsGenerating(false);
            // You might want to show an error toast here
        }
    };

    const handleAgentUpdate = (update: AgentUpdate) => {
        console.log("Agent update received:", update);
        setAgents((prev) => {
            const existingIndex = prev.findIndex(
                (agent) => agent.name === update.agent_name
            );
            if (existingIndex >= 0) {
                const updated = [...prev];
                updated[existingIndex] = {
                    name: update.agent_name,
                    status: update.status,
                    currentTask: update.current_task,
                    progress: update.progress,
                };
                return updated;
            } else {
                return [
                    ...prev,
                    {
                        name: update.agent_name,
                        status: update.status,
                        currentTask: update.current_task,
                        progress: update.progress,
                    },
                ];
            }
        });
    };

    const handleFileUpdate = (update: FileUpdate) => {
        console.log("File update received:", update);
        setFiles((prev) => {
            const existingIndex = prev.findIndex(
                (file) => file.name === update.file_name
            );
            if (existingIndex >= 0) {
                const updated = [...prev];
                updated[existingIndex] = {
                    name: update.file_name,
                    status: update.status,
                    content: update.content,
                    agent: update.agent,
                    task: update.task,
                };
                return updated;
            } else {
                return [
                    ...prev,
                    {
                        name: update.file_name,
                        status: update.status,
                        content: update.content,
                        agent: update.agent,
                        task: update.task,
                    },
                ];
            }
        });
    };

    const handleGenerationComplete = () => {
        console.log("Project generation completed");
        setIsGenerating(false);
    };

    const handleGenerationError = (error: string) => {
        console.error("Project generation error:", error);
        setIsGenerating(false);
        // You might want to show an error toast here
    };

    return (
        <section className="w-full px-6 pb-16">
            <div className="max-w-6xl mx-auto">
                {currentStep === "prompt" && (
                    <PromptInput
                        onGenerate={handlePromptSubmit}
                        isGenerating={isGenerating}
                    />
                )}

                {(currentStep === "requirementGathering" ||
                    currentStep === "building") && (
                    <QuestionFlow
                        currentInput={currentInput}
                        setCurrentInput={setCurrentInput}
                        onBack={handleBackToPrompt}
                        sendMessage={sendMessage}
                    />
                )}

                {currentStep === "building" && (
                    <FileProgress
                        files={files}
                        prompt={prompt}
                        isGenerating={isGenerating}
                        agents={agents}
                        sessionId={sessionId}
                    />
                )}

                {agentWorking && (
                    <div className="fixed flex gap-2 items-center top-4 right-4 bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 px-4 py-2 shadow-2xl text-white z-50 text-xs">
                        <span className="inline-block w-5 aspect-square rounded-full border-2 border-transparent border-r-white animate-spin"></span>
                        {agentWorking} Responding
                    </div>
                )}
            </div>
        </section>
    );
};

export default ProjectBuilder;
