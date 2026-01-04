"""
ProxyPolitics - NPC委任型内政ゲーム
Flaskバックエンド
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

from models.empire import Empire
from logic.command_processor import CommandProcessor
from logic.npc_ai import NPCAI

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# グローバルゲーム状態（本番環境ではセッション管理が必要）
game_state = Empire()
command_processor = CommandProcessor()
npc_ai = NPCAI(game_state.npc_manager, command_processor)


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
    return jsonify(game_state.npc_manager.get_all_npcs())


@app.route('/api/commands', methods=['GET'])
def get_commands():
    """全コマンドリストを取得"""
    sector = request.args.get('sector')
    if sector:
        commands = command_processor.get_commands_by_sector(sector)
    else:
        commands = command_processor.get_all_commands()
    return jsonify(commands)


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """全都市リストを取得"""
    cities = {city_id: city.to_dict() for city_id, city in game_state.cities.items()}
    return jsonify({
        "cities": cities,
        "current_city_id": game_state.current_city_id
    })


@app.route('/api/cities/<city_id>/switch', methods=['POST'])
def switch_city(city_id):
    """都市を切り替え"""
    success = game_state.set_current_city(city_id)

    if success:
        city = game_state.get_city(city_id)
        return jsonify({
            "success": True,
            "message": f"{city.name}に切り替えました",
            "current_city_id": game_state.current_city_id,
            "state": game_state.to_dict()
        })
    else:
        return jsonify({
            "success": False,
            "message": "無効な都市IDです"
        }), 400


@app.route('/api/cities/add', methods=['POST'])
def add_city():
    """新しい都市を追加"""
    data = request.json
    name = data.get('name', '新しい都市')

    # コスト（将来的には征服や建設のコストを設定）
    cost = 2000

    if game_state.resources.get('gold', 0) < cost:
        return jsonify({
            "success": False,
            "message": f"資金不足です（必要: {cost}、所持: {game_state.resources['gold']}）"
        }), 400

    game_state.resources['gold'] -= cost
    new_city = game_state.add_city(name)

    return jsonify({
        "success": True,
        "message": f"新しい都市「{name}」を獲得しました",
        "city": new_city.to_dict(),
        "state": game_state.to_dict()
    })


@app.route('/api/set_governor', methods=['POST'])
def set_governor():
    """都市に総督を設定"""
    data = request.json
    city_id = data.get('city_id')
    npc_id = data.get('npc_id')  # Noneの場合は総督解除

    city = game_state.get_city(city_id)
    if not city:
        return jsonify({
            "success": False,
            "message": "無効な都市IDです"
        }), 400

    city.set_governor(npc_id)

    if npc_id:
        npc = game_state.npc_manager.get_npc(npc_id)
        npc_name = npc.name if npc else "不明"
        game_state.add_event(f"[{city.name}] {npc_name}を総督に任命しました")
        message = f"{city.name}の総督に{npc_name}を任命しました"
    else:
        game_state.add_event(f"[{city.name}] 総督を解任しました")
        message = f"{city.name}の総督を解任しました"

    return jsonify({
        "success": True,
        "message": message,
        "state": game_state.to_dict()
    })


@app.route('/api/delegate', methods=['POST'])
def delegate_sector():
    """分野にNPCを委任"""
    data = request.json
    sector = data.get('sector')
    npc_id = data.get('npc_id')  # Noneの場合は委任解除
    city_id = data.get('city_id', game_state.current_city_id)  # デフォルトは現在の都市

    success = game_state.delegate_sector(city_id, sector, npc_id)

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
    """次のターンへ進む（プレイヤーとNPCのコマンド実行）"""
    data = request.json or {}
    player_commands = data.get('player_commands', {})  # {sector: command_id}

    player_actions = []
    npc_actions = []

    # プレイヤーのコマンドを実行（委任されていない分野のみ）
    current_city = game_state.get_current_city()
    for sector, command_id in player_commands.items():
        if current_city and sector in current_city.sectors:
            # 委任されていないことを確認
            if current_city.sectors[sector].get('delegated_to') is None:
                success, message = command_processor.execute_command(game_state, command_id)
                if success:
                    log_message = f"[プレイヤー] {sector}分野で{message}"
                    player_actions.append(log_message)
                    game_state.add_event(log_message)

    # NPCが委任された分野で自動実行
    npc_actions = npc_ai.process_delegated_sectors(game_state)

    # ターン進行
    game_state.advance_turn()

    # ランダムイベント（人口増加など）
    import random
    population_growth = random.randint(50, 200)
    if current_city:
        current_city.resources["population"] += population_growth
        game_state.add_event(f"[{current_city.name}] 人口が{population_growth}人増加しました")

    return jsonify({
        "success": True,
        "player_actions": player_actions,
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
    new_npc = game_state.npc_manager.recruit_npc(specialty)

    game_state.add_event(f"新しいNPC「{new_npc.name}」を採用しました（コスト: {recruitment_cost}）")

    return jsonify({
        "success": True,
        "message": f"NPCを採用しました: {new_npc.name}",
        "npc": new_npc.to_dict(),
        "state": game_state.to_dict(),
        "all_npcs": game_state.npc_manager.get_all_npcs()
    })


@app.route('/api/ideology', methods=['POST'])
def update_ideology():
    """政治体制を更新"""
    data = request.json
    axis = data.get('axis')
    value = data.get('value')

    if not axis or value is None:
        return jsonify({
            "success": False,
            "message": "軸と値が必要です"
        }), 400

    success = game_state.update_ideology(axis, int(value))

    if success:
        return jsonify({
            "success": True,
            "state": game_state.to_dict()
        })
    else:
        return jsonify({
            "success": False,
            "message": "無効な軸または値です"
        }), 400


@app.route('/api/market_policy', methods=['POST'])
def toggle_market_policy():
    """市場政策を切り替え"""
    data = request.json
    policy = data.get('policy')

    if not policy:
        return jsonify({
            "success": False,
            "message": "政策名が必要です"
        }), 400

    success = game_state.toggle_market_policy(policy)

    if success:
        return jsonify({
            "success": True,
            "state": game_state.to_dict()
        })
    else:
        return jsonify({
            "success": False,
            "message": "無効な政策名です"
        }), 400


@app.route('/api/power_policy', methods=['POST'])
def toggle_power_policy():
    """権力政策を切り替え"""
    data = request.json
    policy = data.get('policy')

    if not policy:
        return jsonify({
            "success": False,
            "message": "政策名が必要です"
        }), 400

    success = game_state.toggle_power_policy(policy)

    if success:
        return jsonify({
            "success": True,
            "state": game_state.to_dict()
        })
    else:
        return jsonify({
            "success": False,
            "message": "無効な政策名です"
        }), 400


@app.route('/api/transfer_resources', methods=['POST'])
def transfer_resources():
    """帝国から都市へリソースを転送"""
    data = request.json
    city_id = data.get('city_id')
    gold_amount = data.get('gold', 0)
    military_amount = data.get('military', 0)

    city = game_state.get_city(city_id)
    if not city:
        return jsonify({
            "success": False,
            "message": "無効な都市IDです"
        }), 400

    # 帝国のリソースが足りるか確認
    if game_state.resources.get('gold', 0) < gold_amount:
        return jsonify({
            "success": False,
            "message": f"帝国の資金が不足しています（必要: {gold_amount}、所持: {game_state.resources['gold']}）"
        }), 400

    if game_state.resources.get('military', 0) < military_amount:
        return jsonify({
            "success": False,
            "message": f"帝国の軍隊が不足しています（必要: {military_amount}、所持: {game_state.resources['military']}）"
        }), 400

    # リソースを転送
    if gold_amount > 0:
        game_state.resources['gold'] -= gold_amount
        city.resources['gold'] = city.resources.get('gold', 0) + gold_amount
        game_state.add_event(f"[{city.name}] 帝国から資金{gold_amount}を配分しました")

    if military_amount > 0:
        game_state.resources['military'] -= military_amount
        city.resources['military_power'] = city.resources.get('military_power', 0) + military_amount
        game_state.add_event(f"[{city.name}] 帝国から軍隊{military_amount}を配分しました")

    return jsonify({
        "success": True,
        "message": f"{city.name}にリソースを配分しました",
        "state": game_state.to_dict()
    })


@app.route('/api/add_empire_resource', methods=['POST'])
def add_empire_resource():
    """帝国リソースを追加（チート用）"""
    data = request.json
    resource_type = data.get('resource_type')  # 'gold' or 'military'
    amount = data.get('amount', 1000)

    if resource_type not in ['gold', 'military']:
        return jsonify({
            "success": False,
            "message": "無効なリソースタイプです"
        }), 400

    game_state.resources[resource_type] += amount
    game_state.add_event(f"帝国の{resource_type}が{amount}増加しました")

    return jsonify({
        "success": True,
        "message": f"{resource_type}を{amount}追加しました",
        "state": game_state.to_dict()
    })


@app.route('/api/reset', methods=['POST'])
def reset_game():
    """ゲームをリセット"""
    global game_state
    game_state = Empire()

    return jsonify({
        "success": True,
        "message": "ゲームをリセットしました",
        "state": game_state.to_dict()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
