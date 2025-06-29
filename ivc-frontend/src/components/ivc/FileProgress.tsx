import React, { useState } from "react";
import {
    FileText,
    Check,
    Loader2,
    Eye,
    Download,
    FolderOpen,
    Code,
    Zap,
    Terminal,
    Bot,
    Users,
} from "lucide-react";
import { useStore } from "@/hooks/ivc/useStore";
import { AgentStatus, FileStatus } from "@/lib/ivc/types";
import { getAgentName } from "@/lib/ivc/agentNames";
import { impactVibeAPI } from "@/services/ivc/impactVibeAPI";
import FileViewer from "./FileViewer";
import VSCodeEditor from "./VSCodeEditor";

interface FileProgressProps {
    prompt: string;
    isGenerating: boolean;
    sessionId?: string;
}

const FileProgress = ({
    prompt,
    isGenerating,
    sessionId,
}: FileProgressProps) => {
    const [selectedFile, setSelectedFile] = useState<FileStatus | null>(null);
    const [showVSCodeEditor, setShowVSCodeEditor] = useState(false);
    const architectAgents = useStore((state) => state.architectAgents);
    const files = useStore((state) => state.files);

    const completedFiles = Object.values(files).filter(
        (f) => f.status === "completed"
    ).length;
    const totalFiles = Object.values(files).length;
    const progress = totalFiles > 0 ? (completedFiles / totalFiles) * 100 : 0;

    const getStatusIcon = (status: FileStatus["status"]) => {
        switch (status) {
            case "pending":
                return (
                    <div className="w-5 h-5 border-2 border-slate-400 rounded-full animate-pulse" />
                );
            case "generating":
                return (
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                );
            case "completed":
                return <Check className="w-5 h-5 text-green-400" />;
        }
    };

    const getStatusColor = (status: FileStatus["status"]) => {
        switch (status) {
            case "generating":
                return "text-blue-300 border-blue-400/50 bg-blue-500/20 shadow-lg shadow-blue-500/25";
            case "completed":
                return "text-green-300 border-green-400/50 bg-green-500/20 shadow-lg shadow-green-500/25";
            case "pending":
            default:
                return "text-slate-400 border-slate-500/50 bg-slate-800/30";
        }
    };

    const getAgentStatusColor = (status: AgentStatus["status"]) => {
        switch (status) {
            case "idle":
                return "text-slate-400 border-slate-500/50 bg-slate-800/30";
            case "working":
                return "text-orange-300 border-orange-400/50 bg-orange-500/20 shadow-lg shadow-orange-500/25";
            case "completed":
                return "text-green-300 border-green-400/50 bg-green-500/20 shadow-lg shadow-green-500/25";
        }
    };

    const handleFileSave = (fileName: string, content: string) => {
        console.log(`Saving file ${fileName}:`, content);
    };

    const handleDownloadProject = async () => {
        if (!sessionId) {
            console.error("No session ID available for download");
            return;
        }

        try {
            const blob = await impactVibeAPI.downloadProject(sessionId);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `impact-vibe-project-${sessionId}.zip`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Error downloading project:", error);
            // You might want to show an error toast here
        }
    };

    return (
        <div className="w-full max-w-7xl mx-auto space-y-8 my-16">
            {/* Agent Status Panel */}
            {Object.keys(architectAgents).length > 0 && (
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-orange-600 to-red-600 rounded-3xl blur opacity-25"></div>
                    <div className="relative bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 p-6 shadow-2xl">
                        <div className="flex items-center space-x-4 mb-6">
                            <div className="p-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl">
                                <Users className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold text-white">
                                    Impact Vibe Coder Agents
                                </h3>
                                <p className="text-orange-200">
                                    Specialized AI agents are building your
                                    project
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {Object.keys(architectAgents).map(
                                (agent, index) => (
                                    <div
                                        key={index}
                                        className={`p-4 rounded-xl border transition-all duration-500 ${getAgentStatusColor(
                                            architectAgents[agent].status
                                        )}`}
                                    >
                                        <div className="flex items-center space-x-3 mb-2">
                                            <Bot className="w-5 h-5" />

                                            <span className="font-semibold capitalize">
                                                {getAgentName(
                                                    architectAgents[agent].name
                                                )}
                                            </span>
                                            {architectAgents[agent].status ===
                                                "working" && (
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                            )}
                                            {architectAgents[agent].status ===
                                                "completed" && (
                                                <Check className="w-4 h-4 text-green-400" />
                                            )}
                                        </div>
                                        <p className="text-sm opacity-80 mb-2">
                                            {architectAgents[agent].currentTask}
                                        </p>
                                        {/* {agent.status === "working" &&
                                        typeof agent.progress === "number" && (
                                            <div className="w-full bg-black/30 rounded-full h-2">
                                                <div
                                                    className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-300"
                                                    style={{
                                                        width: `${agent.progress}%`,
                                                    }}
                                                ></div>
                                            </div>
                                        )} */}
                                    </div>
                                )
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Main Progress Panel */}
            {totalFiles > 0 && (
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>

                    <div className="relative bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 p-8 shadow-2xl">
                        <div className="flex items-center justify-between mb-8">
                            <div className="flex items-center space-x-4">
                                <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl">
                                    <Code className="w-7 h-7 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-bold text-white mb-1">
                                        Project Generation
                                    </h2>
                                    <p className="text-blue-200 font-medium">
                                        Building: {prompt}
                                    </p>
                                </div>
                            </div>
                            <div className="text-right bg-white/10 rounded-2xl p-4 border border-white/20">
                                <div className="text-3xl font-bold text-white">
                                    {completedFiles}
                                    <span className="text-slate-400">
                                        /{totalFiles}
                                    </span>
                                </div>
                                <div className="text-sm text-blue-200 font-medium">
                                    Files completed
                                </div>
                            </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="mb-10">
                            <div className="flex justify-between text-lg text-slate-200 mb-4 font-medium">
                                <span>Overall Progress</span>
                                <span className="text-blue-300">
                                    {Math.round(progress)}%
                                </span>
                            </div>
                            <div className="relative w-full bg-slate-700/50 rounded-full h-4 border border-white/20 overflow-hidden">
                                <div
                                    className="bg-gradient-to-r from-blue-500 via-cyan-400 to-indigo-500 h-full rounded-full transition-all duration-1000 ease-out relative overflow-hidden"
                                    style={{ width: `${progress}%` }}
                                >
                                    <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                                </div>
                            </div>
                        </div>

                        {/* File Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                            {Object.values(files).map((file, index) => (
                                <div
                                    key={index}
                                    className={`relative p-6 rounded-2xl border transition-all duration-500 transform hover:scale-105 ${getStatusColor(
                                        file.status
                                    )}`}
                                >
                                    <div className="flex items-center justify-between mb-3 gap-2">
                                        <div className="flex items-center space-x-3 truncate flex-1">
                                            <FileText className="w-6 h-6" />
                                            <span
                                                title={file.name}
                                                className="font-semibold text-lg w-full truncate"
                                            >
                                                {file.name}
                                            </span>
                                        </div>
                                        <div className="flex items-center space-x-2 w-5">
                                            {getStatusIcon(file.status)}
                                        </div>
                                    </div>

                                    {file.agent && (
                                        <div className="mb-2">
                                            <p className="text-xs opacity-70 capitalize">
                                                Agent:{" "}
                                                {getAgentName(file.agent)}
                                            </p>
                                            <p className="text-xs opacity-70">
                                                {file.task}
                                            </p>
                                        </div>
                                    )}

                                    {file.status === "completed" && (
                                        <div className="flex justify-end space-x-2">
                                            <button
                                                onClick={() =>
                                                    setSelectedFile(file)
                                                }
                                                className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-3 py-2 rounded-lg transition-all duration-300 text-sm font-medium"
                                                title="Quick view file"
                                            >
                                                <Eye className="w-4 h-4" />
                                                <span>View</span>
                                            </button>
                                        </div>
                                    )}

                                    {file.status === "generating" && (
                                        <div className="absolute inset-0 bg-blue-500/10 rounded-2xl animate-pulse pointer-events-none"></div>
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* Action Buttons */}
                        <div className="space-y-6">
                            {!isGenerating && completedFiles === totalFiles && (
                                <div className="text-center">
                                    <div className="inline-flex items-center space-x-2 bg-green-500/20 text-green-300 px-4 py-2 rounded-full border border-green-400/50">
                                        <Check className="w-5 h-5" />
                                        <span className="font-medium">
                                            Project Generated Successfully by
                                            Impact Vibe Coder!
                                        </span>
                                    </div>
                                </div>
                            )}

                            <div className="flex flex-wrap gap-4 justify-center">
                                <button
                                    onClick={() => setShowVSCodeEditor(true)}
                                    className="flex items-center space-x-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-2xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                                >
                                    <Terminal className="w-6 h-6" />
                                    <span>Open in VS Code Editor</span>
                                </button>

                                {!isGenerating &&
                                    completedFiles === totalFiles && (
                                        <button
                                            onClick={handleDownloadProject}
                                            className="flex items-center space-x-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-2xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                                        >
                                            <Download className="w-6 h-6" />
                                            <span>Download Project</span>
                                        </button>
                                    )}

                                {/* <button className="flex items-center space-x-3 bg-white/20 hover:bg-white/30 text-white font-bold py-4 px-8 rounded-2xl border border-white/30 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl">
                                    <FolderOpen className="w-6 h-6" />
                                    <span>Open in External Editor</span>
                                </button> */}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* File Viewer Modal */}
            {selectedFile && (
                <FileViewer
                    file={selectedFile}
                    onClose={() => setSelectedFile(null)}
                />
            )}

            {/* VS Code Editor */}
            {showVSCodeEditor && (
                <VSCodeEditor
                    files={Object.values(files).filter(
                        (f) => f.status !== "pending"
                    )}
                    onClose={() => setShowVSCodeEditor(false)}
                    onSave={handleFileSave}
                />
            )}
        </div>
    );
};

export default FileProgress;
