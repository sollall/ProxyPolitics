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
            "capital": 0,        # 市場：0=放任、2-3=中道、5=介入（政策数で自動計算）
            "power": 0,          # 権力：0=分散、2-3=中道、5=集権
            "legitimacy": 0,     # 正統性：0=カリスマ、2-3=中道、5=超越的
            "power_subject": 0   # 権力主体：0=個人、2-3=中道、5=議会
        }

        # 市場政策（採用されている政策の数がcapital値になる）
        self.market_policies = {
            "coin_minting": False,      # 貨幣の鋳造
            "monopoly_system": False,   # 専売制
            "price_control": False,     # 価格統制
            "capital_control": False,   # 資本移動の制限
            "welfare_policy": False     # 福祉政策
        }

        # 権力政策（採用されている政策の数がpower値になる）
        self.power_policies = {
            "hereditary_ban": False,        # 世襲の禁止
            "tax_deprivation": False,       # 徴税権のはく奪
            "disband_local_army": False,    # 現地の軍隊を解散
            "appointment_authority": False, # 任免権
            "recruitment_exam": False       # 登用試験
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
        """政治体制を更新（capital・powerは政策で自動計算されるため更新不可）"""
        if axis in ["capital", "power"]:
            return False  # capital・powerは政策で自動計算
        if axis in self.ideology and 0 <= value <= 5:
            self.ideology[axis] = value
            return True
        return False

    def toggle_market_policy(self, policy: str) -> bool:
        """市場政策を切り替え"""
        if policy in self.market_policies:
            self.market_policies[policy] = not self.market_policies[policy]
            # capital値を再計算
            self.ideology["capital"] = sum(1 for p in self.market_policies.values() if p)
            return True
        return False

    def toggle_power_policy(self, policy: str) -> bool:
        """権力政策を切り替え"""
        if policy in self.power_policies:
            self.power_policies[policy] = not self.power_policies[policy]
            # power値を再計算
            self.ideology["power"] = sum(1 for p in self.power_policies.values() if p)
            return True
        return False

    def classify_regime(self) -> str:
        """イデオロギー値に基づいて政治体制を分類（0～5の6段階）"""
        capital = self.ideology["capital"]
        power = self.ideology["power"]
        legitimacy = self.ideology["legitimacy"]
        power_subject = self.ideology["power_subject"]

        # 封建制（権力 0-1）の場合、具体的な政体名を使用
        if power <= 1:
            if legitimacy <= 1:  # 個人
                if power_subject <= 1:
                    regime_name = "封建君主制"
                elif power_subject <= 3:
                    regime_name = "諸侯連合"
                else:
                    regime_name = "都市同盟"
            elif legitimacy <= 3:  # 法律
                if power_subject <= 1:
                    regime_name = "契約君主制"
                elif power_subject <= 3:
                    regime_name = "身分制議会"
                else:
                    regime_name = "自由都市連合"
            else:  # 超越
                if power_subject <= 1:
                    regime_name = "神授王権"
                elif power_subject <= 3:
                    regime_name = "聖職貴族制"
                else:
                    regime_name = "聖都連合"
        # 郡県制（権力 4-5）の場合、具体的な政体名を使用
        elif power >= 4:
            if legitimacy <= 1:  # 個人
                if power_subject <= 1:
                    regime_name = "絶対王政"
                elif power_subject <= 3:
                    regime_name = "寡頭政（オリガルキ）"
                else:
                    regime_name = "民主共和国"
            elif legitimacy <= 3:  # 法律
                if power_subject <= 1:
                    regime_name = "法治専制"
                elif power_subject <= 3:
                    regime_name = "元老院制"
                else:
                    regime_name = "立憲民主制"
            else:  # 超越
                if power_subject <= 1:
                    regime_name = "神権政治（皇帝教皇主義）"
                elif power_subject <= 3:
                    regime_name = "神官貴族制"
                else:
                    regime_name = "神聖共和国"
        else:
            # 幕藩制（権力 2-3）は既存のシステムを使用
            if legitimacy <= 1:
                legitimacy_name = "個人"
            elif legitimacy <= 3:
                legitimacy_name = "法律"
            else:
                legitimacy_name = "超越"

            if power_subject <= 1:
                power_subject_name = "専制"
            elif power_subject <= 3:
                power_subject_name = "貴族制"
            else:
                power_subject_name = "共和制"

            regime_name = f"幕藩制{legitimacy_name}{power_subject_name}"

        # 市場軸に基づいて接頭辞を付ける
        if capital <= 1:
            return f"自由貿易{regime_name}"
        elif capital >= 4:
            return f"国家統制{regime_name}"
        else:
            return regime_name

    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "turn": self.turn,
            "resources": self.resources,  # 帝国レベルのリソース
            "ideology": self.ideology,    # 政治体制
            "market_policies": self.market_policies,  # 市場政策
            "power_policies": self.power_policies,    # 権力政策
            "regime": self.classify_regime(),  # 体制分類
            "current_city_id": self.current_city_id,
            "cities": {city_id: city.to_dict() for city_id, city in self.cities.items()},
            "event_log": self.event_log[-10:]  # 最新10件のみ送信
        }
