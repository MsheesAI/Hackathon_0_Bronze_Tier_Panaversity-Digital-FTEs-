---
name: ai-employee-dashboard
description: |
  Manages the AI Employee Dashboard.md - updating status, counting tasks,
  and displaying real-time metrics. Use to view or update the dashboard
  for the AI Employee Bronze Tier system.
---

# AI Employee Dashboard Skill

Manages and updates the Dashboard.md file for real-time status tracking.

## Dashboard Location

```
AI_Employee_Vault/Dashboard.md
```

## Quick Commands

### View Current Status

```bash
# Open in Obsidian
obsidian://open?vault=AI_Employee_Vault&file=Dashboard.md

# Or view in terminal
type AI_Employee_Vault\Dashboard.md
```

### Manual Update

```bash
cd scripts
python -c "from orchestrator import Orchestrator; o = Orchestrator('../AI_Employee_Vault'); o.update_dashboard()"
```

## Dashboard Structure

```markdown
---
last_updated: 2026-03-30T22:52:48
status: active
---

# 🎯 AI Employee Dashboard

## Quick Status
| Metric | Value |
|--------|-------|
| Pending Tasks | 1 |
| Awaiting Approval | 0 |
| Completed Today | 1 |
| Revenue MTD | $0 |

## 📥 Inbox Summary
## ⏳ Pending Actions
## 🕐 Awaiting Your Approval
## ✅ Recent Activity
## 📊 Business Metrics
## 📋 Active Projects
## 🔔 Alerts & Notifications
```

## Status Metrics

| Metric | Source | Updates When |
|--------|--------|--------------|
| Pending Tasks | `Needs_Action/*.md` | New file dropped |
| Awaiting Approval | `Pending_Approval/*.md` | Qwen creates approval request |
| Completed Today | `Done/*.md` | Task finished |
| Revenue MTD | `Accounting/*.md` | Transaction logged |

## How Updates Work

1. **Count files** in each folder
2. **Read** current Dashboard.md
3. **Replace** metric values with counts
4. **Update** timestamp
5. **Write** back to Dashboard.md

## Sections Explained

### Quick Status
Real-time counts of tasks in each state.

### Inbox Summary
Lists files in `Inbox/` folder.

### Pending Actions
Lists files in `Needs_Action/` folder.

### Awaiting Your Approval
Lists files in `Pending_Approval/` folder.

### Recent Activity
Shows recently completed tasks.

### Business Metrics
Revenue tracking and KPIs from `Business_Goals.md`.

### Active Projects
Current projects from `Business_Goals.md`.

### Alerts & Notifications
System alerts and reminders.

## Integration

Used by:
- **Orchestrator** - Updates every 30 seconds
- **Qwen** - Reads for current status
- **Human** - Reviews progress

## Customization

### Add New Metrics

Edit `orchestrator.py` in `update_dashboard()`:

```python
# Add custom count
custom_count = self.count_files(self.custom_folder)

# Add to dashboard content
content = content.replace(
    '| Custom Metric | 0 |',
    f'| Custom Metric | {custom_count} |'
)
```

### Change Update Frequency

```bash
# Default: 30 seconds
python orchestrator.py ../AI_Employee_Vault --interval 10  # Fast
python orchestrator.py ../AI_Employee_Vault --interval 60  # Slow
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Counts show 0 | Check folder paths, verify .md files exist |
| Timestamp not updating | Ensure Dashboard.md is writable |
| Wrong counts | Close Obsidian (may lock files) |
| Formatting broken | Restore Dashboard.md from template |

## Verification

1. Drop a file in `Drop_Folder/`
2. Wait 30 seconds
3. Open `Dashboard.md`
4. Verify "Pending Tasks" increased by 1

## Related Skills

- **file-system-watcher** - Creates tasks that appear on dashboard
- **ai-employee-orchestrator** - Updates dashboard automatically
