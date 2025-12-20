"""
簡単な統合テスト
"""
import sys
sys.path.insert(0, '/home/user/ProxyPolitics/backend')

from models.game_state import GameState
from models.npc import NPCManager
from logic.command_processor import CommandProcessor
from logic.npc_ai import NPCAI


def test_initialization():
    """初期化のテスト"""
    print("=== 初期化テスト ===")

    game_state = GameState()
    npc_manager = NPCManager()
    command_processor = CommandProcessor()
    npc_ai = NPCAI(npc_manager, command_processor)

    print(f"✓ ゲーム状態初期化: ターン {game_state.turn}")
    print(f"✓ 初期資金: {game_state.resources['gold']}")
    print(f"✓ NPC数: {len(npc_manager.npcs)}")
    print(f"✓ コマンド数: {len(command_processor.commands)}")

    return game_state, npc_manager, command_processor, npc_ai


def test_delegation(game_state, npc_manager):
    """委任機能のテスト"""
    print("\n=== 委任機能テスト ===")

    # 経済をnpc_001に委任
    result = game_state.delegate_sector("economy", "npc_001")
    assert result == True, "委任に失敗"
    assert game_state.sectors["economy"]["delegated_to"] == "npc_001"
    print("✓ 経済分野の委任成功")

    # 軍事をnpc_002に委任
    result = game_state.delegate_sector("military", "npc_002")
    assert result == True, "委任に失敗"
    print("✓ 軍事分野の委任成功")

    # 委任解除
    result = game_state.delegate_sector("economy", None)
    assert result == True, "委任解除に失敗"
    assert game_state.sectors["economy"]["delegated_to"] is None
    print("✓ 委任解除成功")


def test_command_execution(game_state, command_processor):
    """コマンド実行のテスト"""
    print("\n=== コマンド実行テスト ===")

    initial_gold = game_state.resources['gold']

    # 市場投資コマンドを実行
    success, message = command_processor.execute_command(game_state, "eco_invest")
    assert success == True, f"コマンド実行に失敗: {message}"

    # 資金が変化したことを確認
    expected_gold = initial_gold - 200 + 300  # コスト200、効果+300
    assert game_state.resources['gold'] == expected_gold, "資金計算が不正"

    print(f"✓ コマンド実行成功: {message}")
    print(f"  資金: {initial_gold} → {game_state.resources['gold']}")

    # 進捗が増えたことを確認
    assert game_state.sectors["economy"]["progress"] > 0, "進捗が増えていない"
    print(f"  経済進捗: {game_state.sectors['economy']['progress']}%")


def test_npc_decision(game_state, npc_manager, command_processor, npc_ai):
    """NPCの自動決定テスト"""
    print("\n=== NPC自動決定テスト ===")

    # 外交を外交専門のNPCに委任
    game_state.delegate_sector("diplomacy", "npc_003")

    # NPCに決定させる
    command_id = npc_ai.decide_command(game_state, "diplomacy", "npc_003")
    assert command_id is not None, "NPCがコマンドを決定できなかった"

    npc = npc_manager.get_npc("npc_003")
    print(f"✓ NPC '{npc.name}' がコマンドを決定: {command_id}")

    # 決定したコマンドを実行
    success, message = command_processor.execute_command(game_state, command_id)
    assert success == True, f"NPC決定コマンドの実行に失敗: {message}"
    print(f"✓ NPC決定コマンド実行成功: {message}")


def test_turn_progression(game_state, npc_ai):
    """ターン進行テスト"""
    print("\n=== ターン進行テスト ===")

    # 複数の分野に委任
    game_state.delegate_sector("economy", "npc_001")
    game_state.delegate_sector("military", "npc_002")

    initial_turn = game_state.turn

    # NPCが委任された分野で自動実行
    executed = npc_ai.process_delegated_sectors(game_state)

    print(f"✓ NPCが {len(executed)} 個のコマンドを実行:")
    for action in executed:
        print(f"  - {action}")

    # ターンを進める
    game_state.advance_turn()
    assert game_state.turn == initial_turn + 1, "ターンが進んでいない"
    print(f"✓ ターン進行成功: {initial_turn} → {game_state.turn}")


def test_game_state_serialization(game_state):
    """ゲーム状態のシリアライズテスト"""
    print("\n=== シリアライズテスト ===")

    state_dict = game_state.to_dict()

    assert "turn" in state_dict
    assert "resources" in state_dict
    assert "sectors" in state_dict
    assert "event_log" in state_dict

    print("✓ ゲーム状態のシリアライズ成功")
    print(f"  含まれるキー: {list(state_dict.keys())}")


def main():
    print("ProxyPolitics 統合テスト\n")

    try:
        # 初期化テスト
        game_state, npc_manager, command_processor, npc_ai = test_initialization()

        # 委任機能テスト
        test_delegation(game_state, npc_manager)

        # コマンド実行テスト
        test_command_execution(game_state, command_processor)

        # NPC決定テスト
        test_npc_decision(game_state, npc_manager, command_processor, npc_ai)

        # ターン進行テスト
        test_turn_progression(game_state, npc_ai)

        # シリアライズテスト
        test_game_state_serialization(game_state)

        print("\n" + "="*50)
        print("✅ 全てのテストが成功しました！")
        print("="*50)

    except AssertionError as e:
        print(f"\n❌ テスト失敗: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
