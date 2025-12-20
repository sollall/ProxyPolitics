"""
コマンド処理ロジック
"""
from typing import Dict, Optional
import random


class Command:
    """実行可能なコマンド"""

    def __init__(self, cmd_id: str, name: str, sector: str,
                 cost: Dict[str, int], effect: Dict[str, int],
                 description: str):
        self.id = cmd_id
        self.name = name
        self.sector = sector
        self.cost = cost
        self.effect = effect
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "sector": self.sector,
            "cost": self.cost,
            "effect": self.effect,
            "description": self.description
        }


class CommandProcessor:
    """コマンド処理"""

    def __init__(self):
        self.commands = self._initialize_commands()

    def _initialize_commands(self) -> Dict[str, Command]:
        """利用可能なコマンドを初期化"""
        commands = {
            # 経済コマンド
            "eco_invest": Command(
                "eco_invest", "市場投資", "economy",
                {"gold": 200},
                {"gold": 300, "progress": 10},
                "市場に投資して経済を発展させる"
            ),
            "eco_tax": Command(
                "eco_tax", "徴税", "economy",
                {"population": -100},
                {"gold": 150, "progress": 5},
                "税金を徴収する（人口が減少）"
            ),
            "eco_trade": Command(
                "eco_trade", "交易促進", "economy",
                {"gold": 100, "diplomatic_influence": 10},
                {"gold": 200, "progress": 8},
                "交易を促進して収入を得る"
            ),

            # 外交コマンド
            "dip_negotiate": Command(
                "dip_negotiate", "外交交渉", "diplomacy",
                {"gold": 100},
                {"diplomatic_influence": 20, "progress": 10},
                "他国と交渉して影響力を高める"
            ),
            "dip_alliance": Command(
                "dip_alliance", "同盟締結", "diplomacy",
                {"gold": 300, "military_power": 50},
                {"diplomatic_influence": 50, "progress": 15},
                "同盟を結び大きな影響力を得る"
            ),
            "dip_culture": Command(
                "dip_culture", "文化交流", "diplomacy",
                {"gold": 150},
                {"diplomatic_influence": 15, "population": 200, "progress": 8},
                "文化交流で人口と影響力を増やす"
            ),

            # 軍事コマンド
            "mil_recruit": Command(
                "mil_recruit", "兵士募集", "military",
                {"gold": 200, "population": -200},
                {"military_power": 100, "progress": 10},
                "兵士を募集して軍事力を増強"
            ),
            "mil_training": Command(
                "mil_training", "軍事訓練", "military",
                {"gold": 150},
                {"military_power": 80, "progress": 8},
                "軍事訓練で戦力を向上"
            ),
            "mil_fortify": Command(
                "mil_fortify", "防衛強化", "military",
                {"gold": 250},
                {"military_power": 120, "progress": 12},
                "要塞を建設して防衛力を高める"
            ),
        }
        return commands

    def get_commands_by_sector(self, sector: str) -> list:
        """分野別のコマンドリストを取得"""
        return [cmd.to_dict() for cmd in self.commands.values()
                if cmd.sector == sector]

    def get_all_commands(self) -> list:
        """全コマンドを取得"""
        return [cmd.to_dict() for cmd in self.commands.values()]

    def execute_command(self, game_state, command_id: str) -> tuple[bool, str]:
        """コマンドを実行"""
        if command_id not in self.commands:
            return False, "無効なコマンドです"

        cmd = self.commands[command_id]

        # コスト確認
        for resource, cost in cmd.cost.items():
            if game_state.resources.get(resource, 0) < cost:
                return False, f"リソース不足: {resource}"

        # コスト支払い
        for resource, cost in cmd.cost.items():
            game_state.resources[resource] -= cost

        # 効果適用
        for resource, gain in cmd.effect.items():
            if resource == "progress":
                # 進捗を対応する分野に追加
                game_state.sectors[cmd.sector]["progress"] += gain
                # レベルアップ判定
                if game_state.sectors[cmd.sector]["progress"] >= 100:
                    game_state.sectors[cmd.sector]["level"] += 1
                    game_state.sectors[cmd.sector]["progress"] = 0
                    game_state.add_event(
                        f"{cmd.sector}分野がレベル{game_state.sectors[cmd.sector]['level']}に上昇！"
                    )
            else:
                game_state.resources[resource] = game_state.resources.get(resource, 0) + gain

        game_state.add_event(f"コマンド実行: {cmd.name}")
        return True, f"{cmd.name}を実行しました"
