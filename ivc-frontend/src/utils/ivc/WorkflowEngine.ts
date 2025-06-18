import { nanoid } from "nanoid";

import {
    Message,
    type ChatEvent,
    type StartOfWorkflowEvent,
} from "@/lib/ivc/types";
import { useStore } from "@/hooks/ivc/useStore";

interface FileDocumentation {
    purpose: string;
    functions?: Record<string, unknown>;
    variables?: Record<string, unknown>;
}

function normalizeFilePath(filePath: string) {
    return filePath
        .replace(/\\\\/g, "/")
        .replace(/\\/g, "/")
        .replace(/projects\//, "");
}

export class WorkflowEngine {
    start(event: ChatEvent) {
        // switch (event.type) {
        //     case "start_of_workflow":
        //         break;
        // }
    }

    async *run(stream: AsyncIterable<ChatEvent>) {
        const setAgentWorking = useStore.getState().setAgentWorking;
        // const addMessage = useStore.getState().addMessage;
        const clearAgentWorking = useStore.getState().clearAgentWorking;
        // const updateMessage = useStore.getState().updateMessage;
        const addArchitectAgent = useStore.getState().addArchitectAgent;
        const updateArchitectAgent = useStore.getState().updateArchitectAgent;
        const addFile = useStore.getState().addFile;
        const updateFile = useStore.getState().updateFile;

        let textMessage: Message | null = null;
        let currentFile: string | null = null;

        addArchitectAgent({
            name: "planner",
            status: "working",
            currentTask: "Create Project Development Plan",
            progress: 0,
        });

        for await (const event of stream) {
            switch (event.type) {
                case "start_of_agent":
                    console.log(event.data);

                    // currently working agent
                    setAgentWorking(event.data.agent_name.toLowerCase());

                    // if agent name ends with _coder, then do not update the architect agent instead change coder_master to working
                    if (event.data.agent_name.endsWith("_coder")) {
                        updateArchitectAgent({
                            name: "coder_master",
                            status: "working",
                            progress: 0,
                        });
                    } else {
                        // update architect agent
                        updateArchitectAgent({
                            name: event.data.agent_name.toLowerCase(),
                            status: "working",
                            progress: 0,
                        });
                    }

                    // message for the agent
                    textMessage = {
                        id: event.data.agent_id,
                        role: "assistant",
                        content: "",
                    };
                    // addMessage(textMessage);

                    yield textMessage;
                    break;

                case "end_of_agent":
                    // update architect agent
                    if (event.data.agent_name.endsWith("_coder")) {
                        updateArchitectAgent({
                            name: "coder_master",
                            status: "completed",
                            progress: 100,
                        });

                        //  file generation completed
                        if (currentFile) {
                            updateFile({
                                name: normalizeFilePath(currentFile),
                                agent: event.data.agent_name,
                                status: "completed",
                            });
                        }
                    } else {
                        updateArchitectAgent({
                            name: event.data.agent_name.toLowerCase(),
                            status: "completed",
                            progress: 100,
                        });
                    }

                    // resetting currentFile
                    currentFile = null;
                    // resetting textMessage
                    textMessage = null;

                    clearAgentWorking();
                    break;

                case "start_of_llm":
                    // currentThinkingTask = {
                    //     id: nanoid(),
                    //     type: "thinking",
                    //     state: "pending",
                    //     payload: {
                    //         text: "",
                    //     },
                    // };
                    // currentStep!.tasks.push(currentThinkingTask);
                    // yield this.workflow;

                    break;

                case "end_of_llm":
                    if (!textMessage) {
                        yield textMessage;
                        break;
                    }
                    console.log(textMessage?.content);

                    const jsonRegexMultiline = /```json\n([\s\S]*?)\n```/;
                    const match = textMessage.content.match(jsonRegexMultiline);
                    console.log(match);
                    let jsonData;
                    try {
                        jsonData = JSON.parse(match?.[1].trim() ?? "");
                    } catch (error) {
                        console.log("Agent is not returning valid json");
                    }

                    if (jsonData) {
                        if (event.data.agent_name == "planner") {
                            // extract json from textMessage.content which will be multiline using regex

                            jsonData.steps.forEach(
                                (step: { agent_name: string; title: string }) =>
                                    addArchitectAgent({
                                        name: step.agent_name,
                                        status: "idle",
                                        currentTask: step.title,
                                        progress: 0,
                                    })
                            );

                            console.log(jsonData);
                        } else if (
                            event.data.agent_name == "directory_generator"
                        ) {
                            console.log("Directory Generator", jsonData);

                            Object.entries(
                                jsonData.file_documentation as Record<
                                    string,
                                    FileDocumentation
                                >
                            ).forEach(([file_path, file]) => {
                                addFile({
                                    name: normalizeFilePath(file_path),
                                    status: "pending",
                                    task: file.purpose,
                                    content: "",
                                });
                            });
                        } else if (event.data.agent_name == "code_planner") {
                            console.log("Code Planner", jsonData);

                            jsonData.forEach(
                                (file: {
                                    file: string;
                                    coder: string;
                                    next_coder_instruction: string;
                                }) => {
                                    updateFile({
                                        name: normalizeFilePath(file.file),
                                        agent: file.coder,
                                        task: file.next_coder_instruction,
                                    });
                                }
                            );
                        } else if (event.data.agent_name.endsWith("_coder")) {
                            updateFile({
                                name: normalizeFilePath(currentFile as string),
                                status: "completed",
                                content: jsonData.code,
                            });
                        }
                    }

                    yield textMessage;
                    break;
                case "message":
                    if (event.data.delta.content) {
                        if (textMessage) {
                            textMessage.content += event.data.delta.content;

                            // updateMessage({
                            //     id: textMessage.id,
                            //     content: textMessage.content,
                            // });
                        }
                    } else if (event.data.delta.reasoning_content) {
                        if (textMessage) {
                            textMessage.content +=
                                event.data.delta.reasoning_content;

                            // updateMessage({
                            //     id: textMessage.id,
                            //     content: textMessage.content,
                            // });
                        }
                    }

                    if (!textMessage) break;

                    // extract file name from textMessage.content if the agent is a coder, and the textMessage.content will not be complete json it will be like this: ```json\n{\n \"FILE\": [\n  \"projects\\\\animated_portfolio\\\\js\\\\script.js\"\n ],\n \"programming
                    //  fix this regex for extracting file name
                    // ```json\n{\n \"FILE\": [\n  \"projects\\\\animated_portfolio\\\\js\\\\script.js\"\n ],\n \"programming
                    const fileRegexMultiline = /"FILE":\s*\s*"([^"]+)"\s*/;
                    const fileMatch =
                        textMessage.content.match(fileRegexMultiline);

                    if (fileMatch) {
                        // fileMatch[1] will contain the file path
                        currentFile = normalizeFilePath(fileMatch[1].trim());

                        //  file generation started
                        if (currentFile) {
                            updateFile({
                                name: normalizeFilePath(currentFile),
                                status: "generating",
                            });
                        }
                    }

                    if (currentFile) {
                        // extract file content from textMessage.content using regex {FILE: [file_path], programming_language: "javascript", content: "file_content
                        const fileContentRegex = /"content":\s*"([^"]+)"/;
                        const fileContentMatch =
                            textMessage.content.match(fileContentRegex);

                        updateFile({
                            name: normalizeFilePath(currentFile),
                            content: fileContentMatch?.[1] || "",
                        });
                    }
                    // yield this.workflow;
                    break;
                case "tool_call":
                    // toolCallTask = {
                    //     id: event.data.tool_call_id,
                    //     type: "tool_call",
                    //     state: "pending",
                    //     payload: {
                    //         toolName: event.data.tool_name,
                    //         input: event.data.tool_input,
                    //     },
                    // };
                    // pendingToolCallTasks.push(toolCallTask);
                    // currentStep!.tasks.push(toolCallTask);
                    // yield this.workflow;
                    break;
                case "tool_call_result":
                    // toolCallTask = pendingToolCallTasks.find(
                    //     (task) => task.id === event.data.tool_call_id
                    // );
                    // if (toolCallTask) {
                    //     toolCallTask.state = "success";
                    //     toolCallTask.payload.output = event.data.tool_result;
                    //     pendingToolCallTasks = pendingToolCallTasks.filter(
                    //         (task) => task.id !== event.data.tool_call_id
                    //     );
                    // }
                    // yield this.workflow;
                    break;
                case "end_of_workflow":
                    // this.workflow.finalState = {
                    //     messages: event.data.messages,
                    // };
                    return;
                default:
                    break;
            }
        }
    }
}
