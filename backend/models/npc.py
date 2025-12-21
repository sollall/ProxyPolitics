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
        self.npc_counter = 5  # デフォルトNPCが5人いるので6から開始
        self._initialize_default_npcs()

        # NPC生成用の名前リスト
        self.first_names = [
            "山田", "中村", "小林", "加藤", "吉田", "山本", "佐々木", "渡辺",
            "松本", "井上", "木村", "林", "清水", "山崎", "森", "阿部",
            "池田", "橋本", "山下", "石川", "中島", "前田", "藤田", "後藤"
        ]
        self.last_names_economy = ["商人", "財務官", "銀行家", "商会長", "貿易商", "会計士", "豪商"]
        self.last_names_diplomacy = ["外交官", "使節", "交渉官", "大使", "参事官", "書記官", "顧問"]
        self.last_names_military = ["将軍", "参謀", "司令官", "隊長", "武官", "戦術家", "指揮官"]

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

    def generate_random_npc(self, specialty: str = None) -> NPC:
        """
        ランダムなNPCを生成

        Args:
            specialty: 専門分野を指定（Noneの場合はランダム）

        Returns:
            生成されたNPC
        """
        self.npc_counter += 1
        npc_id = f"npc_{self.npc_counter:03d}"

        # 専門分野を決定
        if specialty is None:
            specialty = random.choice(["economy", "diplomacy", "military"])

        # 名前を生成
        first_name = random.choice(self.first_names)
        if specialty == "economy":
            last_name = random.choice(self.last_names_economy)
        elif specialty == "diplomacy":
            last_name = random.choice(self.last_names_diplomacy)
        else:  # military
            last_name = random.choice(self.last_names_military)

        name = f"{first_name}{last_name}"

        # 性格を生成（3つの性格タイプからランダムに主要性格を決定）
        personality_type = random.choice(["aggressive", "cautious", "balanced"])

        if personality_type == "aggressive":
            personality = {
                "aggressive": random.randint(7, 10),
                "cautious": random.randint(1, 4),
                "balanced": random.randint(3, 6)
            }
        elif personality_type == "cautious":
            personality = {
                "aggressive": random.randint(1, 4),
                "cautious": random.randint(7, 10),
                "balanced": random.randint(3, 6)
            }
        else:  # balanced
            personality = {
                "aggressive": random.randint(3, 6),
                "cautious": random.randint(3, 6),
                "balanced": random.randint(7, 10)
            }

        return NPC(npc_id, name, specialty, personality)

    def recruit_npc(self, specialty: str = None) -> NPC:
        """
        新しいNPCを採用してプールに追加

        Args:
            specialty: 専門分野を指定（Noneの場合はランダム）

        Returns:
            採用されたNPC
        """
        new_npc = self.generate_random_npc(specialty)
        self.npcs[new_npc.id] = new_npc
        return new_npc

    def get_npc_count(self) -> int:
        """現在のNPC数を取得"""
        return len(self.npcs)
