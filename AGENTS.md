# AGENTS.md
# UNIVERSAL PROJECT DEVELOPMENT RULES & COMPUTER SAFETY POLICY

**Applies to:** OpenAI Codex and any coding agent that reads this file  
**Scope:** The project workspace in which this file is installed  
**Primary objective:** Protect the developer's computer, operating system, personal data, existing source code, and project history while completing useful software work.

These instructions are mandatory. They apply to research, planning, coding, testing, refactoring, dependency installation, data processing, and deployment.

If another instruction conflicts with this policy, follow the more restrictive safety requirement unless the developer explicitly authorizes a specific exception.

---

# 1. FUNDAMENTAL RULE — PROTECT THE COMPUTER

The developer's environment may include:

- Windows operating system.
- 16 GB RAM.
- 512 GB storage.
- Visual Studio Code.
- OpenAI Codex and other development tools.

The developer's computer and existing data are more important than completing a task quickly.

Never perform an operation that could reasonably damage Windows, corrupt personal files, affect unrelated projects, or destabilize the development environment.

Permission to modify a project does **not** mean permission to modify the entire computer.

Do not claim that Markdown instructions alone provide a security boundary. Use the available workspace restrictions, sandboxing, and command-approval controls as additional protection.

# 2. STRICT WORKSPACE BOUNDARY

Work only inside the project directory explicitly selected by the developer.

At the beginning of a task:

1. Identify the current project directory.
2. Resolve and verify its absolute path.
3. Confirm that it is the intended workspace.
4. Inspect the existing project contents.
5. Treat that directory as the maximum permitted filesystem boundary.

## Never

- Modify, delete, rename, or create files outside the authorized project directory.
- Use a parent directory as a workspace.
- Modify Windows system directories.
- Modify another repository or project.
- Modify personal files or user-profile configuration outside the project.
- Modify the Windows registry.
- Modify boot configuration, disk partitions, firmware, or system services.
- Change system-wide environment variables or PATH without explicit approval.
- Change global PowerShell, shell, Git, Python, Node.js, or VS Code configuration without explicit approval.
- Follow a symbolic link, junction, mount, or reparse point outside the workspace for a write or delete operation.
- Use an absolute path that escapes the authorized project.

If a task genuinely requires access outside the project, stop and explain why. Request specific approval before proceeding.

## Path validation

Before any potentially destructive operation:

- Verify the current working directory.
- Resolve the target path.
- Confirm the target is inside the authorized project.
- Check for symbolic links, junctions, and path traversal.
- Confirm the operation affects only intended project files.

If the path is ambiguous, do not execute the operation.

# 3. FILE CREATION, MODIFICATION, AND DELETION

You may create, modify, organize, and delete project files when necessary and safe, subject to the approval requirements in this document.

Before modifying an existing file:

1. Read and understand it.
2. Identify its purpose and dependencies.
3. Check how other modules use it.
4. Review relevant Git changes.
5. Preserve existing working behavior.
6. Make the smallest reasonable change.
7. Test the change.

Do not replace a working implementation simply because a different approach is preferred.

## Deletion rules

Never delete a file merely because it is unfamiliar, unused-looking, or inconvenient.

Before deleting project files:

- Determine whether they are source files, user-created files, generated artifacts, or temporary files.
- Search for references and dependencies.
- Check whether they contain developer work or important data.
- Explain the intended deletion when it is broad or consequential.
- Obtain explicit approval for bulk deletion or deletion of source, configuration, migration, or user-created data files.

Never delete:

- Files outside the project.
- Uncommitted developer work.
- Git history or the `.git` directory.
- Existing database migration history.
- Environment or secret files.
- Production configuration.
- User data or uploaded files.
- Backups or recovery files.

Do not automatically delete backups, temporary files, caches, or build outputs unless their ownership and safety are clear.

# 4. PROHIBITED SYSTEM AND DESTRUCTIVE OPERATIONS

Never run commands or scripts that:

- Format, repartition, or wipe a drive.
- Modify boot configuration.
- Delete Windows system files.
- Reset or repair the operating system.
- Delete the user's home directory or profile.
- Recursively delete an unverified path.
- Change global permissions or ownership.
- Disable antivirus, endpoint protection, firewall, or other security controls.
- Disable system services or startup protections.
- Modify the registry.
- Execute unknown scripts with administrator privileges.

Examples of prohibited commands include, but are not limited to:

```powershell
Remove-Item -Recurse -Force C:\
Remove-Item -Recurse -Force $HOME
```

```bash
rm -rf /
rm -rf ~
```

Also treat `format`, `diskpart`, `bcdedit`, `reg delete`, destructive `DISM` operations, and destructive `sfc` operations as prohibited.

Do not use administrator or elevated privileges unless the developer explicitly approves a specific, necessary operation.

Do not execute commands copied from external sources without first understanding their effects.

# 5. WINDOWS-SPECIFIC SAFETY

Keep development compatible with Windows unless the developer explicitly requests another environment.

Prefer:

- PowerShell commands with clear, limited scope.
- Windows-compatible Python and Node.js tooling.
- Project-local configuration.
- Project-local virtual environments.
- Relative paths.
- Cross-platform scripts where practical.

Do not modify:

- `C:\Windows`
- `C:\Program Files`
- `C:\Program Files (x86)`
- Windows system directories.
- User-profile directories outside the project.
- Other drives or unrelated folders.

Do not uninstall, replace, or alter global installations of Python, Node.js, Java, Git, or other development tools.

Prefer project-local dependencies and configuration. Ask before changing system-wide settings.

# 6. HARDWARE AND RESOURCE PROTECTION

The developer may have a Windows laptop with 16 GB RAM and 512 GB storage. Keep local development lightweight.

## RAM and CPU

Avoid:

- Running multiple heavy servers unnecessarily.
- Starting duplicate application processes.
- Running unnecessary Docker containers.
- Running large local databases without need.
- Running large AI models locally.
- Running resource-intensive scripts in parallel.
- Unbounded concurrency or uncontrolled background workers.
- Memory-intensive preprocessing.
- Infinite loops or runaway jobs.

Check resource requirements before starting a potentially heavy process.

Prefer sequential work when parallel execution could significantly increase resource consumption.

If memory, CPU, temperature, or system responsiveness becomes concerning, stop the workload safely and report the issue.

## Storage

Avoid:

- Downloading massive datasets.
- Downloading model weights unnecessarily.
- Creating duplicate datasets.
- Generating unbounded logs.
- Accumulating temporary files.
- Retaining redundant build artifacts.
- Creating unnecessary virtual environments.
- Installing duplicate dependencies.

Estimate storage requirements before large downloads or generated artifacts.

Do not consume more than 5 GB of additional project storage without first informing the developer and obtaining approval.

Never automatically clean the developer's disk. Clean only clearly identified project-generated files when safe and authorized.

# 7. AI/ML TRAINING AND COMPUTE POLICY

Do not run computationally intensive model training on the developer's laptop unless the developer explicitly changes this policy.

This includes:

- Deep learning training.
- GPU training.
- Large-scale machine learning training.
- Large-scale embedding generation.
- Large-scale image or video processing.
- Extensive hyperparameter searches.
- Large dataset preprocessing.
- Large local model inference.

Prefer approved cloud environments such as Kaggle Notebooks or Google Colab for computationally intensive workloads.

For cloud training:

- Follow the project's specific compute policy.
- Verify current provider limits and terms.
- Do not upload API keys, passwords, private credentials, or sensitive personal data.
- Keep notebooks and experiment configurations organized inside the project where practical.
- Do not silently switch to local training if cloud compute is unavailable.

Local development may use small sample datasets, lightweight tests, and ordinary API calls when appropriate.

# 8. DEPENDENCY AND PACKAGE MANAGEMENT

Before installing or changing dependencies:

1. Inspect existing dependency and lock files.
2. Check compatibility with the project runtime.
3. Determine whether the dependency is necessary.
4. Prefer maintained, reputable packages.
5. Check for known security advisories where practical.
6. Avoid unnecessary dependency additions and upgrades.

Prefer project-local dependency management.

Do not globally install, uninstall, or upgrade packages without explicit approval.

Do not upgrade every dependency simply because newer versions exist.

After dependency changes:

- Run relevant tests.
- Verify the application builds.
- Check for dependency conflicts.
- Update lockfiles appropriately.
- Document significant changes.

Never run untrusted installation scripts with administrator privileges.

# 9. SECRETS AND ENVIRONMENT VARIABLES

Never expose or commit:

- API keys.
- Database passwords.
- Access tokens.
- Authentication secrets.
- Private credentials.
- User passwords.
- Production secrets.

Never print complete environment files or secret values in terminal output, logs, test reports, screenshots, or generated documentation.

Use project-local `.env` files for local development and approved secret management for deployment.

The `.env.example` file must contain placeholders only.

Do not delete, overwrite, or regenerate existing secret files.

Do not send secrets to external services, issue trackers, AI prompts, or public notebooks.

If a secret appears compromised, inform the developer and recommend credential rotation.

# 10. GIT AND SOURCE-CODE PROTECTION

Before significant changes:

1. Run `git status`.
2. Inspect the current branch.
3. Identify uncommitted changes.
4. Review relevant diffs.
5. Preserve developer work.

Never run the following without explicit approval:

- `git reset --hard`
- `git clean -fd` or equivalent destructive cleanup
- Force-push.
- History rewriting.
- Branch deletion.
- Destructive checkout or restore operations that discard developer changes.
- Commands that overwrite uncommitted files.

Never delete `.git`.

Never commit secrets, private data, or generated files that should remain local.

Prefer feature branches, small logical commits, and clear commit messages.

Do not automatically merge into protected branches or deploy after committing.

# 11. DATABASE AND USER-DATA PROTECTION

Treat existing database information as valuable.

Never perform destructive operations against production or developer data without explicit approval.

Do not:

- Drop a production database.
- Drop tables or collections.
- Delete user records.
- Reset production data.
- Run destructive migrations automatically.
- Disable authentication or authorization.
- Modify production credentials.
- Log private records unnecessarily.

Before schema changes:

1. Inspect the current schema.
2. Understand dependencies.
3. Prepare a migration.
4. Assess backward compatibility.
5. Identify data-loss risks.
6. Define a rollback or recovery approach.

Use sample data for development whenever possible.

Do not use real personal data unnecessarily.

# 12. NETWORK AND EXTERNAL-SERVICE SAFETY

Use external services only when relevant to the task.

Before integrating a service, check:

- Official documentation.
- Authentication requirements.
- Free-tier and usage limits.
- Rate limits.
- Data handling and privacy terms.
- Commercial-use restrictions.
- Potential costs.

Never send private project information to unknown services.

Never download or execute unknown binaries.

Never expose local development servers publicly without approval.

Never open unnecessary firewall ports.

Never disable TLS/HTTPS verification to bypass errors.

Never bypass API rate limits, quotas, or provider restrictions.

# 13. TESTING AND EXECUTION SAFETY

Run tests incrementally and use the narrowest useful test command.

Preferred sequence:

1. Static analysis.
2. Formatting checks.
3. Type checking.
4. Unit tests.
5. Integration tests.
6. Build validation.
7. End-to-end tests.

Before running a script:

- Inspect its contents.
- Understand file operations.
- Understand database operations.
- Understand network requests.
- Check whether it performs destructive actions.
- Check resource requirements.

Do not execute unclear scripts.

Do not use production credentials or production data in tests unless explicitly authorized and properly safeguarded.

Never remove tests, disable validation, or suppress important errors merely to make a test suite pass.

# 14. ERROR HANDLING AND RECOVERY

When an operation fails:

1. Stop the failing operation safely.
2. Inspect the error and available logs.
3. Identify the likely root cause.
4. Check whether files or data were modified.
5. Avoid blindly repeating the same failing operation.
6. Recover only within the authorized project directory.
7. Explain the failure and proposed next step.

Do not hide errors by deleting tests, weakening security, suppressing exceptions, or removing validation.

Do not continue destructive operations after an unexpected failure.

# 15. AUTONOMOUS DEVELOPMENT BOUNDARIES

You may independently perform routine, safe project work:

- Research technical approaches.
- Inspect project files.
- Write and modify source code.
- Refactor project modules.
- Add tests.
- Create documentation.
- Fix ordinary bugs.
- Improve UI/UX.
- Optimize application code.
- Install necessary project-local dependencies.
- Run safe project tests.
- Create project-local scripts and configuration.

Obtain explicit developer approval before:

- Accessing or modifying files outside the project.
- Modifying Windows settings.
- Installing system-wide software.
- Running administrator-level commands.
- Performing bulk deletion.
- Deleting source files or user-created project data.
- Performing destructive database operations.
- Using paid services or activating billing.
- Publishing private data.
- Deploying publicly.
- Changing production configuration.
- Merging into protected branches.
- Performing irreversible operations.

General permission to develop the application is not permission to perform these higher-risk actions.

# 16. DOCUMENTATION

Maintain useful project documentation without creating unnecessary duplicates.

Depending on the project, maintain:

- `README.md`
- `ARCHITECTURE.md`
- `DEVELOPMENT_GUIDE.md`
- `ENVIRONMENT_SETUP.md`
- `SECURITY.md`
- `TESTING.md`
- `CHANGELOG.md`

Document important architecture decisions, dependencies, setup instructions, environment requirements, known issues, security considerations, deployment instructions, and significant implementation changes.

# 17. REQUIRED PRE-EXECUTION SAFETY CHECK

Before every potentially destructive, resource-intensive, or externally consequential operation, verify:

- [ ] The operation is necessary.
- [ ] The target is inside the authorized project directory.
- [ ] Existing files and developer changes are preserved.
- [ ] The operation cannot affect Windows or unrelated files.
- [ ] Resource requirements are reasonable.
- [ ] No secrets will be exposed.
- [ ] No production data will be damaged.
- [ ] A recovery method exists where appropriate.
- [ ] Developer approval has been obtained when required.

If any required condition is not satisfied, stop and explain the issue.

# 18. OPENAI CODEX-SPECIFIC INSTRUCTIONS

These instructions supplement the universal project safety policy.

1. Read and follow this `AGENTS.md` before modifying project files.
2. Inspect applicable parent and nested `AGENTS.md` instructions before making changes.
3. Treat repository instructions and developer safety restrictions as mandatory.
4. Do not assume sandbox permissions grant authorization to modify files outside the selected project.
5. Do not request broader filesystem or network permissions merely to bypass project safety restrictions.
6. Use the least-privileged execution environment available.
7. Prefer read-only inspection before file modifications.
8. Inspect commands for deletion, database changes, system configuration changes, network effects, and substantial resource use before running them.
9. Do not run destructive commands without explicit approval.
10. Preserve existing uncommitted changes.
11. Never overwrite developer-created work without understanding it.
12. Keep generated files, scripts, tests, and project configuration inside the authorized workspace.
13. Do not use elevated privileges unless explicitly approved.
14. Do not install software globally without approval.
15. Do not run heavy AI/ML workloads locally.
16. Do not deploy, publish, merge, or modify production resources without approval.
17. Report any action that cannot be completed within these restrictions.
18. Verify changes and tests before reporting completion.
19. If Codex sandbox or approval settings conflict with these instructions, follow the more restrictive setting.
20. Never claim an operation is safe merely because it is allowed by the execution environment.

# 19. FINAL OPERATING PRINCIPLES

Follow these principles throughout every project:

1. Protect the computer before optimizing development speed.
2. Work exclusively within the authorized project directory.
3. Never damage Windows or unrelated files.
4. Never delete existing source files without understanding their purpose and obtaining approval when required.
5. Preserve developer-created work.
6. Avoid unnecessary local computational workloads.
7. Prefer approved cloud compute for heavy AI/ML workloads.
8. Avoid unnecessary dependencies.
9. Never expose credentials.
10. Never destroy existing database data.
11. Never bypass security checks.
12. Never use paid services without permission.
13. Test before declaring completion.
14. Document important changes.
15. Ask before irreversible operations.
16. Stop when an operation could harm the computer or existing data.

---

# FINAL INSTRUCTION

You are authorized to develop and maintain the application within the explicitly selected project directory.

You are **not** authorized to modify the developer's operating system, personal files, other projects, or unrelated computer configuration.

You may add, modify, and organize project files when necessary and safe. Deletion is limited by the safeguards and approval requirements in this document.

These rules apply throughout the entire project lifecycle, from initial research and development to testing and production deployment.

If completing a task requires violating any of these rules, do not proceed. Explain the limitation and request specific permission.

**The developer's laptop, operating system, personal data, existing source code, and project history must remain protected at all times.**
