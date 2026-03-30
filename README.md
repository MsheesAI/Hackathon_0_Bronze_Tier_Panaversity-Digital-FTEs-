# AI Employee - Bronze Tier (Qwen Skills)

A local-first, agent-driven Personal AI Employee built with **Qwen** and Obsidian.

## Overview

This is a **Bronze Tier** implementation of the Panaversity Hackathon 0 challenge using **Qwen Skills** instead of Claude Code (which is paid). It provides the foundational layer for an autonomous AI employee that:

- Monitors a drop folder for new files
- Creates actionable tasks in an Obsidian vault
- Triggers Qwen for processing
- Manages task flow with human-in-the-loop approval
- Maintains audit logs and dashboard

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Drop Folder    │────▶│  FileSystem      │────▶│  Needs_Action   │
│  (Input)        │     │  Watcher Skill   │     │  Folder         │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Dashboard.md   │◀────│  Orchestrator    │◀────│  Qwen           │
│  (Status)       │     │  Skill           │     │  (Reasoning)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts |
| [Qwen Code](https://qwen.ai/) | Latest | **Free** reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base |

## Installation

### 1. Install Python Dependencies

```bash
cd .qwen/skills
pip install -r requirements.txt
```

### 2. Open the Obsidian Vault

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder

## Usage

### Load Qwen Skills

In Qwen Code, load these skills:

1. **file-system-watcher** - Monitors drop folder
2. **ai-employee-orchestrator** - Coordinates tasks
3. **ai-employee-dashboard** - Updates dashboard

### Start the File System Watcher

```bash
cd .qwen/skills/file-system-watcher
python filesystem_watcher.py ../../AI_Employee_Vault ../../Drop_Folder
```

### Start the Orchestrator

In a **separate terminal**:

```bash
cd .qwen/skills/ai-employee-orchestrator
python orchestrator.py ../../AI_Employee_Vault --interval 30
```

### Test the System

1. **Drop a file** into the `Drop_Folder` directory
2. **Watch** as the FileSystemWatcher creates an action file
3. **Orchestrator** detects the task and triggers Qwen
4. **Qwen** processes the task and moves it to `Done/`

### Dry Run Mode

Test without executing actions:

```bash
python orchestrator.py ../../AI_Employee_Vault --dry-run --interval 10
```

## Qwen Skills Structure

```
.qwen/skills/
├── file-system-watcher/
│   ├── SKILL.md                    # Skill documentation
│   ├── base_watcher.py             # Base watcher class
│   └── filesystem_watcher.py       # File system monitor
├── ai-employee-orchestrator/
│   ├── SKILL.md                    # Skill documentation
│   └── orchestrator.py             # Main coordinator
├── ai-employee-dashboard/
│   └── SKILL.md                    # Dashboard management
├── browsing-with-playwright/       # Browser automation
└── requirements.txt                # Python dependencies
```

## Obsidian Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md                    # Real-time status
├── Company_Handbook.md             # Rules of engagement
├── Business_Goals.md               # Q1 2026 objectives
├── Inbox/                          # Raw incoming items
├── Needs_Action/                   # Tasks requiring attention
├── Plans/                          # Multi-step task plans
├── Approved/                       # Human-approved actions
├── Pending_Approval/               # Awaiting human decision
├── Rejected/                       # Declined items
├── Done/                           # Completed tasks
├── Logs/                           # Activity logs
├── Accounting/                     # Financial records
├── Briefings/                      # CEO briefings
└── Invoices/                       # Generated invoices
```

## Key Features

### File System Watcher Skill

- Monitors a drop folder for new files
- Creates `.md` action files with metadata
- Supports both event-driven (watchdog) and polling modes
- Calculates file hash to avoid duplicates

### Orchestrator Skill

- Monitors `Needs_Action` folder for pending tasks
- Triggers Qwen for task processing
- Processes approved tasks from `Approved/` folder
- Updates `Dashboard.md` with current status
- Logs all activities to JSON files

### Dashboard Skill

- Real-time task counts
- Automatic updates every 30 seconds
- Links to all vault sections

## Human-in-the-Loop

For sensitive actions, Qwen creates approval request files:

```markdown
---
type: approval_request
action: payment
amount: 500.00
status: pending
---

# Payment Approval Required

Move this file to `/Approved` to proceed.
Move to `/Rejected` to cancel.
```

## Configuration

### Environment Variables (Optional)

Create a `.env` file in `.qwen/skills/`:

```env
# .env - Never commit this file
DRY_RUN=false
LOG_LEVEL=INFO
CHECK_INTERVAL=30
```

### Customizing Check Intervals

| Component | Default | Recommended Range |
|-----------|---------|-------------------|
| File Watcher | 5s | 1-10s |
| Orchestrator | 30s | 15-60s |

## Troubleshooting

### Python Not Found

```bash
# Check Python installation
python --version

# Should show Python 3.13+
```

### Watchdog Not Installed

The file watcher falls back to polling mode if watchdog is not installed:

```bash
pip install watchdog
```

### Permission Errors

Ensure the vault folder has read/write permissions:

```bash
# Windows (run as Administrator)
icacls AI_Employee_Vault /grant Users:F /T
```

### Qwen Not Processing Tasks

1. Check Qwen Code is loaded with skills
2. Verify vault path is correct
3. Check Logs/ folder for error messages

## Security Notes

1. **Never commit credentials** - Add `.env` to `.gitignore`
2. **Use dry-run mode** during development
3. **Review logs regularly** in the `Logs/` folder
4. **Start with low autonomy** - require approval for most actions

## Comparison: Claude Code vs Qwen

| Feature | Claude Code | Qwen |
|---------|-------------|------|
| Cost | Paid ($20/month) | **Free** |
| Skills | Agent Skills | Qwen Skills |
| Local Execution | Yes | Yes |
| Obsidian Integration | Yes | Yes |

## Next Steps (Silver Tier)

To extend this Bronze implementation:

1. Add Gmail Watcher for email monitoring
2. Add WhatsApp Watcher using Playwright
3. Implement MCP servers for external actions
4. Add scheduled tasks (cron/Task Scheduler)
5. Create Plan.md files for multi-step tasks

## Demo Video

Record a 5-10 minute demo showing:

1. Dropping a file into the drop folder
2. Action file creation in Needs_Action
3. Orchestrator triggering Qwen
4. Task completion and movement to Done
5. Dashboard updates

## Submission Checklist

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System)
- [x] Qwen Skills integration (orchestrator)
- [x] Basic folder structure (/Inbox, /Needs_Action, /Done)
- [x] Python scripts in Qwen skills folders
- [ ] Demo video
- [ ] Submit form: https://forms.gle/JR9T1SJq5rmQyGkGA

## License

This project is part of the Panaversity Hackathon 0 challenge.

## Resources

- [Full Blueprint Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://qwen.ai/)
- [Obsidian Help](https://help.obsidian.md/)
- [Panaversity Wednesday Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)

---

*Built for Panaversity Hackathon 0 - Bronze Tier - Using Qwen (Free)*
## AI Tools Used
- Qwen for reasoning and task processing
