---
name: file-system-watcher
description: |
  Monitors a drop folder for new files and creates action files in the Obsidian vault.
  Use when you need to watch for file drops, process new documents, or trigger AI workflows
  based on file system changes. Works with the AI Employee Bronze Tier system.
---

# File System Watcher Skill

Monitors a folder for new files and creates actionable tasks in Obsidian.

## Prerequisites

- Python 3.13+ installed
- Obsidian vault with required folder structure
- This skill loaded in Qwen

## Vault Structure Required

```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Approved/
├── Pending_Approval/
├── Rejected/
├── Logs/
├── Accounting/
├── Briefings/
└── Invoices/
```

## Quick Start

### Start Watching

```bash
cd scripts
python filesystem_watcher.py ../AI_Employee_Vault ../Drop_Folder
```

### Stop Watching

Press `Ctrl+C` in the terminal running the watcher.

## How It Works

1. **Monitors** the `Drop_Folder` for new files
2. **Detects** new files every 5 seconds (polling mode)
3. **Creates** action files in `Needs_Action/` folder
4. **Logs** all activity to `Logs/` folder

## Action File Format

When a file is dropped, creates:

```markdown
---
type: file_drop
original_name: invoice.pdf
size: 245000
size_formatted: 239.26 KB
detected: 2026-03-30T10:00:00
created: 2026-03-30T10:00:00
modified: 2026-03-30T10:00:00
file_hash: a1b2c3d4e5f6g7h8
status: pending
---

# File Drop for Processing

## Original File
- **Name:** invoice.pdf
- **Size:** 239.26 KB
- **Detected:** 2026-03-30 10:00:00

## Suggested Actions
- [ ] Review file contents
- [ ] Categorize file type
- [ ] Process or forward as needed
- [ ] Move original to appropriate location
- [ ] Mark this task as done

## Notes
*Add your notes here*
```

## Usage Patterns

### Pattern 1: Manual File Drop

1. Copy file to `Drop_Folder/`
2. Wait 5-10 seconds
3. Check `Needs_Action/` for new action file
4. Process the task

### Pattern 2: Automated Workflow

```bash
# Start watcher in background
start python filesystem_watcher.py ../AI_Employee_Vault ../Drop_Folder

# Drop files programmatically
echo "Content" > ../Drop_Folder/new_task.txt
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `check_interval` | 5 seconds | How often to check for new files |
| `vault_path` | Required | Path to Obsidian vault root |
| `drop_folder` | Required | Path to folder to monitor |

## Integration with Orchestrator

The watcher creates files → Orchestrator processes them:

```bash
# Terminal 1: Watcher
python filesystem_watcher.py ../AI_Employee_Vault ../Drop_Folder

# Terminal 2: Orchestrator
python orchestrator.py ../AI_Employee_Vault --interval 30
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No action files created | Check watcher is running, verify drop folder path |
| Duplicate files | System tracks by hash - check hash calculation |
| High CPU usage | Increase check_interval to 10+ seconds |
| Permission errors | Ensure read/write access to both folders |

## Verification

1. Drop a test file: `echo "test" > Drop_Folder/test.txt`
2. Wait 10 seconds
3. Check `Needs_Action/` for new `.md` file
4. Verify log file in `Logs/`

## Next Steps

After action file is created:
1. **Orchestrator** detects it in `Needs_Action/`
2. **Qwen** processes the task using Company Handbook rules
3. **Task** moves to `Done/` when complete
4. **Dashboard** updates automatically
