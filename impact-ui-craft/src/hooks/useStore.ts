import { Message } from "@/lib/types";
import { create } from "zustand";

interface State {
    session_id: string | null;
    messages: Message[];
    responding: boolean;
    directory_structure: Object;
    files: { path: string; name: string; isGenerated: boolean; code: string }[];
    agentWorking: string;
    workflowStarted?: string;
    setState: (newState: Partial<State>) => void;
    addMessage: (message: Message) => void;
    setAgentWorking: (agentName: string) => void;
    setResponding: (responding: boolean) => void;
    updateMessage: (message: Partial<Message> & { id: string }) => void;
    setDirectoryStructure: (structure: Object) => void;
    setFiles: (files: State["files"]) => void;
    addFile: (file: State["files"][0]) => void;
    removeFile: (path: string) => void;
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
    files: [],
    agentWorking: null,
    workflowStarted: undefined,
    setState: (newState: Partial<State>) =>
        useStore.setState((state) => ({ ...state, ...newState })),
    addMessage: (message: Message) =>
        useStore.setState((state) => ({
            messages: [...state.messages, message],
        })),
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
    setFiles: (files: State["files"]) =>
        useStore.setState((state) => ({ files: files })),
    addFile: (file: State["files"][0]) =>
        useStore.setState((state) => ({
            files: [...state.files, file],
        })),
    removeFile: (path: string) =>
        useStore.setState((state) => ({
            files: state.files.filter((file) => file.path !== path),
        })),
    clearMessages: () => useStore.setState({ messages: [] }),
    clearFiles: () => useStore.setState({ files: [] }),
    clearDirectoryStructure: () =>
        useStore.setState({ directory_structure: {} }),
    clearAgentWorking: () => useStore.setState({ agentWorking: null }),
    setWorkflowStarted: (id) => useStore.setState({ workflowStarted: id }),
    clearWorkflowStarted: () => useStore.setState({ workflowStarted: null }),
}));
