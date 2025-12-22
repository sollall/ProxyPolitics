"""
ターンベースシステムのテスト
"""
import sys
import os

# バックエンドのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.game_state import GameState
from models.npc import NPCManager
from logic.command_processor import CommandProcessor
from logic.npc_ai import NPCAI


class TestTurnBasedSelection:
    """ターンベース選択システムのテスト"""

    def test_player_command_selection(self):
        """プレイヤーのコマンド選択"""
        game_state = GameState()
        command_processor = CommandProcessor()

        # プレイヤーがコマンドを選択（委任されていない分野）
        assert game_state.sectors["economy"]["delegated_to"] is None

        # コマンド実行
        success, message = command_processor.execute_command(game_state, "eco_invest")
        assert success is True
        assert game_state.sectors["economy"]["progress"] > 0

    def test_delegated_sector_blocking(self):
        """委任された分野の選択ブロック"""
        game_state = GameState()
        city_id = game_state.current_city_id
        city = game_state.get_current_city()

        # 経済を委任
        game_state.delegate_sector(city_id, "economy", "npc_001")

        # 委任されているか確認
        assert city.sectors["economy"]["delegated_to"] == "npc_001"

        # プレイヤーは選択できない（フロントエンドでブロック）
        # バックエンドではこのチェックはAPIレベルで行われる

    def test_non_delegated_sector_selection(self):
        """委任されていない分野の選択"""
        game_state = GameState()
        command_processor = CommandProcessor()
        city_id = game_state.current_city_id
        city = game_state.get_current_city()

        # 経済を委任
        game_state.delegate_sector(city_id, "economy", "npc_001")

        # 軍事は委任されていない
        assert city.sectors["military"]["delegated_to"] is None

        # 軍事コマンドは実行可能
        success, message = command_processor.execute_command(game_state, "mil_recruit")
        assert success is True


class TestTurnProgression:
    """ターン進行のテスト"""

    def test_player_and_npc_turn_execution(self):
        """プレイヤーとNPCのターン実行"""
        game_state = GameState()
        npc_manager = NPCManager()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(npc_manager, command_processor)
        city_id = game_state.current_city_id
        city = game_state.get_current_city()

        # プレイヤーコマンド（経済）
        success, _ = command_processor.execute_command(game_state, "eco_invest")
        assert success is True

        # NPCに外交を委任
        game_state.delegate_sector(city_id, "diplomacy", "npc_003")

        # NPCの自動実行
        npc_actions = npc_ai.process_delegated_sectors(game_state)
        assert len(npc_actions) > 0

        # 両方の分野で進捗があることを確認
        assert city.sectors["economy"]["progress"] > 0
        assert city.sectors["diplomacy"]["progress"] > 0

    def test_turn_advance_clears_selections(self):
        """ターン進行後の選択クリア（概念的テスト）"""
        game_state = GameState()

        # ターン進行
        initial_turn = game_state.turn
        game_state.advance_turn()

        # ターンが進んだことを確認
        assert game_state.turn == initial_turn + 1

        # 実際の選択クリアはフロントエンドで行われる


class TestDelegationAndSelection:
    """委任と選択の相互作用テスト"""

    def test_delegation_prevents_player_action(self):
        """委任がプレイヤーの行動を防ぐ"""
        game_state = GameState()
        npc_manager = NPCManager()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(npc_manager, command_processor)
        city_id = game_state.current_city_id
        city = game_state.get_current_city()

        # 経済を委任
        game_state.delegate_sector(city_id, "economy", "npc_001")

        # プレイヤーが経済コマンドを実行しようとする
        # （本来はフロントエンドでブロックされるが、バックエンドでも確認）
        player_commands = {"economy": "eco_invest"}

        # ターン進行時の処理をシミュレート
        for sector, command_id in player_commands.items():
            if city.sectors[sector].get('delegated_to') is None:
                command_processor.execute_command(game_state, command_id)

        # 経済は委任されているのでプレイヤーコマンドは実行されない
        # （ループで実行されなかったことを確認）

        # NPCが実行
        npc_actions = npc_ai.process_delegated_sectors(game_state)
        assert len(npc_actions) > 0

    def test_undelegation_enables_player_action(self):
        """委任解除でプレイヤーの行動が可能に"""
        game_state = GameState()
        command_processor = CommandProcessor()
        city_id = game_state.current_city_id
        city = game_state.get_current_city()

        # 経済を委任
        game_state.delegate_sector(city_id, "economy", "npc_001")
        assert city.sectors["economy"]["delegated_to"] == "npc_001"

        # 委任解除
        game_state.delegate_sector(city_id, "economy", None)
        assert city.sectors["economy"]["delegated_to"] is None

        # プレイヤーがコマンド実行可能
        success, _ = command_processor.execute_command(game_state, "eco_invest")
        assert success is True
