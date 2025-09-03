# core/save_manager.py - Game Persistence

## Purpose
The SaveManager class handles all game state persistence operations, including saving games to disk and loading them back. It provides a clean interface for game state serialization using Python's pickle module, with proper error handling and metadata management.

## Key Responsibilities
- Serialize complex game states to persistent storage
- Load and deserialize saved games with backwards compatibility
- Manage save file directories and organization
- Handle save/load errors gracefully
- Provide file listing and management capabilities

## Class Structure

### Instance Variables

#### Directory Management
- `data_dir`: Path object pointing to save directory (`"data/saves"`)
- `default_save_file`: Path object for default save file (`data_dir / "database.pkl"`)

**Why these paths?**
- Separates save data from application code
- Creates dedicated saves subdirectory for