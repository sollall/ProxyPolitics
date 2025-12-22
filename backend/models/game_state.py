"""
ゲーム状態を管理するモデル（帝国レベル）
"""
from typing import Dict, Optional, List
import json
from models.city import City


class GameState:
    """ゲーム全体の状態を管理（帝国レベル）"""

    def __init__(self):
        self.turn = 1

        # 帝国レベルのリソース（全都市で共有）
        self.empire_resources = {
            "gold": 1000,  # 資金は帝国全体で共有
        }

        # 都市リスト
        self.cities: Dict[str, City] = {}
        self._city_counter = 0

        # デフォルトで首都を作成
        self._create_default_city()

        # 現在選択されている都市ID
        self.current_city_id = "city_001"

        # イベントログ
        self.event_log = []

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

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "turn": self.turn,
            "empire_resources": self.empire_resources,
            "current_city_id": self.current_city_id,
            "cities": {city_id: city.to_dict() for city_id, city in self.cities.items()},
            "event_log": self.event_log[-10:]  # 最新10件のみ送信
        }

    # 後方互換性のためのプロパティ（既存のコードが動作するように）
    @property
    def resources(self) -> Dict:
        """現在の都市のリソース + 帝国リソース（後方互換性）"""
        current_city = self.get_current_city()
        if current_city:
            combined = dict(self.empire_resources)
            combined.update(current_city.resources)
            return combined
        return self.empire_resources

    @property
    def sectors(self) -> Dict:
        """現在の都市の分野（後方互換性）"""
        current_city = self.get_current_city()
        return current_city.sectors if current_city else {}

