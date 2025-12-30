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

        # 政治体制（0～5の6段階スライダー値）
        self.ideology = {
            "capital": 0,        # 市場：0=放任、2-3=中道、5=介入
            "power": 0,          # 権力：0=分散、2-3=中道、5=集権
            "legitimacy": 0,     # 正統性：0=カリスマ、2-3=中道、5=超越的
            "power_subject": 0   # 権力主体：0=個人、2-3=中道、5=議会
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
        if axis in self.ideology and 0 <= value <= 5:
            self.ideology[axis] = value
            return True
        return False

    def classify_regime(self) -> str:
        """イデオロギー値に基づいて政治体制を分類（0～5の6段階）"""
        capital = self.ideology["capital"]
        power = self.ideology["power"]
        legitimacy = self.ideology["legitimacy"]
        power_subject = self.ideology["power_subject"]

        # 神権政治 (transcendent legitimacy が高い: 4以上)
        if legitimacy >= 4:
            if power >= 4:
                return "神権君主制" if power_subject <= 1 else "神聖帝国"
            elif power <= 1:
                return "宗教自治連邦"
            else:
                return "立憲神権制" if power_subject >= 3 else "宗教君主制"

        # カリスマに基づく体制 (charisma が高い: 1以下)
        if legitimacy <= 1:
            if power_subject <= 1:
                # 個人支配が強い
                if power >= 4:
                    return "帝国" if capital <= 2 else "全体主義"
                elif power <= 1:
                    return "封建制"
                else:
                    # 中程度の集権
                    if capital >= 4:
                        return "統制経済"
                    else:
                        return "幕藩体制"
            else:
                # 議会的・集団指導
                if power >= 4:
                    return "全体主義" if capital >= 4 else "カリスマ国家"
                elif power <= 1:
                    return "貴族制"
                else:
                    return "革命評議会"

        # 以下、中庸な正統性の場合
        # 極端な中央集権
        if power == 5:
            if power_subject <= 1:
                return "郡県制" if capital <= 2 else "人民独裁"
            else:
                return "中央集権国家" if capital <= 2 else "中央計画経済"

        # 極端な分権
        if power == 0:
            if capital >= 4:
                return "アナルコ・サンディカリズム"
            elif capital <= 1:
                return "アナルコ・キャピタリズム"
            else:
                if power_subject >= 3:
                    return "連邦制"
                else:
                    return "自治都市連合"

        # 中庸な権力分散度
        if capital >= 4:
            # 集産主義
            if power_subject <= 1:
                return "社会主義独裁"
            else:
                return "評議会社会主義"
        elif capital <= 1:
            # 市場経済
            if power <= 1:
                # 分権的
                if power_subject >= 3:
                    return "連邦制"
                else:
                    return "大統領制民主主義"
            else:
                # 中央集権的
                if power_subject <= 1:
                    # 個人支配かつ中央集権的な市場経済
                    if power >= 4:
                        return "権威主義資本主義"
                    else:
                        return "重商主義"
                else:
                    return "官僚資本主義"
        else:
            # 混合経済
            if power <= 1:
                if power_subject >= 3:
                    return "議会制民主主義"
                else:
                    return "共和制"
            else:
                if power_subject <= 1:
                    return "立憲君主制"
                else:
                    return "議会制国家"

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "turn": self.turn,
            "resources": self.resources,  # 帝国レベルのリソース
            "ideology": self.ideology,    # 政治体制
            "regime": self.classify_regime(),  # 体制分類
            "current_city_id": self.current_city_id,
            "cities": {city_id: city.to_dict() for city_id, city in self.cities.items()},
            "event_log": self.event_log[-10:]  # 最新10件のみ送信
        }
