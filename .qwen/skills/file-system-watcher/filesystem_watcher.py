"""
File System Watcher Module

Monitors a drop folder for new files and creates action files in the Needs_Action folder.
This is the Bronze Tier watcher - simple, reliable, and doesn't require API credentials.

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/drop_folder
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from base_watcher import BaseWatcher

# Try to import watchdog, fall back to polling if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Using polling mode instead.")
    print("Install with: pip install watchdog")


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events for the drop folder."""
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        self.logger.info(f'File created: {event.src_path}')
        self.watcher.process_file(Path(event.src_path))


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files and creates action files.
    
    Supports two modes:
    1. Event-driven (watchdog) - real-time file monitoring
    2. Polling - periodic folder scanning (fallback)
    """
    
    def __init__(self, vault_path: str, drop_folder: str, check_interval: int = 5):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the folder to monitor for new files
            check_interval: Seconds between checks (default: 5 for responsive UI)
        """
        super().__init__(vault_path, check_interval)
        
        self.drop_folder = Path(drop_folder)
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash
        self.processed_files: Dict[str, str] = {}  # hash -> filename
        
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]  # Use first 16 chars for filename
    
    def _get_file_size_formatted(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in the drop folder (polling mode).
        
        Returns:
            List of new file paths to process
        """
        new_files = []
        
        try:
            for file_path in self.drop_folder.iterdir():
                if file_path.is_file() and file_path.suffix != '.md':
                    file_hash = self._calculate_file_hash(file_path)
                    
                    if file_hash not in self.processed_files:
                        self.logger.info(f'New file detected: {file_path.name}')
                        new_files.append(file_path)
        except Exception as e:
            self.logger.error(f'Error scanning drop folder: {e}')
        
        return new_files
    
    def process_file(self, file_path: Path) -> Optional[Path]:
        """
        Process a single file and create an action file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Path to the created action file, or None if failed
        """
        try:
            # Calculate hash and mark as processed
            file_hash = self._calculate_file_hash(file_path)
            self.processed_files[file_hash] = file_path.name
            
            # Get file metadata
            stat = file_path.stat()
            file_size = stat.st_size
            created_time = datetime.fromtimestamp(stat.st_ctime)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Generate action file content
            content = f'''---
type: file_drop
original_name: {file_path.name}
size: {file_size}
size_formatted: {self._get_file_size_formatted(file_size)}
detected: {datetime.now().isoformat()}
created: {created_time.isoformat()}
modified: {modified_time.isoformat()}
file_hash: {file_hash}
status: pending
---

# File Drop for Processing

## Original File
- **Name:** {file_path.name}
- **Size:** {self._get_file_size_formatted(file_size)}
- **Detected:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## File Location
- **Drop Folder:** `{self.drop_folder}`
- **Action File:** `{self.needs_action}`

## Suggested Actions
- [ ] Review file contents
- [ ] Categorize file type
- [ ] Process or forward as needed
- [ ] Move original to appropriate location
- [ ] Mark this task as done

## Notes
*Add your notes here*

---
*Generated by FileSystemWatcher v0.1*
'''
            
            # Generate filename
            safe_name = file_path.stem.replace(' ', '_').replace('.', '_')
            filename = self._generate_filename('FILE', f'{safe_name}_{file_hash}')
            action_path = self.needs_action / filename
            
            # Write action file
            action_path.write_text(content, encoding='utf-8')
            
            self.logger.info(f'Created action file: {action_path.name}')
            
            return action_path
            
        except Exception as e:
            self.logger.error(f'Error processing file {file_path.name}: {e}')
            return None
    
    def create_action_file(self, item: Path) -> Optional[Path]:
        """
        Create an action file for a detected file.
        
        Args:
            item: Path to the file to process
            
        Returns:
            Path to the created action file
        """
        return self.process_file(item)
    
    def run_event_driven(self) -> None:
        """Run in event-driven mode using watchdog."""
        if not WATCHDOG_AVAILABLE:
            self.logger.warning('Watchdog not available, falling back to polling')
            self.run()
            return
        
        self.logger.info(f'Starting FileSystemWatcher (event-driven mode)')
        self.logger.info(f'Drop folder: {self.drop_folder}')
        
        event_handler = DropFolderHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        self.logger.info('Watching for file changes...')
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info('Watcher stopped by user')
        observer.join()
    
    def run(self, use_watchdog: bool = True) -> None:
        """
        Main run loop for the watcher.
        
        Args:
            use_watchdog: If True and available, use event-driven mode
        """
        if use_watchdog and WATCHDOG_AVAILABLE:
            self.run_event_driven()
        else:
            # Fall back to polling mode from parent class
            super().run()


def main():
    """Entry point for running the file system watcher."""
    if len(sys.argv) < 3:
        print("Usage: python filesystem_watcher.py <vault_path> <drop_folder> [check_interval]")
        print("\nExample:")
        print("  python filesystem_watcher.py ./AI_Employee_Vault ./Drop_Folder")
        print("  python filesystem_watcher.py ./AI_Employee_Vault ./Drop_Folder 10")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    drop_folder = sys.argv[2]
    check_interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    # Validate paths
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    watcher = FileSystemWatcher(vault_path, drop_folder, check_interval)
    
    # Use polling mode by default (more reliable across platforms)
    watcher.run(use_watchdog=False)


if __name__ == '__main__':
    main()
