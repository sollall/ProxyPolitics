"""
ターンベースシステムのテスト
"""
import sys
sys.path.insert(0, '/home/user/ProxyPolitics/backend')

from models.game_state import GameState
from models.npc import NPCManager
from logic.command_processor import CommandProcessor
from logic.npc_ai import NPCAI


def test_turn_based_system():
    """ターンベースシステムのテスト"""
    print("=== ターンベースシステムテスト ===\n")

    game_state = GameState()
    npc_manager = NPCManager()
    command_processor = CommandProcessor()
    npc_ai = NPCAI(npc_manager, command_processor)

    print(f"初期状態:")
    print(f"  ターン: {game_state.turn}")
    print(f"  資金: {game_state.resources['gold']}")
    print(f"  経済レベル: {game_state.sectors['economy']['level']}")
    print(f"  経済進捗: {game_state.sectors['economy']['progress']}")

    # プレイヤーがコマンドを選択（経済分野で市場投資）
    print("\n--- プレイヤーアクション ---")
    player_commands = {"economy": "eco_invest"}

    # プレイヤーコマンドを実行
    for sector, command_id in player_commands.items():
        if game_state.sectors[sector].get('delegated_to') is None:
            success, message = command_processor.execute_command(game_state, command_id)
            if success:
                print(f"✓ [プレイヤー] {sector}分野で{message}")

    # 外交分野をNPCに委任
    print("\n--- NPC委任 ---")
    game_state.delegate_sector("diplomacy", "npc_003")
    print(f"✓ 外交分野を{npc_manager.get_npc('npc_003').name}に委任")

    # NPCが委任された分野で実行
    print("\n--- NPCアクション ---")
    npc_actions = npc_ai.process_delegated_sectors(game_state)
    for action in npc_actions:
        print(f"✓ {action}")

    # ターン進行
    game_state.advance_turn()
    game_state.resources["population"] += 100

    print(f"\n実行後の状態:")
    print(f"  ターン: {game_state.turn}")
    print(f"  資金: {game_state.resources['gold']}")
    print(f"  経済レベル: {game_state.sectors['economy']['level']}")
    print(f"  経済進捗: {game_state.sectors['economy']['progress']}")
    print(f"  外交進捗: {game_state.sectors['diplomacy']['progress']}")


def test_delegation_blocking():
    """委任時の選択ブロックテスト"""
    print("\n\n=== 委任時の選択ブロックテスト ===\n")

    game_state = GameState()
    npc_manager = NPCManager()
    command_processor = CommandProcessor()

    # 経済分野を委任
    game_state.delegate_sector("economy", "npc_001")
    print(f"✓ 経済分野を委任")

    # 委任された分野で選択を試みる
    print("\n委任された分野での選択を確認:")
    if game_state.sectors["economy"]["delegated_to"] is not None:
        print("✓ 経済分野は委任されているため、プレイヤーは選択不可")
    else:
        print("✗ エラー: 委任されているはずが選択可能")

    # 委任されていない分野は選択可能
    print("\n委任されていない分野での選択を確認:")
    if game_state.sectors["military"]["delegated_to"] is None:
        print("✓ 軍事分野は委任されていないため、プレイヤーは選択可能")
        success, message = command_processor.execute_command(game_state, "mil_recruit")
        if success:
            print(f"✓ {message}")
    else:
        print("✗ エラー: 委任されていないはずが選択不可")


def main():
    print("ProxyPolitics ターンベースシステムテスト\n")

    try:
        test_turn_based_system()
        test_delegation_blocking()

        print("\n" + "="*50)
        print("✅ 全てのテストが成功しました！")
        print("="*50)

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
