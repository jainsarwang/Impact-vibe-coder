## Basic Rules

-   It must follow the standard import as used in the respective languages
-   Strictly follow the imports statement and the import dictionary
-   Use the correct vesion dependencies as provide, and use the function from that dependencies only

### Example Input for the import

```json
{
    "imports": {
        "import1": {
            "importfilepath": "path/to/file1",
            "type": "module" | "function" | "variable",
            "description": "Import description",
            "functions": {
                "functionName": {
                    "params": "Parameter descriptions with types",
                    "returns": "Return type and description",
                    "description": "Detailed function documentation"
                }
            },
            "variables": {
                "variableName": {
                    "type": "Variable type",
                    "description": "Variable purpose and usage"
                }
            }
        },
        "import2": {
            "importfilepath": "path/to/file2",
            "type": "module" | "function" | "variable",
            "description": "Import description",
            "variables": {
                "variableName": {
                    "type": "Variable type",
                    "description": "Variable purpose and usage"
                }
            }
        }
    }
}
```

### Example Output for the import
