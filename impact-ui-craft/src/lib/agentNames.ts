export const getAgentName = (agent: string) => {
    switch (agent) {
        case "planner":
            return "Project Planner";
        case "diagram":
            return "Architect";
        case "import-export":
            return "Import/Export";
        case "figma_coder":
            return "Image Generator";
        default:
            return agent.replace("_", " ").replace("-", " ");
    }
};
