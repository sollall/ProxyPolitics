"""
都市モデル
"""
from typing import Dict, Optional


class City:
    """個別の都市を表すクラス"""

    def __init__(self, city_id: str, name: str):
        self.id = city_id
        self.name = name

        # 都市ごとのリソース
        self.resources = {
            "population": 10000,
            "military_power": 500,
            "diplomatic_influence": 50
        }

        # 各分野の状態
        self.sectors = {
            "economy": {
                "level": 1,
                "progress": 0,
                "delegated_to": None  # NPC ID or None
            },
            "diplomacy": {
                "level": 1,
                "progress": 0,
                "delegated_to": None
            },
            "military": {
                "level": 1,
                "progress": 0,
                "delegated_to": None
            }
        }

    def delegate_sector(self, sector: str, npc_id: Optional[str]) -> bool:
        """分野にNPCを委任（または解除）"""
        if sector in self.sectors:
            self.sectors[sector]["delegated_to"] = npc_id
            return True
        return False

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "resources": self.resources,
            "sectors": self.sectors
        }
