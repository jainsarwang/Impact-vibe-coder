import { useStore } from "@/hooks/useStore";
import { fetchStream } from "@/lib/fetch-stream";
import { ChatEvent, Message } from "@/lib/types";
import { WorkflowEngine } from "@/utils/WorkflowEngine";

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
    let textMessage: Message = null;

    setResponding(true);

    const stream = fetchStream<ChatEvent>(
        `${
            import.meta.env.VITE_BACKEND_URL
        }/chat/stream?session_id=${session_id}`,
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
