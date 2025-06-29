
interface ProjectRequest {
  prompt: string;
  answers: Record<string, any>;
}

interface AgentUpdate {
  agent_name: string;
  status: 'idle' | 'working' | 'completed';
  current_task?: string;
  progress?: number;
}

interface FileUpdate {
  file_name: string;
  status: 'pending' | 'generating' | 'completed';
  content?: string;
  agent?: string;
  task?: string;
}

class ImpactVibeAPI {
  private baseURL: string;
  private eventSource: EventSource | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async startProjectGeneration(projectData: ProjectRequest): Promise<{ session_id: string }> {
    const response = await fetch(`${this.baseURL}/api/generate-project`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(projectData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  subscribeToProgress(
    sessionId: string,
    onAgentUpdate: (update: AgentUpdate) => void,
    onFileUpdate: (update: FileUpdate) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ) {
    this.eventSource = new EventSource(`${this.baseURL}/api/progress/${sessionId}`);

    this.eventSource.addEventListener('agent_update', (event) => {
      try {
        const update: AgentUpdate = JSON.parse(event.data);
        onAgentUpdate(update);
      } catch (error) {
        console.error('Error parsing agent update:', error);
      }
    });

    this.eventSource.addEventListener('file_update', (event) => {
      try {
        const update: FileUpdate = JSON.parse(event.data);
        onFileUpdate(update);
      } catch (error) {
        console.error('Error parsing file update:', error);
      }
    });

    this.eventSource.addEventListener('generation_complete', () => {
      onComplete();
      this.closeConnection();
    });

    this.eventSource.addEventListener('error', (event) => {
      onError('Connection error occurred');
      this.closeConnection();
    });
  }

  closeConnection() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  async downloadProject(sessionId: string): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/api/download-zip/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.blob();
  }
}

export const impactVibeAPI = new ImpactVibeAPI(process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8080');
export type { AgentUpdate, FileUpdate, ProjectRequest };
