"""
NPC採用機能のテスト
"""
import sys
sys.path.insert(0, '/home/user/ProxyPolitics/backend')

from models.game_state import GameState
from models.npc import NPCManager


def test_npc_generation():
    """NPC生成のテスト"""
    print("=== NPC生成テスト ===")

    npc_manager = NPCManager()
    initial_count = npc_manager.get_npc_count()
    print(f"初期NPC数: {initial_count}")

    # 経済専門のNPCを生成
    npc1 = npc_manager.generate_random_npc("economy")
    print(f"\n✓ 経済専門NPC生成: {npc1.name} (ID: {npc1.id})")
    print(f"  専門: {npc1.specialty}")
    print(f"  性格: {npc1.personality}")
    print(f"  主要性格: {npc1.get_decision_bias()}")

    # 外交専門のNPCを生成
    npc2 = npc_manager.generate_random_npc("diplomacy")
    print(f"\n✓ 外交専門NPC生成: {npc2.name} (ID: {npc2.id})")

    # 軍事専門のNPCを生成
    npc3 = npc_manager.generate_random_npc("military")
    print(f"✓ 軍事専門NPC生成: {npc3.name} (ID: {npc3.id})")

    # ランダム専門のNPCを生成
    npc4 = npc_manager.generate_random_npc()
    print(f"✓ ランダム専門NPC生成: {npc4.name} (ID: {npc4.id}, 専門: {npc4.specialty})")


def test_npc_recruitment():
    """NPC採用のテスト"""
    print("\n=== NPC採用テスト ===")

    npc_manager = NPCManager()
    game_state = GameState()

    initial_count = npc_manager.get_npc_count()
    initial_gold = game_state.resources['gold']

    print(f"初期NPC数: {initial_count}")
    print(f"初期資金: {initial_gold}")

    # NPCを採用
    recruitment_cost = 500
    if game_state.resources['gold'] >= recruitment_cost:
        game_state.resources['gold'] -= recruitment_cost
        new_npc = npc_manager.recruit_npc("economy")

        print(f"\n✓ NPC採用成功: {new_npc.name}")
        print(f"  採用後NPC数: {npc_manager.get_npc_count()}")
        print(f"  残り資金: {game_state.resources['gold']}")

        assert npc_manager.get_npc_count() == initial_count + 1, "NPC数が増えていない"
        assert game_state.resources['gold'] == initial_gold - recruitment_cost, "資金計算が不正"
        print("✓ 採用後の状態が正しい")


def test_multiple_recruitment():
    """複数NPC採用のテスト"""
    print("\n=== 複数NPC採用テスト ===")

    npc_manager = NPCManager()
    game_state = GameState()

    # 資金を増やす
    game_state.resources['gold'] = 5000

    specialties = ['economy', 'diplomacy', 'military', None]
    recruited = []

    for i, specialty in enumerate(specialties):
        if game_state.resources['gold'] >= 500:
            game_state.resources['gold'] -= 500
            npc = npc_manager.recruit_npc(specialty)
            recruited.append(npc)
            specialty_name = specialty if specialty else 'ランダム'
            print(f"✓ {i+1}人目採用: {npc.name} ({specialty_name}) - 残り資金: {game_state.resources['gold']}")

    print(f"\n採用完了: {len(recruited)}人のNPCを採用")
    print(f"現在のNPC数: {npc_manager.get_npc_count()}")

    # 全NPCを表示
    print("\n現在のNPCプール:")
    for npc_dict in npc_manager.get_all_npcs():
        print(f"  - {npc_dict['name']} ({npc_dict['specialty']}, 経験値: {npc_dict['experience']})")


def main():
    print("ProxyPolitics NPC採用機能テスト\n")

    try:
        test_npc_generation()
        test_npc_recruitment()
        test_multiple_recruitment()

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
