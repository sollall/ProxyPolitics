"""
NPCキャラクターのモデル
"""
from typing import Dict, List
import random


class NPC:
    """NPCキャラクター"""

    def __init__(self, npc_id: str, name: str, specialty: str,
                 personality: Dict[str, int]):
        self.id = npc_id
        self.name = name
        self.specialty = specialty  # "economy", "diplomacy", "military"
        self.personality = personality  # {"aggressive": 0-10, "cautious": 0-10, "balanced": 0-10}
        self.loyalty = 100
        self.experience = 0

    def get_decision_bias(self) -> str:
        """性格に基づいた意思決定の傾向を返す"""
        max_trait = max(self.personality.items(), key=lambda x: x[1])
        return max_trait[0]

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty,
            "personality": self.personality,
            "loyalty": self.loyalty,
            "experience": self.experience
        }


class NPCManager:
    """NPC管理クラス"""

    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self._initialize_default_npcs()

    def _initialize_default_npcs(self):
        """デフォルトのNPCを初期化"""
        default_npcs = [
            NPC("npc_001", "田中商人", "economy",
                {"aggressive": 3, "cautious": 7, "balanced": 5}),
            NPC("npc_002", "佐藤将軍", "military",
                {"aggressive": 8, "cautious": 2, "balanced": 4}),
            NPC("npc_003", "鈴木外交官", "diplomacy",
                {"aggressive": 4, "cautious": 6, "balanced": 7}),
            NPC("npc_004", "高橋総督", "economy",
                {"aggressive": 6, "cautious": 3, "balanced": 8}),
            NPC("npc_005", "伊藤参謀", "military",
                {"aggressive": 5, "cautious": 8, "balanced": 6}),
        ]

        for npc in default_npcs:
            self.npcs[npc.id] = npc

    def get_npc(self, npc_id: str) -> NPC:
        """NPCを取得"""
        return self.npcs.get(npc_id)

    def get_all_npcs(self) -> List[Dict]:
        """全NPCを辞書形式のリストで取得"""
        return [npc.to_dict() for npc in self.npcs.values()]

    def get_npcs_by_specialty(self, specialty: str) -> List[Dict]:
        """専門分野でフィルタリングしたNPCリストを取得"""
        return [npc.to_dict() for npc in self.npcs.values()
                if npc.specialty == specialty]
