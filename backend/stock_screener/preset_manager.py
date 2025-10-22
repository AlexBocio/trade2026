# preset_manager.py - Scan Preset Management
# Save, load, update, delete scan configurations

import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PresetManager:
    """
    Manage scan presets (in-memory storage).

    In production, replace with database storage.
    """

    def __init__(self):
        self.presets = {}
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Initialize with default presets."""
        default_presets = [
            {
                'id': 'preset_default_001',
                'name': 'Momentum Breakout',
                'description': 'Strong momentum with volume confirmation',
                'config': {
                    'universe': 'sp500',
                    'strategy': 'swing',
                    'top_n': 25,
                    'filters': {
                        'min_momentum_20d': 0.15,
                        'min_volume_surge': 2.0,
                        'min_rsi': 50,
                        'max_rsi': 70
                    }
                },
                'is_default': True,
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat()
            },
            {
                'id': 'preset_default_002',
                'name': 'Oversold Value',
                'description': 'Oversold stocks with good fundamentals',
                'config': {
                    'universe': 'sp500',
                    'strategy': 'position',
                    'top_n': 30,
                    'filters': {
                        'max_rsi': 30
                    }
                },
                'is_default': True,
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat()
            },
            {
                'id': 'preset_default_003',
                'name': 'Day Trading Setup',
                'description': 'High volume, volatile stocks for intraday',
                'config': {
                    'universe': 'sp500',
                    'strategy': 'intraday',
                    'top_n': 15,
                    'filters': {
                        'min_liquidity': 100
                    }
                },
                'is_default': True,
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat()
            }
        ]

        for preset in default_presets:
            self.presets[preset['id']] = preset

        logger.info(f"Initialized {len(default_presets)} default presets")

    def get_all_presets(self) -> List[Dict]:
        """Get all presets."""
        return list(self.presets.values())

    def get_preset(self, preset_id: str) -> Optional[Dict]:
        """Get specific preset by ID."""
        return self.presets.get(preset_id)

    def create_preset(self, name: str, description: str, config: Dict) -> Dict:
        """
        Create new preset.

        Args:
            name: Preset name
            description: Preset description
            config: Scan configuration

        Returns:
            Created preset
        """
        preset_id = f"preset_{len(self.presets) + 1:03d}"

        preset = {
            'id': preset_id,
            'name': name,
            'description': description,
            'config': config,
            'is_default': False,
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }

        self.presets[preset_id] = preset

        logger.info(f"Created preset: {preset_id} - {name}")

        return preset

    def update_preset(self, preset_id: str, name: str = None, description: str = None, config: Dict = None) -> Optional[Dict]:
        """
        Update existing preset.

        Args:
            preset_id: Preset ID
            name: New name (optional)
            description: New description (optional)
            config: New config (optional)

        Returns:
            Updated preset or None if not found
        """
        if preset_id not in self.presets:
            logger.warning(f"Preset not found: {preset_id}")
            return None

        preset = self.presets[preset_id]

        # Don't allow updating default presets
        if preset.get('is_default', False):
            logger.warning(f"Cannot update default preset: {preset_id}")
            return None

        if name:
            preset['name'] = name
        if description is not None:
            preset['description'] = description
        if config:
            preset['config'] = config

        logger.info(f"Updated preset: {preset_id}")

        return preset

    def delete_preset(self, preset_id: str) -> bool:
        """
        Delete preset.

        Args:
            preset_id: Preset ID

        Returns:
            True if deleted, False otherwise
        """
        if preset_id not in self.presets:
            logger.warning(f"Preset not found: {preset_id}")
            return False

        preset = self.presets[preset_id]

        # Don't allow deleting default presets
        if preset.get('is_default', False):
            logger.warning(f"Cannot delete default preset: {preset_id}")
            return False

        del self.presets[preset_id]

        logger.info(f"Deleted preset: {preset_id}")

        return True

    def mark_used(self, preset_id: str):
        """Update last_used timestamp for preset."""
        if preset_id in self.presets:
            self.presets[preset_id]['last_used'] = datetime.now().isoformat()

    def export_presets(self) -> str:
        """Export all presets to JSON."""
        export_data = {
            'presets': list(self.presets.values()),
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        return json.dumps(export_data, indent=2)

    def import_presets(self, json_data: str) -> int:
        """
        Import presets from JSON.

        Args:
            json_data: JSON string

        Returns:
            Number of presets imported
        """
        try:
            data = json.loads(json_data)
            imported = 0

            for preset in data.get('presets', []):
                # Skip if already exists
                if preset['id'] in self.presets:
                    continue

                # Don't import default presets
                if preset.get('is_default', False):
                    continue

                self.presets[preset['id']] = preset
                imported += 1

            logger.info(f"Imported {imported} presets")

            return imported

        except Exception as e:
            logger.error(f"Error importing presets: {e}")
            return 0
