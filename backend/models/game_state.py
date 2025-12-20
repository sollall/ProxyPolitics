"""
ゲーム状態を管理するモデル
"""
from typing import Dict, Optional
import json


class GameState:
    """ゲーム全体の状態を管理"""

    def __init__(self):
        self.turn = 1
        self.resources = {
            "gold": 1000,
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

        # イベントログ
        self.event_log = []

    def add_event(self, message: str):
        """イベントログに追加"""
        self.event_log.append(f"Turn {self.turn}: {message}")
        if len(self.event_log) > 50:  # 最新50件のみ保持
            self.event_log.pop(0)

    def delegate_sector(self, sector: str, npc_id: Optional[str]):
        """分野にNPCを委任（または解除）"""
        if sector in self.sectors:
            self.sectors[sector]["delegated_to"] = npc_id
            if npc_id:
                self.add_event(f"{sector}分野を{npc_id}に委任しました")
            else:
                self.add_event(f"{sector}分野の委任を解除しました")
            return True
        return False

    def advance_turn(self):
        """ターンを進める"""
        self.turn += 1
        self.add_event(f"=== ターン {self.turn} 開始 ===")

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "turn": self.turn,
            "resources": self.resources,
            "sectors": self.sectors,
            "event_log": self.event_log[-10:]  # 最新10件のみ送信
        }
