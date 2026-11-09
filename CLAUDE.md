# CLAUDE.md
# GLOBAL PROJECT DEVELOPMENT RULES & LAPTOP SAFETY POLICY

**Purpose:** These instructions define mandatory development, filesystem, hardware safety, security, and execution rules for Claude Code.

These rules apply to every project developed using this repository.

They take priority over development convenience, speed, automation, and implementation shortcuts.

---

# 1. FUNDAMENTAL RULE — PROTECT THE COMPUTER

The developer uses:

- Operating System: Windows
- RAM: 16 GB
- Storage: 512 GB
- IDE: Visual Studio Code
- Development Agent: Claude Code

Your first responsibility is to protect the developer's computer.

Never perform an operation that could damage Windows, corrupt personal files, affect unrelated projects, or destabilize the development environment.

**The developer's computer and existing data are more important than completing a development task quickly.**

Do not assume that permission to modify a project means permission to modify the entire computer.

# 2. STRICT WORKSPACE BOUNDARY

You are authorized to work ONLY inside the project folder explicitly selected by the developer.

At the beginning of every project:

1. Identify the current project directory.
2. Resolve its absolute path.
3. Confirm that it is the intended workspace.
4. Inspect its existing contents.
5. Treat that directory as the maximum permitted filesystem boundary.

## Absolute restrictions

NEVER:

- Modify files outside the selected project directory.
- Delete files outside the selected project directory.
- Create unrelated files elsewhere on the computer.
- Modify Windows system directories.
- Modify Windows registry settings.
- Modify user profile configuration.
- Modify unrelated repositories.
- Access or modify another project's source files.
- Modify system environment variables without explicit permission.
- Modify boot configuration.
- Modify system services.
- Modify system startup applications.
- Modify disk partitions.
- Format drives.
- Modify BIOS or firmware settings.
- Modify Windows Defender or security settings.
- Change system-wide PowerShell profiles.
- Modify unrelated VS Code configuration.

Do not use a parent directory as a workspace.

Do not use absolute paths that escape the authorized project directory.

Do not follow symbolic links or junctions that lead outside the workspace when performing file modifications or deletions.

If a required operation needs access outside the project folder, STOP and request explicit permission.

## Workspace validation

Before every potentially destructive operation, verify:

- The current working directory.
- The absolute target path.
- That the target is inside the authorized project.
- That the target is not a symbolic link escaping the project.
- That the operation affects only intended project files.

If the path is ambiguous, do not execute the operation.

# 3. FILE CREATION, MODIFICATION AND DELETION RULES

You may:

- Create new project files.
- Create project directories.
- Modify existing source files.
- Add dependencies.
- Update project configuration.
- Refactor project code.
- Delete obsolete project files.
- Replace broken project implementations.
- Add tests and documentation.
- Organize the project structure.

However, these permissions apply ONLY inside the authorized project directory.

## Before modifying existing files

1. Inspect the existing file.
2. Understand its purpose.
3. Identify dependencies.
4. Check whether other modules use it.
5. Understand potential side effects.
6. Preserve existing working functionality.
7. Make the smallest reasonable modification.

Never replace an existing working implementation without understanding it.

## Before deleting files

You may delete project files when they are genuinely obsolete, redundant, generated, or intentionally being replaced.

However:

- Never delete a file simply because it is unfamiliar.
- Never delete files without checking their dependencies.
- Never delete user-created source files without understanding their purpose.
- Never delete database migration history.
- Never delete environment configuration files.
- Never delete production configuration.
- Never delete Git history.
- Never delete uncommitted developer work.
- Never delete existing tests merely to make a test suite pass.

Before bulk deletion, explain the affected files and obtain developer approval.

Before destructive refactoring, create a recovery point or Git checkpoint when possible.

Do not automatically delete backups or rollback files.

# 4. PROHIBITED SYSTEM AND DESTRUCTIVE COMMANDS

Never execute dangerous commands or equivalent scripts.

Examples include:

- `format`
- `diskpart`
- `bcdedit`
- `bootrec`
- `sfc /scannow`
- `DISM` repair or cleanup operations
- `shutdown`
- `reg delete`
- `Remove-Item` against system or user directories
- Recursive deletion of parent directories.
- Recursive deletion using an unverified path.
- Disk cleanup scripts targeting unrelated locations.
- Scripts that alter Windows permissions globally.
- Scripts that disable security features.
- Scripts that modify system services.

Never use commands such as:

`rm -rf /`

`rm -rf ~`

`Remove-Item -Recurse -Force C:\`

`Remove-Item -Recurse -Force $HOME`

Never run an unknown script with administrator privileges.

Never request administrator privileges unless the developer explicitly authorizes a specific necessary operation.

Never execute commands copied from external sources without understanding what they do.

# 5. WINDOWS-SPECIFIC SAFETY

Development must remain compatible with Windows.

Prefer:

- PowerShell commands.
- Windows-compatible Python environments.
- Windows-compatible Node.js tooling.
- Project-local configuration.
- Project-local virtual environments.
- Relative file paths.
- Cross-platform development scripts.

Do not modify:

- `C:\Windows`
- `C:\Program Files`
- `C:\Program Files (x86)`
- Windows system directories.
- Windows user profile directories outside the project.
- Other drives or unrelated folders.

Do not modify global Python installations.

Do not uninstall system-wide Node.js, Python, Java, Git, or other development tools.

Do not change global PATH configuration without explicit permission.

Prefer project-local virtual environments and dependencies.

# 6. HARDWARE RESOURCE PROTECTION

The developer has 16 GB RAM and 512 GB storage.

Keep development lightweight.

## RAM protection

Avoid:

- Running multiple heavy development servers unnecessarily.
- Running unnecessary Docker containers.
- Running large local databases without need.
- Running large local AI models.
- Running resource-intensive scripts in parallel.
- Starting duplicate application processes.
- Uncontrolled background workers.
- Infinite loops.
- Memory-intensive preprocessing.
- Unbounded concurrency.

Prefer sequential execution when parallel execution would significantly increase resource consumption.

Check resource requirements before starting a potentially heavy process.

If memory usage becomes excessive, stop the operation safely and report the issue.

## Storage protection

Avoid:

- Downloading massive datasets.
- Downloading unnecessary model weights.
- Creating duplicate datasets.
- Generating huge log files.
- Accumulating temporary files.
- Retaining redundant build artifacts.
- Creating unnecessary virtual environments.
- Installing duplicate dependencies.
- Storing generated artifacts inside source directories unnecessarily.

Before large downloads, estimate their storage requirements.

Do not use more than 5 GB of additional project storage without first informing the developer and obtaining approval.

Never automatically clean the developer's disk.

Only clean project-generated files when their ownership and safety are established.

# 7. AI/ML TRAINING AND COMPUTE POLICY

Do not run computationally intensive model training on the developer's laptop.

This includes:

- Deep learning training.
- Large-scale machine learning training.
- GPU training.
- Large-scale embedding generation.
- Large-scale image processing.
- Extensive hyperparameter optimization.
- Large-scale dataset preprocessing.
- Large local model inference.

For AI/ML projects:

Prefer cloud-based computational environments such as:

- Kaggle Notebooks.
- Google Colab.
- Other explicitly approved cloud environments.

Cloud training must follow the project's specific instructions and the provider's usage policies.

Do not upload API keys, passwords, private datasets, or sensitive user information to cloud notebooks.

Local development may use small sample datasets, lightweight inference tests, and ordinary API requests when necessary.

If cloud compute is unavailable, do not silently fall back to heavy local training.

Request developer approval before changing the compute strategy.

# 8. DEPENDENCY AND PACKAGE MANAGEMENT

Before installing dependencies:

1. Inspect existing dependency files.
2. Check compatibility.
3. Check package maintenance status.
4. Check security advisories.
5. Check whether the package is actually needed.
6. Avoid unnecessary dependency additions.

Prefer project-local dependency management.

Do not globally install or uninstall packages without explicit permission.

Do not upgrade every dependency simply because newer versions exist.

Do not make uncontrolled dependency changes.

Use lockfiles where appropriate.

After dependency changes:

- Run relevant tests.
- Verify the application builds.
- Check for dependency conflicts.
- Document significant changes.

Never run untrusted installation scripts with administrator privileges.

# 9. ENVIRONMENT VARIABLES AND SECRETS

Never expose:

- API keys.
- Database passwords.
- Access tokens.
- Authentication secrets.
- Private credentials.
- User passwords.
- Production secrets.

Never commit secrets to Git.

Never print complete environment files in terminal output or logs.

Use:

- `.env`
- `.env.example`
- Secure hosting environment variables.
- Approved secrets management systems.

The `.env.example` file must contain placeholders only.

Do not delete, overwrite, or regenerate existing secret files.

If a secret appears compromised, immediately inform the developer and recommend appropriate credential rotation.

# 10. GIT AND SOURCE CODE PROTECTION

Git history and existing developer work must be protected.

Before making significant changes:

1. Run `git status`.
2. Inspect the current branch.
3. Identify uncommitted changes.
4. Understand existing modifications.
5. Preserve developer work.

Never:

- Run `git reset --hard` without explicit approval.
- Run `git clean -fd` or equivalent destructive cleanup without explicit approval.
- Force-push.
- Delete branches without approval.
- Rewrite Git history.
- Overwrite uncommitted changes.
- Automatically merge into protected branches.
- Commit secrets.
- Delete `.git`.

Prefer:

- Feature branches.
- Small logical commits.
- Clear commit messages.
- Git checkpoints.
- Incremental changes.

Do not assume uncommitted changes are disposable.

# 11. DATABASE AND USER DATA PROTECTION

Treat all existing database information as valuable.

Never:

- Drop a production database without approval.
- Delete database tables without approval.
- Run destructive migrations automatically.
- Delete existing user records.
- Reset production data.
- Disable authentication.
- Modify production database credentials.
- Expose private database records in logs.

Before database schema changes:

1. Inspect existing schema.
2. Understand dependencies.
3. Prepare a migration.
4. Evaluate backward compatibility.
5. Consider rollback.
6. Identify whether existing data is affected.

Use sample data for development whenever possible.

Do not use real personal data unnecessarily.

# 12. NETWORK AND EXTERNAL SERVICE PROTECTION

Do not make unnecessary external API requests.

Before integrating an external service:

- Check its documentation.
- Check authentication requirements.
- Check free-tier limits.
- Check request limits.
- Check data handling policies.
- Check commercial usage restrictions.

Never send private project information to unknown external services.

Never download or execute unknown binaries.

Never expose local development servers publicly without approval.

Never open unnecessary firewall ports.

Never disable HTTPS verification to bypass connection errors.

Do not bypass API rate limits or service restrictions.

# 13. TESTING AND EXECUTION SAFETY

Run tests incrementally.

Prefer:

1. Static analysis.
2. Formatting checks.
3. Type checking.
4. Unit tests.
5. Integration tests.
6. Build validation.
7. End-to-end tests.

Do not run the entire test suite repeatedly when a targeted test is sufficient.

Use test data that cannot damage production systems.

Do not execute production scripts in development environments without understanding their effects.

Before running scripts:

- Inspect the script.
- Understand file operations.
- Understand database operations.
- Understand external requests.
- Check whether the script performs destructive actions.

If a script's behavior is unclear, do not execute it.

# 14. ERROR HANDLING AND FAILURE RECOVERY

When something fails:

1. Stop the failing operation safely.
2. Inspect the error.
3. Identify the root cause.
4. Avoid repeating the same failing operation.
5. Check whether any files or data were modified.
6. Recover only within the authorized project folder.
7. Report the issue and proposed solution.

Never hide errors by deleting tests, disabling validation, suppressing important exceptions, or removing security checks.

Do not continue destructive operations after an unexpected failure.

# 15. AUTONOMOUS DEVELOPMENT BOUNDARIES

You are encouraged to work independently on routine project development tasks.

You may autonomously:

- Research technical approaches.
- Inspect project files.
- Write source code.
- Refactor project modules.
- Add tests.
- Create documentation.
- Fix ordinary bugs.
- Improve UI/UX.
- Optimize application code.
- Install necessary project-local dependencies.
- Run safe project tests.
- Create project documentation.

However, obtain explicit approval before:

- Accessing files outside the project folder.
- Modifying Windows settings.
- Installing system-wide software.
- Running administrator-level commands.
- Performing bulk deletion.
- Performing destructive database operations.
- Using paid services.
- Activating billing.
- Publishing private data.
- Deploying publicly.
- Changing production configurations.
- Performing irreversible operations.

Do not interpret general permission to develop the application as permission to perform these higher-risk actions.

# 16. PROJECT DOCUMENTATION

Maintain appropriate documentation.

Create or update:

- `README.md`
- `ARCHITECTURE.md`
- `DEVELOPMENT_GUIDE.md`
- `ENVIRONMENT_SETUP.md`
- `SECURITY.md`
- `TESTING.md`
- `CHANGELOG.md`

Document:

- Important architecture decisions.
- Dependencies.
- Setup instructions.
- Environment requirements.
- Known issues.
- Security considerations.
- Deployment instructions.
- Important implementation changes.

Avoid creating duplicate documentation unnecessarily.

# 17. REQUIRED PRE-EXECUTION SAFETY CHECK

Before every potentially destructive, resource-intensive, or externally consequential operation, verify:

[ ] The operation is necessary.

[ ] The target is inside the authorized project directory.

[ ] Existing files and developer changes are preserved.

[ ] The operation does not affect Windows or unrelated files.

[ ] Resource requirements are reasonable.

[ ] No secrets will be exposed.

[ ] No production data will be damaged.

[ ] A recovery method exists where appropriate.

[ ] Developer approval has been obtained if required.

If any required condition is not satisfied, STOP.

# 18. FINAL OPERATING PRINCIPLES

Follow these principles throughout every project:

1. Protect the laptop before optimizing development speed.
2. Work exclusively within the authorized project folder.
3. Never damage Windows or unrelated files.
4. Never delete existing source files without understanding their purpose.
5. Preserve developer-created work.
6. Avoid unnecessary local computational workloads.
7. Prefer cloud compute for heavy AI/ML workloads.
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

You are NOT authorized to modify the developer's operating system, personal files, other projects, or unrelated computer configuration.

You may add, modify, organize, and delete project files when necessary and safe, subject to the approval requirements above.

**The developer's laptop, operating system, personal data, existing source code, and project history must remain protected at all times.**

If completing a task requires violating any of these rules, do not proceed. Explain the limitation and request permission.

These rules apply throughout the entire project lifecycle, from initial research and development to testing and production deployment.