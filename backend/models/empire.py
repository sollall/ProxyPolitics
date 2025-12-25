"""
帝国モデル - 帝国全体の状態を管理
"""
from typing import Dict, Optional, List
from models.city import City
from models.npc import NPCManager


class Empire:
    """帝国全体を管理するクラス"""

    def __init__(self):
        # ターンカウンター
        self.turn = 1

        # 帝国レベルのリソース（全都市で共有）
        self.resources = {
            "gold": 1000,  # 資金は帝国全体で共有
        }

        # 政治体制（0-100のスライダー値）
        self.ideology = {
            "capital": 50,      # 資本：0=集産、100=市場
            "power": 50,        # 権力：0=集権、100=分散
            "legitimacy": 50,   # 正統性：0=カリスマ、100=超越的
            "integration": 50   # 統合：0=国粋、100=多元
        }

        # 都市管理
        self.cities: Dict[str, City] = {}
        self._city_counter = 0
        self.current_city_id = "city_001"

        # NPC管理
        self.npc_manager = NPCManager()

        # イベントログ
        self.event_log = []

        # デフォルトで首都を作成
        self._create_default_city()

    def _create_default_city(self):
        """デフォルトの首都を作成"""
        capital = City("city_001", "首都")
        self.cities["city_001"] = capital
        self._city_counter = 1

    def add_city(self, name: str) -> City:
        """新しい都市を追加"""
        self._city_counter += 1
        city_id = f"city_{self._city_counter:03d}"
        new_city = City(city_id, name)
        self.cities[city_id] = new_city
        self.add_event(f"新しい都市「{name}」を獲得しました")
        return new_city

    def get_city(self, city_id: str) -> Optional[City]:
        """都市を取得"""
        return self.cities.get(city_id)

    def get_current_city(self) -> Optional[City]:
        """現在選択されている都市を取得"""
        return self.cities.get(self.current_city_id)

    def set_current_city(self, city_id: str) -> bool:
        """現在の都市を切り替え"""
        if city_id in self.cities:
            self.current_city_id = city_id
            return True
        return False

    def add_event(self, message: str):
        """イベントログに追加"""
        self.event_log.append(f"Turn {self.turn}: {message}")
        if len(self.event_log) > 50:  # 最新50件のみ保持
            self.event_log.pop(0)

    def delegate_sector(self, city_id: str, sector: str, npc_id: Optional[str]) -> bool:
        """指定都市の分野にNPCを委任（または解除）"""
        city = self.get_city(city_id)
        if city and city.delegate_sector(sector, npc_id):
            if npc_id:
                self.add_event(f"[{city.name}] {sector}分野を{npc_id}に委任しました")
            else:
                self.add_event(f"[{city.name}] {sector}分野の委任を解除しました")
            return True
        return False

    def advance_turn(self):
        """ターンを進める"""
        self.turn += 1
        self.add_event(f"=== ターン {self.turn} 開始 ===")

    def update_ideology(self, axis: str, value: int) -> bool:
        """政治体制を更新"""
        if axis in self.ideology and 0 <= value <= 100:
            self.ideology[axis] = value
            return True
        return False

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "turn": self.turn,
            "resources": self.resources,  # 帝国レベルのリソース
            "ideology": self.ideology,    # 政治体制
            "current_city_id": self.current_city_id,
            "cities": {city_id: city.to_dict() for city_id, city in self.cities.items()},
            "event_log": self.event_log[-10:]  # 最新10件のみ送信
        }
