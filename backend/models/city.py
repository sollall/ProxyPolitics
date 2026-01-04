"""
都市モデル
"""
from typing import Dict, Optional


class City:
    """個別の都市を表すクラス"""

    def __init__(self, city_id: str, name: str):
        self.id = city_id
        self.name = name

        # 総督（都市全体を管理するNPC）
        self.governor = None  # NPC ID or None

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

    def set_governor(self, npc_id: Optional[str]) -> bool:
        """総督を設定（または解除）"""
        self.governor = npc_id
        # 総督が設定された場合、すべての分野を総督に委任
        if npc_id:
            for sector in self.sectors:
                self.sectors[sector]["delegated_to"] = npc_id
        # 総督が解除された場合、すべての分野の委任も解除
        else:
            for sector in self.sectors:
                self.sectors[sector]["delegated_to"] = None
        return True

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
            "governor": self.governor,
            "resources": self.resources,
            "sectors": self.sectors
        }
