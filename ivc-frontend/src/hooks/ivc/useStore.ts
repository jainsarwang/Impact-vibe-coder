import { Message, AgentStatus, FileStatus } from "@/lib/ivc/types";
import { create } from "zustand";

interface State {
    session_id: string | null;
    messages: Message[];
    responding: boolean;
    directory_structure: Object;

    files: Record<string, FileStatus>;
    agentWorking: string;
    architectAgents: Record<string, AgentStatus>;
    workflowStarted?: string;
    frontend_generated: boolean;
    setFrontendGenerated: (frontend_generated: boolean) => void;
    setState: (newState: Partial<State>) => void;
    addMessage: (message: Message) => void;
    addArchitectAgent: (agent: AgentStatus) => void;
    updateArchitectAgent: (
        agent: Partial<AgentStatus> & { name: string }
    ) => void;
    clearArchitectAgents: () => void;
    setAgentWorking: (agentName: string) => void;
    setResponding: (responding: boolean) => void;
    updateMessage: (message: Partial<Message> & { id: string }) => void;
    setDirectoryStructure: (structure: Object) => void;
    setFiles: (files: Record<string, FileStatus>) => void;
    addFile: (file: FileStatus) => void;
    updateFile: (file: Partial<FileStatus> & { name: string }) => void;
    removeFile: (name: string) => void;
    clearMessages: () => void;
    clearFiles: () => void;
    clearDirectoryStructure: () => void;
    clearAgentWorking: () => void;
    setWorkflowStarted: (id: string) => void;
    clearWorkflowStarted: () => void;
}

export const useStore = create<State>(() => ({
    session_id: null,
    messages: [],
    responding: false,
    directory_structure: {},
    files: {},
    architectAgents: {},
    agentWorking: null,
    workflowStarted: undefined,
    frontend_generated: false, // for image to frontend generation
    setFrontendGenerated: (frontend_generated: boolean) =>
        useStore.setState((state) => ({ frontend_generated })),
    setState: (newState: Partial<State>) =>
        useStore.setState((state) => ({ ...state, ...newState })),
    addMessage: (message: Message) =>
        useStore.setState((state) => ({
            messages: [...state.messages, message],
        })),
    addArchitectAgent: (agent: AgentStatus) =>
        useStore.setState((state) => ({
            architectAgents: {
                ...state.architectAgents,
                [agent.name]: agent,
            },
        })),
    updateArchitectAgent: (agent: Partial<AgentStatus> & { name: string }) =>
        useStore.setState((state) => ({
            architectAgents: {
                ...state.architectAgents,
                [agent.name]: {
                    ...state.architectAgents[agent.name],
                    ...agent,
                },
            },
        })),
    clearArchitectAgents: () => useStore.setState({ architectAgents: {} }),
    setAgentWorking: (agentName: string) =>
        useStore.setState((state) => ({ agentWorking: agentName })),
    setResponding: (responding: boolean) =>
        useStore.setState((state) => ({ responding })),
    updateMessage: (message: Partial<Message> & { id: string }) =>
        useStore.setState((state) => {
            const index = state.messages.findIndex((m) => m.id === message.id);
            if (index === -1) {
                return state;
            }
            const updatedMessage = { ...state.messages[index], ...message };
            return {
                messages: [
                    ...state.messages.slice(0, index),
                    updatedMessage,
                    ...state.messages.slice(index + 1),
                ],
            };
        }),
    setDirectoryStructure: (structure: Object) =>
        useStore.setState((state) => ({ directory_structure: structure })),
    setFiles: (files: Record<string, FileStatus>) =>
        useStore.setState((state) => ({ files: files })),
    addFile: (file: FileStatus) =>
        useStore.setState((state) => ({
            files: { ...state.files, [file.name]: file },
        })),
    updateFile: (file: Partial<FileStatus> & { name: string }) =>
        useStore.setState((state) => ({
            files: {
                ...state.files,
                [file.name]: { ...state.files[file.name], ...file },
            },
        })),
    removeFile: (name: string) =>
        useStore.setState((state) => ({
            files: Object.fromEntries(
                Object.entries(state.files).filter(([key]) => key !== name)
            ),
        })),
    clearMessages: () => useStore.setState({ messages: [] }),
    clearFiles: () => useStore.setState({ files: {} }),
    clearDirectoryStructure: () =>
        useStore.setState({ directory_structure: {} }),
    clearAgentWorking: () => useStore.setState({ agentWorking: null }),
    setWorkflowStarted: (id) => useStore.setState({ workflowStarted: id }),
    clearWorkflowStarted: () => useStore.setState({ workflowStarted: null }),
}));
