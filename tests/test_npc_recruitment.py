"""
NPC採用機能のテスト
"""
import sys
import os

# バックエンドのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.game_state import GameState
from models.npc import NPCManager


class TestNPCGeneration:
    """NPC生成のテスト"""

    def test_generate_economy_specialist(self):
        """経済専門NPCの生成"""
        npc_manager = NPCManager()
        npc = npc_manager.generate_random_npc("economy")

        assert npc.specialty == "economy"
        assert npc.name is not None
        assert len(npc.name) > 0
        assert npc.loyalty == 100
        assert npc.experience == 0

    def test_generate_diplomacy_specialist(self):
        """外交専門NPCの生成"""
        npc_manager = NPCManager()
        npc = npc_manager.generate_random_npc("diplomacy")

        assert npc.specialty == "diplomacy"

    def test_generate_military_specialist(self):
        """軍事専門NPCの生成"""
        npc_manager = NPCManager()
        npc = npc_manager.generate_random_npc("military")

        assert npc.specialty == "military"

    def test_generate_random_specialty(self):
        """ランダム専門NPCの生成"""
        npc_manager = NPCManager()
        npc = npc_manager.generate_random_npc()

        assert npc.specialty in ["economy", "diplomacy", "military"]

    def test_personality_generation(self):
        """性格の生成"""
        npc_manager = NPCManager()
        npc = npc_manager.generate_random_npc()

        assert "aggressive" in npc.personality
        assert "cautious" in npc.personality
        assert "balanced" in npc.personality
        assert all(1 <= v <= 10 for v in npc.personality.values())


class TestNPCRecruitment:
    """NPC採用のテスト"""

    def test_recruit_npc(self):
        """NPCの採用"""
        npc_manager = NPCManager()
        initial_count = npc_manager.get_npc_count()

        new_npc = npc_manager.recruit_npc("economy")

        assert npc_manager.get_npc_count() == initial_count + 1
        assert npc_manager.get_npc(new_npc.id) is not None

    def test_recruitment_with_cost(self):
        """コスト支払いありのNPC採用"""
        game_state = GameState()
        npc_manager = NPCManager()

        recruitment_cost = 500
        initial_gold = game_state.resources['gold']

        # コスト確認と支払い
        assert game_state.resources['gold'] >= recruitment_cost
        game_state.resources['gold'] -= recruitment_cost

        # 採用
        new_npc = npc_manager.recruit_npc("economy")

        assert game_state.resources['gold'] == initial_gold - recruitment_cost
        assert new_npc is not None

    def test_multiple_recruitment(self):
        """複数NPCの採用"""
        npc_manager = NPCManager()
        initial_count = npc_manager.get_npc_count()

        for i in range(3):
            npc_manager.recruit_npc()

        assert npc_manager.get_npc_count() == initial_count + 3


class TestNPCManager:
    """NPCマネージャーのテスト"""

    def test_get_npc_by_id(self):
        """IDでNPCを取得"""
        npc_manager = NPCManager()
        npc = npc_manager.get_npc("npc_001")

        assert npc is not None
        assert npc.id == "npc_001"

    def test_get_npcs_by_specialty(self):
        """専門分野でNPCを取得"""
        npc_manager = NPCManager()
        economy_npcs = npc_manager.get_npcs_by_specialty("economy")

        assert len(economy_npcs) > 0
        assert all(npc["specialty"] == "economy" for npc in economy_npcs)

    def test_npc_counter_increment(self):
        """NPCカウンターの増分"""
        npc_manager = NPCManager()
        npc1 = npc_manager.recruit_npc()
        npc2 = npc_manager.recruit_npc()

        # IDが連番になっていることを確認
        id1_num = int(npc1.id.split('_')[1])
        id2_num = int(npc2.id.split('_')[1])

        assert id2_num == id1_num + 1
