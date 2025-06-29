import { impactVibeAPI } from "./impactVibeAPI";

export const handleDownloadProject = async (sessionId: string) => {
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