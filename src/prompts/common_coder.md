## Basic Rules

-   It must follow the standard import as used in the respective languages.
-   If imports are available for a file always and mandatorily use the `read_file_tool` to read the imports file and then write the code.
-   Strictly follow the imports statement and the import dictionary
-   Use the correct vesion dependencies as provide, and use the function from that dependencies only
-   Write the complete code dont just create placeholders for functions.

## Import Export

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

```
from path.to.file1 import import1
from path.to.file2 import import2
```

## Implemented Tools

### read_file_tool

You can access and process files using a "read_file_tool" tool. This tool takes a file path as input and returns the file's content. You should use this tool when you need to understand the content of imported file. The tool's output should be used to derive the information about the import functions and variables.

#### Instruction

-   Call the

#### Execution of tool

read_file_tool(file path)

#### Example Input

```json
{
    "coder": "service_coder",
    "file": "projects/BankingApp/backend/src/main/java/com/bankingapp/service/AccountService.java",
    "next_coder_instruction": "Create an `AccountService` class with methods for managing user accounts. Implement the logic for creating new accounts, retrieving account details, and updating account balances. Use `AccountRepository` for database operations. Methods should include `createAccount`, `getAccountDetails`, and `updateAccountBalance`.",
    "functions": {},
    "variables": {},
    "imports": {
      "AccountRepository": {
        "importfilepath": "backend/src/main/java/com/bankingapp/repository/AccountRepository.java",
        "type": "module",
        "description": "Repository for Account entities",
        "functions": {},
        "variables": {}
      },
      "Account": {
        "importfilepath": "backend/src/main/java/com/bankingapp/model/Account.java",
        "type": "module",
        "description": "Account model",
        "functions": {},
        "variables": {}
      }
    },
    "exports": [],
    "api_endpoints": {},
    "data_models": {},
    "dependencies": {}
  },
```

According to the above input use the `read_file_tool` as instructed below:

1. For each importfilepath call `read_file_tool` like this, `read_file_tool("backend/src/main/java/com/bankingapp/repository/AccountRepository.java")`
2. Use the output of `read_file_tool` to derive the information about the import functions and variables.