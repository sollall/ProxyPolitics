"""
ProxyPolitics - NPC委任型内政ゲーム
Flaskバックエンド
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

from models.game_state import GameState
from models.npc import NPCManager
from logic.command_processor import CommandProcessor
from logic.npc_ai import NPCAI

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# グローバルゲーム状態（本番環境ではセッション管理が必要）
game_state = GameState()
npc_manager = NPCManager()
command_processor = CommandProcessor()
npc_ai = NPCAI(npc_manager, command_processor)


@app.route('/')
def index():
    """フロントエンドを提供"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/state', methods=['GET'])
def get_state():
    """現在のゲーム状態を取得"""
    return jsonify(game_state.to_dict())


@app.route('/api/npcs', methods=['GET'])
def get_npcs():
    """全NPCリストを取得"""
    return jsonify(npc_manager.get_all_npcs())


@app.route('/api/commands', methods=['GET'])
def get_commands():
    """全コマンドリストを取得"""
    sector = request.args.get('sector')
    if sector:
        commands = command_processor.get_commands_by_sector(sector)
    else:
        commands = command_processor.get_all_commands()
    return jsonify(commands)


@app.route('/api/delegate', methods=['POST'])
def delegate_sector():
    """分野にNPCを委任"""
    data = request.json
    sector = data.get('sector')
    npc_id = data.get('npc_id')  # Noneの場合は委任解除

    success = game_state.delegate_sector(sector, npc_id)

    if success:
        return jsonify({
            "success": True,
            "message": f"{sector}の委任を更新しました",
            "state": game_state.to_dict()
        })
    else:
        return jsonify({
            "success": False,
            "message": "無効な分野です"
        }), 400


@app.route('/api/execute', methods=['POST'])
def execute_command():
    """プレイヤーがコマンドを実行"""
    data = request.json
    command_id = data.get('command_id')

    success, message = command_processor.execute_command(game_state, command_id)

    return jsonify({
        "success": success,
        "message": message,
        "state": game_state.to_dict()
    })


@app.route('/api/next_turn', methods=['POST'])
def next_turn():
    """次のターンへ進む（NPCが委任された分野で自動実行）"""
    # NPCが委任された分野で自動実行
    npc_actions = npc_ai.process_delegated_sectors(game_state)

    # ターン進行
    game_state.advance_turn()

    # ランダムイベント（人口増加など）
    import random
    population_growth = random.randint(50, 200)
    game_state.resources["population"] += population_growth
    game_state.add_event(f"人口が{population_growth}人増加しました")

    return jsonify({
        "success": True,
        "npc_actions": npc_actions,
        "state": game_state.to_dict()
    })


@app.route('/api/recruit_npc', methods=['POST'])
def recruit_npc():
    """新しいNPCを採用"""
    data = request.json
    specialty = data.get('specialty')  # Noneの場合はランダム

    # 採用コスト
    recruitment_cost = 500

    # 資金確認
    if game_state.resources.get('gold', 0) < recruitment_cost:
        return jsonify({
            "success": False,
            "message": f"資金不足です（必要: {recruitment_cost}、所持: {game_state.resources['gold']}）"
        }), 400

    # 資金を支払い
    game_state.resources['gold'] -= recruitment_cost

    # NPCを採用
    new_npc = npc_manager.recruit_npc(specialty)

    game_state.add_event(f"新しいNPC「{new_npc.name}」を採用しました（コスト: {recruitment_cost}）")

    return jsonify({
        "success": True,
        "message": f"NPCを採用しました: {new_npc.name}",
        "npc": new_npc.to_dict(),
        "state": game_state.to_dict(),
        "all_npcs": npc_manager.get_all_npcs()
    })


@app.route('/api/reset', methods=['POST'])
def reset_game():
    """ゲームをリセット"""
    global game_state, npc_manager
    game_state = GameState()
    npc_manager = NPCManager()

    return jsonify({
        "success": True,
        "message": "ゲームをリセットしました",
        "state": game_state.to_dict()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
