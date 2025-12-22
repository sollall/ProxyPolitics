"""
NPCのAI意思決定ロジック
"""
import random
from typing import Optional, List, Dict


class NPCAI:
    """NPCの自動意思決定"""

    def __init__(self, npc_manager, command_processor):
        self.npc_manager = npc_manager
        self.command_processor = command_processor

    def decide_command(self, game_state, sector: str, npc_id: str) -> Optional[str]:
        """
        NPCが委任された分野でコマンドを決定

        Args:
            game_state: ゲーム状態
            sector: 委任された分野
            npc_id: NPC ID

        Returns:
            選択されたコマンドID、または None
        """
        npc = self.npc_manager.get_npc(npc_id)
        if not npc:
            return None

        # 分野のコマンドリストを取得
        available_commands = self.command_processor.get_commands_by_sector(sector)

        # 実行可能なコマンドのみフィルタリング
        executable_commands = []
        for cmd_dict in available_commands:
            can_execute = True
            for resource, cost in cmd_dict["cost"].items():
                if game_state.resources.get(resource, 0) < cost:
                    can_execute = False
                    break
            if can_execute:
                executable_commands.append(cmd_dict)

        if not executable_commands:
            return None

        # NPCの性格に基づいて選択
        decision_bias = npc.get_decision_bias()
        selected_command = self._select_by_personality(
            executable_commands, decision_bias, npc.specialty, sector
        )

        # 経験値を増加
        npc.experience += 1

        return selected_command["id"] if selected_command else None

    def _select_by_personality(self, commands: List[Dict],
                               bias: str, specialty: str, sector: str) -> Optional[Dict]:
        """
        性格に基づいてコマンドを選択

        Args:
            commands: 実行可能なコマンドリスト
            bias: 性格傾向 ("aggressive", "cautious", "balanced")
            specialty: NPCの専門分野
            sector: 委任された分野

        Returns:
            選択されたコマンド
        """
        if not commands:
            return None

        # 専門分野の場合はボーナス
        specialty_bonus = 1.5 if specialty == sector else 1.0

        # 性格に基づいた選択
        if bias == "aggressive":
            # 効果が高いコマンドを優先（コストは気にしない）
            scored_commands = []
            for cmd in commands:
                total_effect = sum(cmd["effect"].values())
                score = total_effect * specialty_bonus * random.uniform(0.8, 1.2)
                scored_commands.append((cmd, score))

            scored_commands.sort(key=lambda x: x[1], reverse=True)
            return scored_commands[0][0]

        elif bias == "cautious":
            # コストパフォーマンスを優先
            scored_commands = []
            for cmd in commands:
                total_effect = sum(cmd["effect"].values())
                total_cost = sum(cmd["cost"].values())
                efficiency = total_effect / max(total_cost, 1)
                score = efficiency * specialty_bonus * random.uniform(0.8, 1.2)
                scored_commands.append((cmd, score))

            scored_commands.sort(key=lambda x: x[1], reverse=True)
            return scored_commands[0][0]

        else:  # balanced
            # バランス良く選択（ランダム性高め）
            weights = [specialty_bonus if cmd == commands[0] else 1.0
                      for cmd in commands]
            return random.choices(commands, weights=weights)[0]

    def process_delegated_sectors(self, game_state, city_id: str = None) -> List[str]:
        """
        委任された全分野のNPC決定を処理

        Args:
            game_state: ゲーム状態
            city_id: 処理する都市ID（Noneの場合は全都市）

        Returns:
            実行されたコマンドのログ
        """
        executed_commands = []

        # 処理する都市のリストを決定
        if city_id:
            cities = {city_id: game_state.get_city(city_id)}
        else:
            cities = game_state.cities

        # 各都市の委任された分野を処理
        for cid, city in cities.items():
            if not city:
                continue

            for sector, sector_data in city.sectors.items():
                npc_id = sector_data.get("delegated_to")
                if npc_id:
                    # NPCが決定（都市ごとのゲーム状態を渡す）
                    command_id = self.decide_command(game_state, sector, npc_id)
                    if command_id:
                        npc = self.npc_manager.get_npc(npc_id)
                        success, message = self.command_processor.execute_command(
                            game_state, command_id, cid
                        )
                        if success:
                            log_message = f"[NPC: {npc.name}] [{city.name}] {sector}分野で{message}"
                            executed_commands.append(log_message)
                            # add_eventは既にcommand_processor内で呼ばれているのでここでは不要

        return executed_commands
