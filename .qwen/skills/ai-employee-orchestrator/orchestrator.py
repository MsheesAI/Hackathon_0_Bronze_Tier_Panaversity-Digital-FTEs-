"""
Orchestrator Module

Main orchestration script for the AI Employee system.
Monitors folders, triggers Claude Code for processing, and manages task flow.

Usage:
    python orchestrator.py /path/to/vault [--dry-run] [--interval SECONDS]
"""

import os
import sys
import json
import shutil
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Responsibilities:
    - Monitor Needs_Action folder for new tasks
    - Trigger Claude Code to process tasks
    - Move completed tasks to Done folder
    - Update Dashboard.md with current status
    - Log all activities
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30, dry_run: bool = False):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30)
            dry_run: If True, log actions without executing (default: False)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.dry_run = dry_run
        
        # Define folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.approved = self.vault_path / 'Approved'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.accounting = self.vault_path / 'Accounting'
        self.briefings = self.vault_path / 'Briefings'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        self._ensure_folders()
        
        # Setup logging
        self._setup_logging()
        
        # Track processed files
        self.processed_files: set = set()
        
        self.logger.info(f'Orchestrator initialized (dry_run={dry_run})')
        self.logger.info(f'Vault path: {self.vault_path}')
    
    def _ensure_folders(self) -> None:
        """Ensure all required folders exist."""
        folders = [
            self.inbox, self.needs_action, self.plans, self.approved,
            self.pending_approval, self.rejected, self.done, self.logs,
            self.accounting, self.briefings
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self) -> None:
        """Configure logging."""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
    
    def _log_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """
        Log an action to the daily log file.
        
        Args:
            action_type: Type of action (e.g., 'task_processed', 'file_moved')
            details: Dictionary of action details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            **details
        }
        
        log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        
        # Append to existing log or create new
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, IOError):
                logs = []
        
        logs.append(log_entry)
        
        if not self.dry_run:
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        
        self.logger.info(f"Action logged: {action_type}")
    
    def count_files(self, folder: Path) -> int:
        """Count .md files in a folder."""
        if not folder.exists():
            return 0
        return len([f for f in folder.iterdir() if f.suffix == '.md'])
    
    def update_dashboard(self) -> None:
        """Update the Dashboard.md with current status."""
        if not self.dashboard.exists():
            self.logger.warning('Dashboard.md not found')
            return

        # Count items in each folder
        pending_count = self.count_files(self.needs_action)
        approval_count = self.count_files(self.pending_approval)
        done_today = self.count_files(self.done)

        # Read current dashboard
        content = self.dashboard.read_text(encoding='utf-8')

        # Update timestamp
        content = content.replace(
            'last_updated: ', 
            f'last_updated: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}'
        )

        # Update Quick Status table - line by line replacement
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip().startswith('| Pending Tasks |'):
                new_lines.append(f'| Pending Tasks | {pending_count} |')
            elif line.strip().startswith('| Awaiting Approval |'):
                new_lines.append(f'| Awaiting Approval | {approval_count} |')
            elif line.strip().startswith('| Completed Today |'):
                new_lines.append(f'| Completed Today | {done_today} |')
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
        
        # Update Inbox Summary section
        inbox_items = list(self.inbox.glob('*.md'))
        if inbox_items:
            inbox_summary = '\n'.join([f'- [[{item.stem}]]' for item in inbox_items[:10]])
        else:
            inbox_summary = '*No new items*'
        
        content = re.sub(
            r'## 📥 Inbox Summary\n\n.*?\n\n---',
            f'## 📥 Inbox Summary\n\n{inbox_summary}\n\n---',
            content,
            flags=re.DOTALL
        )
        
        # Update Pending Actions section
        pending_items = list(self.needs_action.glob('*.md'))
        if pending_items:
            pending_summary = '\n'.join([f'- [[{item.stem}]]' for item in pending_items[:10]])
        else:
            pending_summary = '*No pending actions*'
        
        content = re.sub(
            r'## ⏳ Pending Actions\n\n.*?\n\n---',
            f'## ⏳ Pending Actions\n\n{pending_summary}\n\n---',
            content,
            flags=re.DOTALL
        )
        
        # Update Awaiting Approval section
        approval_items = list(self.pending_approval.glob('*.md'))
        if approval_items:
            approval_summary = '\n'.join([f'- [[{item.stem}]]' for item in approval_items[:10]])
        else:
            approval_summary = '*No items awaiting approval*'
        
        content = re.sub(
            r'## 🕐 Awaiting Your Approval\n\n.*?\n\n---',
            f'## 🕐 Awaiting Your Approval\n\n{approval_summary}\n\n---',
            content,
            flags=re.DOTALL
        )
        
        # Write updated dashboard
        if not self.dry_run:
            self.dashboard.write_text(content, encoding='utf-8')
        
        self.logger.info('Dashboard updated')
    
    def get_pending_tasks(self) -> List[Path]:
        """Get list of pending task files."""
        tasks = []
        for f in self.needs_action.glob('*.md'):
            if f.name not in self.processed_files:
                tasks.append(f)
        return tasks
    
    def trigger_claude(self, task_file: Path) -> bool:
        """
        Trigger Claude Code to process a task.
        
        Args:
            task_file: Path to the task file to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        self.logger.info(f'Triggering Claude Code for: {task_file.name}')
        
        # Create a prompt for Claude
        prompt = f"""Please process the task file: {task_file.name}

1. Read the task file from Needs_Action folder
2. Analyze what needs to be done
3. Create a plan if this is a multi-step task
4. Execute the required actions
5. Move the task to Done folder when complete

For sensitive actions (payments, new contacts, etc.), create an approval request in Pending_Approval folder instead of executing directly.

Refer to Company_Handbook.md for rules and guidelines."""

        if self.dry_run:
            self.logger.info(f'[DRY RUN] Would trigger Claude with prompt: {prompt[:100]}...')
            return True
        
        try:
            # Check if claude command is available
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.warning('Claude Code not available, skipping processing')
                return False
            
            # Trigger Claude Code
            # Note: In a real implementation, you would use claude-code-router or direct API
            # For now, we log that Claude would be triggered
            self.logger.info('Claude Code triggered (simulated)')
            
            self._log_action('claude_triggered', {
                'task_file': str(task_file),
                'prompt_length': len(prompt)
            })
            
            return True
            
        except FileNotFoundError:
            self.logger.warning('Claude Code command not found. Install with: npm install -g @anthropic/claude-code')
            return False
        except subprocess.TimeoutExpired:
            self.logger.error('Claude Code version check timed out')
            return False
        except Exception as e:
            self.logger.error(f'Error triggering Claude Code: {e}')
            return False
    
    def process_approved_tasks(self) -> None:
        """Process tasks that have been approved by human."""
        approved_files = list(self.approved.glob('*.md'))
        
        for approved_file in approved_files:
            self.logger.info(f'Processing approved task: {approved_file.name}')
            
            # Read the approval file to determine action
            content = approved_file.read_text(encoding='utf-8')
            
            # Extract action type from frontmatter
            action_type = 'unknown'
            if 'action: ' in content:
                for line in content.split('\n'):
                    if line.startswith('action:'):
                        action_type = line.split(':')[1].strip()
                        break
            
            self.logger.info(f'Approved action type: {action_type}')
            
            # In a full implementation, execute the approved action via MCP
            # For Bronze tier, we just move to Done and log
            if not self.dry_run:
                # Move to Done
                dest = self.done / approved_file.name
                shutil.move(str(approved_file), str(dest))
                
                self._log_action('approved_task_completed', {
                    'file': str(approved_file),
                    'action_type': action_type,
                    'destination': str(dest)
                })
            
            self.logger.info(f'Moved approved task to Done: {approved_file.name}')
    
    def check_completion(self) -> None:
        """Check for tasks that Claude has completed (marked with completion indicator)."""
        for task_file in self.needs_action.glob('*.md'):
            content = task_file.read_text(encoding='utf-8')
            
            # Check for completion markers
            if '[x]' in content or 'TASK_COMPLETE' in content or 'completed' in content.lower():
                # Verify all checkboxes are checked
                lines = content.split('\n')
                checkboxes = [l for l in lines if '- [' in l and ']' in l]
                
                if checkboxes:
                    unchecked = [l for l in checkboxes if '- [ ]' in l]
                    if not unchecked:
                        # All tasks complete
                        self.logger.info(f'Task complete: {task_file.name}')
                        
                        if not self.dry_run:
                            dest = self.done / task_file.name
                            shutil.move(str(task_file), str(dest))
                            self.processed_files.add(task_file.name)
                            
                            self._log_action('task_completed', {
                                'file': str(task_file),
                                'destination': str(dest)
                            })
    
    def run_cycle(self) -> None:
        """Run one complete processing cycle."""
        self.logger.info('Starting processing cycle')
        
        # Update dashboard
        self.update_dashboard()
        
        # Check for completed tasks
        self.check_completion()
        
        # Process approved tasks
        self.process_approved_tasks()
        
        # Get pending tasks
        pending_tasks = self.get_pending_tasks()
        
        if pending_tasks:
            self.logger.info(f'Found {len(pending_tasks)} pending tasks')
            
            for task in pending_tasks:
                self.trigger_claude(task)
                self.processed_files.add(task.name)
        else:
            self.logger.debug('No pending tasks')
        
        # Final dashboard update
        self.update_dashboard()
        
        self.logger.info('Processing cycle complete')
    
    def run(self) -> None:
        """Main run loop."""
        self.logger.info(f'Starting Orchestrator (check_interval={self.check_interval}s)')
        
        try:
            while True:
                self.run_cycle()
                
                import time
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise


def main():
    """Entry point for the orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=30, 
                        help='Check interval in seconds (default: 30)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='Log actions without executing')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    orchestrator = Orchestrator(
        str(vault_path),
        check_interval=args.interval,
        dry_run=args.dry_run
    )
    
    orchestrator.run()


if __name__ == '__main__':
    main()
