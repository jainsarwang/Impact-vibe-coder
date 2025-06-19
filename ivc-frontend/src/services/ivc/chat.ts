import { useStore } from "@/hooks/ivc/useStore";
import { fetchStream } from "@/lib/ivc/fetch-stream";
import { ChatEvent, Message } from "@/lib/ivc/types";
import { WorkflowEngine } from "@/utils/ivc/WorkflowEngine";

export const sendChat = async (
    userMessage: Message,
    messages: Message[],
    params: { deepThinkingMode: boolean; searchBeforePlanning: boolean },
    options: { abortSignal?: AbortSignal } = {}
) => {
    const {
        session_id,
        setAgentWorking,
        clearAgentWorking,
        addMessage,
        updateMessage,
        setResponding,
        setWorkflowStarted,
    } = useStore.getState();
    let textMessage: Message | null = null;

    setResponding(true);

    const stream = fetchStream<ChatEvent>(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/chat/stream?session_id=${session_id}`,
        {
            body: JSON.stringify({
                messages: [...messages, userMessage],
                deep_thinking_mode: params.deepThinkingMode,
                search_before_planning: params.searchBeforePlanning,
                debug:
                    location.search.includes("debug") &&
                    !location.search.includes("debug=false"),
            }),
            signal: options.abortSignal,
        }
    );

    try {
        for await (const event of stream) {
            switch (event.type) {
                case "start_of_agent":
                    console.log(event.data);
                    setAgentWorking(event.data.agent_name);

                    textMessage = {
                        id: event.data.agent_id,
                        role: "assistant",
                        content: "",
                    };

                    addMessage(textMessage);
                    break;
                case "message":
                    if (textMessage) {
                        textMessage.content += event.data.delta.content;

                        updateMessage({
                            id: textMessage.id,
                            content: textMessage.content,
                        });
                    }

                    break;
                case "end_of_agent":
                    textMessage = null;

                    clearAgentWorking();
                    break;
                case "start_of_workflow":
                    console.log(event.data);
                    setWorkflowStarted(event.data.workflow_id);
                    const workflowEngine = new WorkflowEngine();
                    const workflow = workflowEngine.start(event);
                    // const workflowMessage: Message = {
                    //     id: event.data.workflow_id,
                    //     role: "assistant",
                    //     type: "workflow",
                    //     content: { workflow: [] },
                    // };
                    // addMessage(workflowMessage);

                    for await (const updatedWorkflow of workflowEngine.run(
                        stream
                    )) {
                        // updateMessage({
                        //     id: workflowMessage.id,
                        //     content: { workflow: updatedWorkflow },
                        // });
                    }
                    break;
                default:
                    break;
            }
        }
    } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") {
            return;
        }
        throw e;
    } finally {
        setResponding(false);
    }
};


export const sendImageGenerationChat = async (
    image: File,
    options: { abortSignal?: AbortSignal } = {}
) => {
    const session_id = useStore.getState().session_id,
        setAgentWorking = useStore.getState().setAgentWorking,
        setResponding = useStore.getState().setResponding,
        clearAgentWorking = useStore.getState().clearAgentWorking,
        setFrontendGenerated = useStore.getState().setFrontendGenerated;

    setResponding(true);

    const formData = new FormData();
    formData.append("file", image);

    const stream = fetchStream<{data: {status: string}, type: "message"}>(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/generate-frontend-code?session_id=${session_id}`,
        {
            body: formData,
            signal: options.abortSignal,
            headers: {
                "Cache-Control": "no-cache",
            }
        }
    );

    try {
        for await (const event of stream) {
            if(event.type === "message") {
                setAgentWorking(event.data.status);
            }
        }

        setFrontendGenerated(true);
    } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") {
            return;
        }
        throw e;
    } finally {
        clearAgentWorking();
        setResponding(false);
    }
};
