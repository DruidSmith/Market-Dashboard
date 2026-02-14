"""
Storage abstraction for market data.
Handles reading/writing JSON files for each symbol.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DataStorage:
    """Manages reading and writing market data to JSON files."""
    
    def __init__(self, data_dir: str = "data/raw", metadata_dir: str = "data/metadata"):
        self.data_dir = Path(data_dir)
        self.metadata_dir = Path(metadata_dir)
        self.metadata_file = self.metadata_dir / "update_status.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata file if it doesn't exist
        if not self.metadata_file.exists():
            self._write_json(self.metadata_file, {})
    
    def get_symbol_file_path(self, symbol: str) -> Path:
        """Get the file path for a symbol's data."""
        # Replace special characters in symbol (e.g., BTC-USD -> BTC_USD)
        safe_symbol = symbol.replace("-", "_").replace("^", "")
        return self.data_dir / f"{safe_symbol}.json"
    
    def load_symbol_data(self, symbol: str) -> Optional[Dict]:
        """Load existing data for a symbol."""
        file_path = self.get_symbol_file_path(symbol)
        if not file_path.exists():
            return None
        return self._read_json(file_path)
    
    def save_symbol_data(self, symbol: str, symbol_type: str, category: str, 
                        api_source: str, data: List[Dict]) -> None:
        """Save or update data for a symbol."""
        file_path = self.get_symbol_file_path(symbol)
        
        # Load existing data or create new structure
        existing = self.load_symbol_data(symbol)
        
        if existing:
            # Merge new data with existing (avoid duplicates by date)
            existing_dates = {item['date'] for item in existing.get('data', [])}
            new_data_points = [d for d in data if d['date'] not in existing_dates]
            combined_data = existing.get('data', []) + new_data_points
            # Sort by date descending (newest first)
            combined_data.sort(key=lambda x: x['date'], reverse=True)
        else:
            combined_data = sorted(data, key=lambda x: x['date'], reverse=True)
        
        # Create the full structure
        full_data = {
            "symbol": symbol,
            "type": symbol_type,
            "category": category,
            "api_source": api_source,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "data": combined_data
        }
        
        # Write to file
        self._write_json(file_path, full_data)
        
        # Update metadata
        self._update_metadata(symbol, "success", len(combined_data))
    
    def _update_metadata(self, symbol: str, status: str, data_points: int) -> None:
        """Update the metadata tracking file."""
        metadata = self._read_json(self.metadata_file)
        
        metadata[symbol] = {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "last_fetch_status": status,
            "data_points": data_points
        }
        
        self._write_json(self.metadata_file, metadata)
    
    def get_metadata(self) -> Dict:
        """Get all metadata about symbol updates."""
        return self._read_json(self.metadata_file)
    
    def mark_symbol_failed(self, symbol: str, error: str) -> None:
        """Mark a symbol fetch as failed in metadata."""
        metadata = self._read_json(self.metadata_file)
        
        metadata[symbol] = {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "last_fetch_status": f"failed: {error}",
            "data_points": 0
        }
        
        self._write_json(self.metadata_file, metadata)
    
    @staticmethod
    def _read_json(file_path: Path) -> Dict:
        """Read JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def _write_json(file_path: Path, data: Dict) -> None:
        """Write JSON file with nice formatting."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)