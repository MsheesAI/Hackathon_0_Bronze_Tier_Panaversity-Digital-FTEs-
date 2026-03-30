---
name: ai-employee-orchestrator
description: |
  Main orchestrator for the AI Employee system. Monitors folders, triggers Qwen for
  processing tasks, manages task flow from Needs_Action to Done, and updates Dashboard.md.
  Use to coordinate autonomous AI employee operations.
---

# AI Employee Orchestrator Skill

Coordinates the AI Employee system - processing tasks, updating dashboard, and managing workflows.

## Prerequisites

- Python 3.13+ installed
- Obsidian vault with required structure
- Qwen loaded with this skill
- File System Watcher running (optional)

## Quick Start

### Start Orchestrator

```bash
cd scripts
python orchestrator.py ../AI_Employee_Vault --interval 30
```

### Dry Run Mode (Test without changes)

```bash
python orchestrator.py ../AI_Employee_Vault --dry-run --interval 10
```

## What It Does

1. **Monitors** `Needs_Action/` folder for pending tasks
2. **Triggers** Qwen to process each task
3. **Processes** approved tasks from `Approved/` folder
4. **Updates** `Dashboard.md` with current status
5. **Moves** completed tasks to `Done/` folder
6. **Logs** all activities to `Logs/` folder

## Folder Monitoring

| Folder | Purpose | Action |
|--------|---------|--------|
| `Needs_Action/` | Pending tasks | Process with Qwen |
| `Approved/` | Human-approved | Execute actions |
| `Pending_Approval/` | Awaiting decision | Wait for human |
| `Done/` | Completed | Archive |
| `Rejected/` | Declined | Archive |

## Dashboard Updates

Automatically updates `Dashboard.md`:

| Metric | Source |
|--------|--------|
| Pending Tasks | Count of `.md` files in `Needs_Action/` |
| Awaiting Approval | Count in `Pending_Approval/` |
| Completed Today | Count in `Done/` |

## Task Processing Flow

```
1. Scan Needs_Action/ for .md files
         ↓
2. Read task file content
         ↓
3. Check Company_Handbook.md for rules
         ↓
4. Determine required action
         ↓
5a. Simple task → Execute → Move to Done/
5b. Sensitive task → Create approval request → Wait
5c. Complex task → Create Plan.md → Execute steps
         ↓
6. Update Dashboard.md
         ↓
7. Log activity to Logs/YYYY-MM-DD.json
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--interval` | 30 seconds | Check interval in seconds |
| `--dry-run` | false | Log without executing |
| `vault_path` | Required | Path to Obsidian vault |

## Usage Examples

### Normal Operation

```bash
python orchestrator.py ../AI_Employee_Vault --interval 30
```

### Fast Processing (Development)

```bash
python orchestrator.py ../AI_Employee_Vault --interval 5
```

### Test Mode (No Changes)

```bash
python orchestrator.py ../AI_Employee_Vault --dry-run
```

## Integration with Qwen

When a task is detected, Qwen:

1. **Reads** the task file from `Needs_Action/`
2. **Consults** `Company_Handbook.md` for rules
3. **Checks** `Business_Goals.md` for context
4. **Creates** plan if multi-step task
5. **Executes** required actions
6. **Moves** file to `Done/` when complete

## Human-in-the-Loop

For sensitive actions, Qwen creates:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
status: pending
---

# Payment Approval Required

**Amount:** $500.00  
**To:** Client A  
**Reason:** Invoice #1234

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.
```

## Activity Logging

All actions logged to `Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-03-30T10:00:00",
  "action_type": "task_processed",
  "actor": "orchestrator",
  "file": "FILE_invoice_abc123.md",
  "result": "success"
}
```

## Complete Setup

### Terminal 1: File Watcher
```bash
python filesystem_watcher.py ../AI_Employee_Vault ../Drop_Folder
```

### Terminal 2: Orchestrator
```bash
python orchestrator.py ../AI_Employee_Vault --interval 30
```

### Test: Drop a File
```bash
echo "Test content" > ../Drop_Folder/test.txt
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard not updating | Check vault path, verify Dashboard.md exists |
| Tasks not processing | Ensure Qwen has access to vault files |
| High CPU usage | Increase --interval to 60+ seconds |
| Permission errors | Check folder read/write access |

## Verification Checklist

- [ ] Orchestrator starts without errors
- [ ] Dashboard.md updates every cycle
- [ ] Tasks move from Needs_Action to Done
- [ ] Logs created in Logs/ folder
- [ ] Dry-run mode works (no file changes)

## Next Steps

After orchestrator is running:
1. Drop a file to test the flow
2. Check Dashboard.md for updates
3. Review logs in Logs/ folder
4. Upgrade to Silver Tier with more watchers
