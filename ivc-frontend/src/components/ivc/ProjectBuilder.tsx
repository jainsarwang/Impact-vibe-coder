import React, { useEffect, useState } from "react";
import { useStore } from "@/hooks/ivc/useStore";
import { Message } from "@/lib/ivc/types";
import { getAgentName } from "@/lib/ivc/agentNames";
import { sendChat, sendImageGenerationChat } from "@/services/ivc/chat";
import PromptInput from "./PromptInput";
import QuestionFlow from "./QuestionFlow";
import FileProgress from "./FileProgress";

type BuilderStep = "prompt" | "requirementGathering" | "building";

interface SendMessageParams {
    deepThinkingMode: boolean;
    searchBeforePlanning: boolean;
}

const ProjectBuilder: React.FC = () => {
    const [prompt, setPrompt] = useState<string>("");
    const [currentStep, setCurrentStep] = useState<BuilderStep>("prompt");
    const [isGenerating, setIsGenerating] = useState<boolean>(false);
    const [currentInput, setCurrentInput] = useState<string>("");
    const [sessionId, setSessionId] = useState<string>("");
    const [deepThinkingMode, setDeepThinkingMode] = useState(false);
    const [searchBeforePlanning, setSearchBeforePlanning] = useState(false);
    const [uploadedImage, setUploadedImage] = useState<File | null>(null);

    const addMessage = useStore((state) => state.addMessage);
    const clearArchitectAgents = useStore(
        (state) => state.clearArchitectAgents
    );
    const agentWorking = useStore((state) => state.agentWorking);
    const messages = useStore((state) => state.messages);
    const clearMessages = useStore((state) => state.clearMessages);
    const workflowStarted = useStore((state) => state.workflowStarted);
    const clearWorkflowStarted = useStore(
        (state) => state.clearWorkflowStarted
    );
    const clearFiles = useStore((state) => state.clearFiles);

    useEffect(() => {
        if (workflowStarted) handleReqGatheringComplete();
    }, [workflowStarted]);

    useEffect(() => {
        // sending initial prompt
        if (currentInput) {
            handleFormSubmit();
        }
    }, [prompt]);

    const handlePromptSubmit = async (
        userPrompt: string = "",
        imageFile?: File
    ): Promise<void> => {
        console.log("Prompt submitted:", userPrompt);
        console.log("Image file:", imageFile);

        setPrompt(userPrompt);
        setCurrentInput(userPrompt);
        setUploadedImage(imageFile || null);

        if (imageFile) {
            handleImageSubmit(undefined, imageFile);
        } else {
            handleFormSubmit(undefined, userPrompt);
            setCurrentStep("requirementGathering");
        }

        setIsGenerating(false);
    };

    const sendMessage = async (
        msg: string,
        params: SendMessageParams
    ): Promise<void> => {
        console.log("Sending message:", messages);

        const userMessage: Message = {
            id: crypto.randomUUID(),
            content: msg,
            role: "user",
        };
        try {
            await sendChat(userMessage, messages, params);
        } catch (error) {
            console.error("Error sending message:", error);
        }
    };

    const handleFormSubmit = async (e?: React.FormEvent, message?: string) => {
        e?.preventDefault();

        let messageToSend = message || currentInput;

        const userMessage: Message = {
            id: crypto.randomUUID(),
            role: "user",
            content: messageToSend.trim(),
        };
        addMessage(userMessage);
        setCurrentInput("");

        await sendMessage(messageToSend, {
            deepThinkingMode,
            searchBeforePlanning,
        });
    };

    const handleImageSubmit  = async (e?:React.FormEvent, imageFile?: File) => {
        e?.preventDefault();
        if (!imageFile) return;
        
        await sendImageGenerationChat(imageFile);
    }

    const handleReqGatheringComplete = async (): Promise<void> => {
        setCurrentStep("building");
        await startRealProjectGeneration();
    };

    const handleBackToPrompt = (): void => {
        console.log("Going back to prompt");
        setCurrentStep("prompt");
        clearFiles();
        clearMessages();
        setCurrentInput("");
        clearArchitectAgents();
        setUploadedImage(null);
        clearWorkflowStarted();
        setIsGenerating(false);
    };

    const startRealProjectGeneration = async (): Promise<void> => {
        console.log("Starting real project generation with Impact Vibe Coder");
        setIsGenerating(true);

        try {
            // Prepare the request data
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
        }
    };

    // const handleAgentUpdate = (update: AgentUpdate) => {
    //     console.log("Agent update received:", update);
    //     setAgents((prev) => {
    //         const existingIndex = prev.findIndex(
    //             (agent) => agent.name === update.agent_name
    //         );
    //         if (existingIndex >= 0) {
    //             const updated = [...prev];
    //             updated[existingIndex] = {
    //                 name: update.agent_name,
    //                 status: update.status,
    //                 currentTask: update.current_task,
    //                 progress: update.progress,
    //             };
    //             return updated;
    //         } else {
    //             return [
    //                 ...prev,
    //                 {
    //                     name: update.agent_name,
    //                     status: update.status,
    //                     currentTask: update.current_task,
    //                     progress: update.progress,
    //                 },
    //             ];
    //         }
    //     });
    // };

    /* const handleFileUpdate = (update: FileUpdate) => {
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
    }; */

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
                        handleFormSubmit={handleFormSubmit}
                    />
                )}

                {currentStep === "building" && (
                    <FileProgress
                        prompt={prompt}
                        isGenerating={isGenerating}
                        sessionId={sessionId}
                    />
                )}

                {agentWorking && (
                    <div className="fixed flex gap-2 items-center top-4 right-4 bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 px-4 py-2 shadow-2xl text-white z-50 text-xs pointer-events-none capitalize">
                        <span className="inline-block w-5 aspect-square rounded-full border-2 border-transparent border-r-white animate-spin"></span>
                        {getAgentName(agentWorking)} Working
                    </div>
                )}
            </div>
        </section>
    );
};

export default ProjectBuilder;
