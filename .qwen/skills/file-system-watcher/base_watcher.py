"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
Watchers monitor external sources and create actionable .md files in the Needs_Action folder.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers.
    
    Watchers run continuously, monitoring their respective sources
    and creating action files when new items are detected.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    def _setup_logging(self) -> None:
        """Configure logging for this watcher."""
        log_file = self.logs / f'{self.__class__.__name__}_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items from the monitored source.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in the Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if creation failed
        """
        pass
    
    def _is_new_item(self, item_id: str) -> bool:
        """Check if an item has already been processed."""
        return item_id not in self.processed_ids
    
    def _mark_processed(self, item_id: str) -> None:
        """Mark an item as processed."""
        self.processed_ids.add(item_id)
    
    def _generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a standardized filename.
        
        Args:
            prefix: File type prefix (e.g., 'EMAIL', 'WHATSAPP')
            unique_id: Unique identifier for the item
            
        Returns:
            Formatted filename with date
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"{prefix}_{unique_id}_{date_str}.md"
    
    def _create_metadata_file(self, action_path: Path, metadata: dict) -> Path:
        """
        Create a companion metadata file.
        
        Args:
            action_path: Path to the action file
            metadata: Dictionary of metadata
            
        Returns:
            Path to the metadata file
        """
        meta_path = action_path.with_suffix('.meta.json')
        import json
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        return meta_path
    
    def run(self) -> None:
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    self.logger.debug(f'Found {len(items)} new items')
                    
                    for item in items:
                        try:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created action file: {filepath.name}')
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                    
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
