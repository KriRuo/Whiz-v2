# Command Guardrails for Autonomous Coding Agent
To balance autonomy with safety, we define three levels of command execution for the agent.
## 1. Auto-Approval (Safe Commands)
The agent is permitted to run these without explicit user confirmation.
- **Exploration**: `ls`, `dir`, `tree`, `find`, `fd`, `grep`, `ripgrep`.
- **Read Operations**: `cat`, `type`, `head`, `tail`, `more`.
- **Environment Checks**: `node -v`, `npm -v`, `python --version`, `rustc --version`, `git status`.
- **Local Testing**: `npm test`, `pytest`, `cargo test` (only if they don't modify the environment).
## 2. Protected (User Confirmation Required)
Commands that modify the project structure, dependencies, or local environment.
- **Dependency Management**: `npm install`, `pip install`, `cargo add`.
- **File System**: `mkdir`, `cp`, `mv`.
- **Version Control**: `git add`, `git commit`, `git push`.
- **Server Startup**: `npm run dev`, `uvicorn main:app`, `cargo run`.
- **Framework CLI**: `npx create-next-app`, `supabase init`, `shadcn-ui add`.
## 3. Forbidden (Strictly Prohibited)
Commands that pose a risk to the system or data outside the project scope.
- **Destructive File Operations**: `rm -rf /`, `del /s /q C:\*`.
- **System Configuration**: `chmod` (system paths), `chown`, `regedit`.
- **Information Leakage**: `cat ~/.ssh/*`, `cat ~/.env` (outside project).
- **Network Scanning**: `nmap`, `netstat` (beyond local dev ports).
## 4. Operational Guardrails
- **Timeouts**: No command should run for more than 5 minutes without a status update.
- **Port Management**: Only use ports between `3000-9000` for local servers.
- **Scope Locking**: Any command with a path argument MUST be relative to the project root or contained within it.
- **Supabase Safety**: Migrations must be previewed/validated before application.
## 5. Integration with Implementation Plan
The agent must use these guardrails as follows:
1.  **Exploration**: Run `Auto-Approval` commands as needed to understand the environment.
2.  **Proposal**: In the `implementation_plan.md`, explicitly list any `Protected` commands required for the task.
3.  **Validation**: Post-implementation health checks should prioritize `Auto-Approval` commands to minimize friction.
4.  **Conflicts**: If a command is required but falls into `Forbidden`, the agent MUST propose an alternative or explain why it cannot proceed.
