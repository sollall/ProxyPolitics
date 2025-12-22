"""
次のターン進行時のエラーハンドリングテスト
/api/next_turnエンドポイントの堅牢性を検証
"""
import sys
import os

# バックエンドのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.empire import Empire
from logic.command_processor import CommandProcessor
from logic.npc_ai import NPCAI


class TestNextTurnNormalCases:
    """次のターン進行の正常系テスト"""

    def test_next_turn_with_valid_commands(self):
        """正常なコマンドでターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()

        # プレイヤーコマンドを準備
        player_commands = {
            "economy": "eco_invest",
            "military": "mil_recruit"
        }

        initial_turn = empire.turn
        current_city = empire.get_current_city()

        # コマンドを実行
        for sector, command_id in player_commands.items():
            if current_city.sectors[sector].get('delegated_to') is None:
                success, message = command_processor.execute_command(empire, command_id)
                assert success is True, f"コマンド実行に失敗: {message}"

        # ターン進行
        empire.advance_turn()

        assert empire.turn == initial_turn + 1

    def test_next_turn_with_empty_commands(self):
        """空のコマンドでターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(empire.npc_manager, command_processor)

        player_commands = {}
        initial_turn = empire.turn

        # プレイヤーコマンド実行（空）
        current_city = empire.get_current_city()
        for sector, command_id in player_commands.items():
            if current_city and sector in current_city.sectors:
                if current_city.sectors[sector].get('delegated_to') is None:
                    success, message = command_processor.execute_command(empire, command_id)

        # NPCが委任された分野で自動実行
        npc_actions = npc_ai.process_delegated_sectors(empire)

        # ターン進行
        empire.advance_turn()

        # ターンが進むことを確認
        assert empire.turn == initial_turn + 1

    def test_next_turn_with_single_command(self):
        """単一のコマンドでターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()

        player_commands = {
            "economy": "eco_invest"
        }

        current_city = empire.get_current_city()
        initial_economy_progress = current_city.sectors["economy"]["progress"]

        # コマンド実行
        for sector, command_id in player_commands.items():
            if current_city.sectors[sector].get('delegated_to') is None:
                success, message = command_processor.execute_command(empire, command_id)
                assert success is True

        # 進捗が増えていることを確認
        assert current_city.sectors["economy"]["progress"] > initial_economy_progress


class TestNextTurnInvalidCommands:
    """無効なコマンドの処理テスト"""

    def test_next_turn_with_invalid_command_id(self):
        """無効なcommand_idでのターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()

        player_commands = {
            "economy": "invalid_command_id"
        }

        current_city = empire.get_current_city()

        # コマンド実行
        for sector, command_id in player_commands.items():
            if current_city and sector in current_city.sectors:
                if current_city.sectors[sector].get('delegated_to') is None:
                    success, message = command_processor.execute_command(empire, command_id)
                    # 無効なコマンドは失敗すべき
                    assert success is False
                    assert "無効なコマンド" in message

    def test_next_turn_with_invalid_sector(self):
        """存在しない分野のコマンドでのターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()

        player_commands = {
            "invalid_sector": "eco_invest"
        }

        current_city = empire.get_current_city()

        # コマンド実行
        for sector, command_id in player_commands.items():
            # 存在しない分野はスキップされる
            if current_city and sector in current_city.sectors:
                if current_city.sectors[sector].get('delegated_to') is None:
                    success, message = command_processor.execute_command(empire, command_id)

        # エラーが発生せずにターン進行できることを確認
        empire.advance_turn()
        assert empire.turn == 2


class TestNextTurnResourceShortage:
    """リソース不足時の処理テスト"""

    def test_next_turn_with_insufficient_gold(self):
        """資金不足でコマンド実行失敗"""
        empire = Empire()
        command_processor = CommandProcessor()

        # 資金を減らす
        empire.resources["gold"] = 50  # eco_investには200必要

        player_commands = {
            "economy": "eco_invest"
        }

        current_city = empire.get_current_city()

        # コマンド実行
        for sector, command_id in player_commands.items():
            if current_city.sectors[sector].get('delegated_to') is None:
                success, message = command_processor.execute_command(empire, command_id)
                # リソース不足で失敗すべき
                assert success is False
                assert "リソース不足" in message

    def test_next_turn_with_insufficient_population(self):
        """人口不足でコマンド実行失敗"""
        empire = Empire()
        command_processor = CommandProcessor()
        current_city = empire.get_current_city()

        # 人口を減らす
        current_city.resources["population"] = 50  # mil_recruitには200必要

        player_commands = {
            "military": "mil_recruit"
        }

        # コマンド実行
        for sector, command_id in player_commands.items():
            if current_city.sectors[sector].get('delegated_to') is None:
                success, message = command_processor.execute_command(empire, command_id)
                # リソース不足で失敗すべき
                assert success is False
                assert "リソース不足" in message


class TestNextTurnDelegation:
    """委任された分野の処理テスト"""

    def test_next_turn_with_delegated_sector_ignored(self):
        """委任された分野のプレイヤーコマンドは無視される"""
        empire = Empire()
        command_processor = CommandProcessor()
        city_id = empire.current_city_id
        city = empire.get_current_city()

        # 経済を委任
        empire.delegate_sector(city_id, "economy", "npc_001")

        player_commands = {
            "economy": "eco_invest"  # 委任されているので実行されない
        }

        initial_progress = city.sectors["economy"]["progress"]

        # プレイヤーコマンド実行（委任されていない分野のみ）
        for sector, command_id in player_commands.items():
            if city and sector in city.sectors:
                if city.sectors[sector].get('delegated_to') is None:
                    success, message = command_processor.execute_command(empire, command_id)

        # 委任されているので進捗は変わらない
        assert city.sectors["economy"]["progress"] == initial_progress

    def test_next_turn_with_mixed_delegation(self):
        """委任と非委任が混在する場合"""
        empire = Empire()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(empire.npc_manager, command_processor)
        city_id = empire.current_city_id
        city = empire.get_current_city()

        # 経済を委任
        empire.delegate_sector(city_id, "economy", "npc_001")

        player_commands = {
            "economy": "eco_invest",   # 委任されているので実行されない
            "military": "mil_recruit"  # 委任されていないので実行される
        }

        initial_military_progress = city.sectors["military"]["progress"]

        # プレイヤーコマンド実行（委任されていない分野のみ）
        for sector, command_id in player_commands.items():
            if city and sector in city.sectors:
                if city.sectors[sector].get('delegated_to') is None:
                    success, message = command_processor.execute_command(empire, command_id)
                    if success:
                        empire.add_event(f"[プレイヤー] {sector}分野で{message}")

        # NPCが委任された分野で自動実行
        npc_actions = npc_ai.process_delegated_sectors(empire)

        # 軍事は進捗があるはず
        assert city.sectors["military"]["progress"] > initial_military_progress

        # NPCが経済を実行したはず
        assert len(npc_actions) > 0


class TestNextTurnMultipleCities:
    """複数都市がある場合のターン進行テスト"""

    def test_next_turn_with_multiple_cities(self):
        """複数都市が存在する場合のターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()

        # 新しい都市を追加（資金を増やす）
        empire.resources["gold"] = 5000
        new_city = empire.add_city("第二都市")

        # 現在の都市でコマンド実行
        player_commands = {
            "economy": "eco_invest"
        }

        current_city = empire.get_current_city()

        for sector, command_id in player_commands.items():
            if current_city.sectors[sector].get('delegated_to') is None:
                success, message = command_processor.execute_command(empire, command_id)
                assert success is True

        # ターン進行
        empire.advance_turn()

        # 両方の都市が存在することを確認
        assert len(empire.cities) == 2
        assert empire.get_city("city_001") is not None
        assert empire.get_city(new_city.id) is not None

    def test_next_turn_with_city_switch(self):
        """都市切り替え後のターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()

        # 新しい都市を追加
        empire.resources["gold"] = 5000
        new_city = empire.add_city("第二都市")

        # 都市を切り替え
        success = empire.set_current_city(new_city.id)
        assert success is True
        assert empire.current_city_id == new_city.id

        # 新しい都市でコマンド実行
        player_commands = {
            "economy": "eco_invest"
        }

        current_city = empire.get_current_city()

        for sector, command_id in player_commands.items():
            if current_city.sectors[sector].get('delegated_to') is None:
                success, message = command_processor.execute_command(empire, command_id)
                assert success is True

        # 新しい都市の進捗が増えていることを確認
        assert current_city.sectors["economy"]["progress"] > 0


class TestNextTurnEdgeCases:
    """エッジケースのテスト"""

    def test_next_turn_with_none_commands(self):
        """Noneのコマンド辞書でのターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(empire.npc_manager, command_processor)

        # player_commandsがNoneの場合をシミュレート
        player_commands = None

        if player_commands is None:
            player_commands = {}

        current_city = empire.get_current_city()

        # プレイヤーコマンド実行
        for sector, command_id in player_commands.items():
            if current_city and sector in current_city.sectors:
                if current_city.sectors[sector].get('delegated_to') is None:
                    success, message = command_processor.execute_command(empire, command_id)

        # NPCが委任された分野で自動実行
        npc_actions = npc_ai.process_delegated_sectors(empire)

        # ターン進行
        empire.advance_turn()

        # エラーが発生しないことを確認
        assert empire.turn == 2

    def test_next_turn_multiple_times(self):
        """複数回連続してターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()

        initial_turn = empire.turn

        # 10ターン進める
        for i in range(10):
            player_commands = {
                "economy": "eco_invest"
            }

            current_city = empire.get_current_city()

            for sector, command_id in player_commands.items():
                if current_city.sectors[sector].get('delegated_to') is None:
                    # リソース不足の場合はスキップ
                    success, message = command_processor.execute_command(empire, command_id)

            empire.advance_turn()

        assert empire.turn == initial_turn + 10

    def test_next_turn_with_all_sectors_delegated(self):
        """全分野が委任されている場合のターン進行"""
        empire = Empire()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(empire.npc_manager, command_processor)
        city_id = empire.current_city_id

        # 全分野を委任
        empire.delegate_sector(city_id, "economy", "npc_001")
        empire.delegate_sector(city_id, "diplomacy", "npc_002")
        empire.delegate_sector(city_id, "military", "npc_003")

        player_commands = {
            "economy": "eco_invest",
            "diplomacy": "dip_negotiate",
            "military": "mil_recruit"
        }

        current_city = empire.get_current_city()

        # プレイヤーコマンド実行（全て委任されているので実行されない）
        player_count = 0
        for sector, command_id in player_commands.items():
            if current_city and sector in current_city.sectors:
                if current_city.sectors[sector].get('delegated_to') is None:
                    success, message = command_processor.execute_command(empire, command_id)
                    if success:
                        player_count += 1

        # プレイヤーコマンドは実行されていない
        assert player_count == 0

        # NPCが委任された分野で自動実行
        npc_actions = npc_ai.process_delegated_sectors(empire)

        # NPCが3つのアクションを実行したはず
        assert len(npc_actions) >= 3

        # ターン進行
        empire.advance_turn()

        assert empire.turn == 2

    def test_next_turn_preserves_delegation_state(self):
        """ターン進行後も委任状態が保持される"""
        empire = Empire()
        city_id = empire.current_city_id
        city = empire.get_current_city()

        # 経済を委任
        empire.delegate_sector(city_id, "economy", "npc_001")

        # ターン進行
        empire.advance_turn()

        # 委任状態が保持されていることを確認
        assert city.sectors["economy"]["delegated_to"] == "npc_001"
        assert city.sectors["diplomacy"]["delegated_to"] is None
        assert city.sectors["military"]["delegated_to"] is None
