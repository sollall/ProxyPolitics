"""
ゲームロジックのテスト
"""
import sys
import os

# バックエンドのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.empire import Empire
from logic.command_processor import CommandProcessor
from logic.npc_ai import NPCAI


class TestGameInitialization:
    """ゲーム初期化のテスト"""

    def test_game_state_initialization(self):
        """帝国の初期化"""
        empire = Empire()
        city = empire.get_current_city()
        assert empire.turn == 1
        assert empire.resources['gold'] == 1000
        assert city.resources['population'] == 10000
        assert len(city.sectors) == 3

    def test_npc_manager_initialization(self):
        """NPCマネージャーの初期化"""
        empire = Empire()
        assert empire.npc_manager.get_npc_count() == 5
        npcs = empire.npc_manager.get_all_npcs()
        assert len(npcs) == 5

    def test_command_processor_initialization(self):
        """コマンドプロセッサーの初期化"""
        command_processor = CommandProcessor()
        commands = command_processor.get_all_commands()
        assert len(commands) == 9  # 3分野 × 3コマンド


class TestDelegation:
    """委任機能のテスト"""

    def test_delegate_sector(self):
        """分野の委任"""
        empire = Empire()
        city_id = empire.current_city_id
        result = empire.delegate_sector(city_id, "economy", "npc_001")
        assert result is True
        assert empire.cities[city_id].sectors["economy"]["delegated_to"] == "npc_001"

    def test_undelegate_sector(self):
        """委任の解除"""
        empire = Empire()
        city_id = empire.current_city_id
        empire.delegate_sector(city_id, "economy", "npc_001")
        result = empire.delegate_sector(city_id, "economy", None)
        assert result is True
        assert empire.cities[city_id].sectors["economy"]["delegated_to"] is None

    def test_invalid_sector_delegation(self):
        """無効な分野への委任"""
        empire = Empire()
        city_id = empire.current_city_id
        result = empire.delegate_sector(city_id, "invalid", "npc_001")
        assert result is False


class TestCommandExecution:
    """コマンド実行のテスト"""

    def test_execute_command(self):
        """コマンドの実行"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        success, message = command_processor.execute_command(empire, "eco_invest")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 200 + 300
        assert city.sectors["economy"]["progress"] > 0

    def test_insufficient_resources(self):
        """リソース不足時のコマンド実行"""
        empire = Empire()
        command_processor = CommandProcessor()

        # 資金を0にする
        empire.resources['gold'] = 0

        success, message = command_processor.execute_command(empire, "eco_invest")
        assert success is False
        assert "不足" in message


class TestNPCDecision:
    """NPC意思決定のテスト"""

    def test_npc_command_decision(self):
        """NPCのコマンド決定"""
        empire = Empire()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(empire.npc_manager, command_processor)

        command_id = npc_ai.decide_command(empire, "economy", "npc_001")
        assert command_id is not None
        assert command_id.startswith("eco_")

    def test_npc_delegated_execution(self):
        """委任されたNPCの自動実行"""
        empire = Empire()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(empire.npc_manager, command_processor)

        city_id = empire.current_city_id
        empire.delegate_sector(city_id, "economy", "npc_001")
        executed = npc_ai.process_delegated_sectors(empire)

        assert len(executed) > 0
        assert any("economy" in action for action in executed)


class TestTurnProgression:
    """ターン進行のテスト"""

    def test_turn_advance(self):
        """ターンの進行"""
        empire = Empire()
        initial_turn = empire.turn

        empire.advance_turn()
        assert empire.turn == initial_turn + 1

    def test_player_and_npc_actions(self):
        """プレイヤーとNPCの並行実行"""
        empire = Empire()
        command_processor = CommandProcessor()
        npc_ai = NPCAI(empire.npc_manager, command_processor)

        city_id = empire.current_city_id
        city = empire.get_current_city()

        # プレイヤーが経済コマンド実行
        command_processor.execute_command(empire, "eco_invest")

        # 外交をNPCに委任
        empire.delegate_sector(city_id, "diplomacy", "npc_003")

        # NPCが委任された分野で実行
        npc_actions = npc_ai.process_delegated_sectors(empire)

        assert len(npc_actions) > 0
        assert city.sectors["economy"]["progress"] > 0
        assert city.sectors["diplomacy"]["progress"] > 0


class TestAllCommands:
    """全コマンドのテスト"""

    def test_economy_invest(self):
        """経済：市場投資"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        success, message = command_processor.execute_command(empire, "eco_invest")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 200 + 300
        assert city.sectors["economy"]["progress"] >= 10

    def test_economy_tax(self):
        """経済：徴税"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_population = city.resources['population']
        success, message = command_processor.execute_command(empire, "eco_tax")

        assert success is True
        assert empire.resources['gold'] == initial_gold + 150
        assert city.resources['population'] == initial_population - 100
        assert city.sectors["economy"]["progress"] >= 5

    def test_economy_trade(self):
        """経済：交易促進"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_influence = city.resources['diplomatic_influence']
        success, message = command_processor.execute_command(empire, "eco_trade")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 100 + 200
        assert city.resources['diplomatic_influence'] == initial_influence - 10
        assert city.sectors["economy"]["progress"] >= 8

    def test_diplomacy_negotiate(self):
        """外交：外交交渉"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_influence = city.resources['diplomatic_influence']
        success, message = command_processor.execute_command(empire, "dip_negotiate")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 100
        assert city.resources['diplomatic_influence'] == initial_influence + 20
        assert city.sectors["diplomacy"]["progress"] >= 10

    def test_diplomacy_alliance(self):
        """外交：同盟締結"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_influence = city.resources['diplomatic_influence']
        initial_military = city.resources['military_power']
        success, message = command_processor.execute_command(empire, "dip_alliance")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 300
        assert city.resources['diplomatic_influence'] == initial_influence + 50
        assert city.resources['military_power'] == initial_military - 50
        assert city.sectors["diplomacy"]["progress"] >= 15

    def test_diplomacy_culture(self):
        """外交：文化交流"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_influence = city.resources['diplomatic_influence']
        initial_population = city.resources['population']
        success, message = command_processor.execute_command(empire, "dip_culture")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 150
        assert city.resources['diplomatic_influence'] == initial_influence + 15
        assert city.resources['population'] == initial_population + 200
        assert city.sectors["diplomacy"]["progress"] >= 8

    def test_military_recruit(self):
        """軍事：兵士募集"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_population = city.resources['population']
        initial_military = city.resources['military_power']
        success, message = command_processor.execute_command(empire, "mil_recruit")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 200
        assert city.resources['population'] == initial_population - 200
        assert city.resources['military_power'] == initial_military + 100
        assert city.sectors["military"]["progress"] >= 10

    def test_military_training(self):
        """軍事：軍事訓練"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_military = city.resources['military_power']
        success, message = command_processor.execute_command(empire, "mil_training")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 150
        assert city.resources['military_power'] == initial_military + 80
        assert city.sectors["military"]["progress"] >= 8

    def test_military_fortify(self):
        """軍事：防衛強化"""
        empire = Empire()
        command_processor = CommandProcessor()
        city = empire.get_current_city()

        initial_gold = empire.resources['gold']
        initial_military = city.resources['military_power']
        success, message = command_processor.execute_command(empire, "mil_fortify")

        assert success is True
        assert empire.resources['gold'] == initial_gold - 250
        assert city.resources['military_power'] == initial_military + 120
        assert city.sectors["military"]["progress"] >= 12
