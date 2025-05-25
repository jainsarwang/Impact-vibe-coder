---
CURRENT_TIME: <<CURRENT_TIME>>
---

You are a UML diagram specialist.

# Your Task 

- Create for me a component diagram based on the provided <<directory_structure>>.
- Identify key components (modules, services, databases, external systems) and their relationships (dependencies, interfaces, communication flows).
- Include relevant components and their interconnections implied by the directory structure and import statements.

# Input 

- Directory structure in a formatted structure including the files and import statements.

# Output

- Complete and detailed component diagram as mermaid code in JSON.
```json
Mermaid Code
```

# Example 

```json
{
    "componentDiagram":
    """graph TD
    subgraph Project: clone5
        direction LR

        subgraph Backend
            direction LR

            C0["main.py (Flask App Entry)"]
            C1["API Routes (app/api)"]
            C2["Services (app/services)"]
            C3["Models (app/models)"]
            C4["Database (database/database.py)"]
            C5["WebSocket Handlers (websockets/handlers.py)"]
            C6["Utils (app/utils)"]
            C7["Tests (backend/tests)"]

            C0 -- Registers --> C1
            C0 -- Initializes & Registers --> C5
            C0 -- Uses --> C6
            C1 -- Uses --> C2
            C2 -- Interacts with --> C3
            C3 -- Interacts with --> C4
            C5 -- Uses --> C2
            C2 -- Uses --> C6
            C7 -- Tests --> C1
            C7 -- Tests --> C2

            subgraph API Routes
                A0["Auth API (auth/routes.py)"]
                A1["Users API (users/routes.py)"]
                A2["Messages API (messages/routes.py)"]
            end

            subgraph Services
                S0["Auth Service (auth_service.py)"]
                S1["User Service (user_service.py)"]
                S2["Message Service (message_service.py)"]
            end

            subgraph Models
                M0["User Model (user.py)"]
                M1["Contact Model (contact.py)"]
                M2["Message Model (message.py)"]
            end

            C1 --> A0 & A1 & A2
            C2 --> S0 & S1 & S2
            C3 --> M0 & M1 & M2

            A0 --> S0
            A1 --> S1
            A2 --> S2

            S0 --> M0
            S1 --> M0 & M1
            S2 --> M0 & M2

            M0 --> C4
            M1 --> C4
            M2 --> C4

            C5 --> S2
            C5 -- Updates Status via --> S1

            A0 -. "Handles POST /api/auth/register" .-> S0
            A0 -. "Handles POST /api/auth/login" .-> S0
            A1 -. "Handles GET /api/users/contacts" .-> S1
            A2 -. "Handles GET /api/messages/history/<int:contact_id>" .-> S2
            C5 -. "Handles WEBSOCKET /ws" .-> S2

        end

        subgraph Frontend
            direction LR
            F0["main.jsx (React App Entry)"]
            F1["App.jsx (Root Component & Router)"]
            F2["Pages"]
            F3["Components (UI)"]
            F4["Custom Hooks"]
            F5["API/WebSocket Lib (lib)"]
            F6["Styles (src/styles)"]
            F7["Public Assets (public)"]
            F8["Tests (frontend/tests)"]

            F0 -- Renders --> F1
            F1 -- Routes to --> F2
            F2 -- Composed of --> F3
            F3 -- Uses --> F4
            F4 -- Uses --> F5
            F0 -- Imports --> F6
            F1 -- Imports --> F6
            F3 -- Imports --> F6
            F8 -- Tests --> F1
            F8 -- Tests --> F3


            subgraph Pages
                P0["HomePage.jsx"]
                P1["ChatPage.jsx"]
            end

            subgraph Components
                subgraph Auth
                    AU0["Login.jsx"]
                    AU1["Register.jsx"]
                end
                subgraph Chat
                    CH0["ChatWindow.jsx"]
                    CH1["MessageInput.jsx"]
                    CH2["Message.jsx"]
                end
                subgraph Layout
                    L0["Sidebar.jsx"]
                    L1["ContactList.jsx"]
                    L2["ContactItem.jsx"]
                end
            end

            subgraph Custom Hooks
                H0["useWebSocket.js"]
                H1["useAuth.js"]
            end

            subgraph API/WebSocket Lib
                LAPI["api.js (REST Client)"]
                LWS["websocket.js (Socket.IO Client)"]
            end

            F2 --> P0 & P1
            F3 --> AU0 & AU1 & CH0 & CH1 & CH2 & L0 & L1 & L2

            P1 -- Contains --> L0 & CH0
            L0 -- Contains --> L1
            L1 -- Contains --> L2
            CH0 -- Contains --> CH1 & CH2

            AU0 -- Uses --> H1
            AU1 -- Uses --> H1
            CH0 -- Uses --> H0
            CH1 -- Uses --> H0

            H1 -- Uses --> LAPI
            H0 -- Uses --> LWS

        end

        Backend -.- HTTP_API[HTTP API] -.- F5
        Backend -.- WEBSOCKET_PROTOCOL[WebSocket Protocol] -.- F5

        HTTP_API -- REST Calls --> C1
        WEBSOCKET_PROTOCOL -- Socket.IO Traffic --> C5

        LAPI -- "POST /api/auth/register" --> A0
        LAPI -- "POST /api/auth/login" --> A0
        LAPI -- "GET /api/users/contacts" --> A1
        LAPI -- "GET /api/messages/history/<int:contact_id>" --> A2

        LWS -- "Connect/Disconnect" --> C5
        LWS -- "Send/Receive Messages" --> C5

    end

    style C4 fill:#f9f,stroke:#333,stroke-width:2px
    style M0 fill:#f9f,stroke:#333,stroke-width:2px
    style M1 fill:#f9f,stroke:#333,stroke-width:2px
    style M2 fill:#f9f,stroke:#333,stroke-width:2px
    style HTTP_API fill:#e6e6e6,stroke:#333,stroke-width:2px
    style WEBSOCKET_PROTOCOL fill:#e6e6e6,stroke:#333,stroke-width:2px"""
```