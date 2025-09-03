"""Game save/load functionality"""

import pickle
import time
from pathlib import Path
from typing import Optional, Dict, Any
from .game_state import GameState

class SaveManager:
    def __init__(self):
        """Initialize save manager with data directories"""
        self.data_dir = Path("data/saves")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.default_save_file = self.data_dir / "database.pkl"
    
    def save_game(self, game_state: GameState, ai_settings: Optional[Dict] = None, 
                  filename: Optional[str] = None) -> bool:
        """Save game state with metadata"""
        try:
            save_path = self.data_dir / filename if filename else self.default_save_file
            
            save_data = {
                'game_state': game_state,
                'timestamp': time.time(),
                'version': '1.0',
                'ai_settings': ai_settings or {}
            }
            
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, filename: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load game state and metadata"""
        try:
            load_path = self.data_dir / filename if filename else self.default_save_file
            
            if not load_path.exists():
                print("Save file not found")
                return None
            
            with open(load_path, 'rb') as f:
                save_data = pickle.load(f)
                
            # Handle different save formats
            if isinstance(save_data, dict):
                return save_data
            else:
                # Old format - direct GameState object
                return {'game_state': save_data, 'ai_settings': {}}
                
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def list_saves(self) -> list[str]:
        """List all available save files"""
        return [f.name for f in self.data_dir.glob("*.pkl")]
    
    def delete_save(self, filename: str) -> bool:
        """Delete a save file"""
        try:
            save_path = self.data_dir / filename
            if save_path.exists():
                save_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False