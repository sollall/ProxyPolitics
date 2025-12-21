// ProxyPolitics - フロントエンドJavaScript

const API_BASE = 'http://localhost:5000/api';

let gameState = null;
let allNPCs = [];
let allCommands = [];
let currentDelegationSector = null;
let selectedCommands = {
    economy: null,
    diplomacy: null,
    military: null
}; // 各分野で選択されたコマンド

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    loadGameState();
    loadNPCs();
    loadCommands();

    document.getElementById('next-turn-btn').addEventListener('click', nextTurn);
    document.getElementById('reset-btn').addEventListener('click', resetGame);
});

// ゲーム状態を読み込み
async function loadGameState() {
    try {
        const response = await fetch(`${API_BASE}/state`);
        gameState = await response.json();
        updateUI();
    } catch (error) {
        console.error('ゲーム状態の読み込みエラー:', error);
    }
}

// NPCリストを読み込み
async function loadNPCs() {
    try {
        const response = await fetch(`${API_BASE}/npcs`);
        allNPCs = await response.json();
        renderNPCList();
    } catch (error) {
        console.error('NPC読み込みエラー:', error);
    }
}

// コマンドリストを読み込み
async function loadCommands() {
    try {
        const response = await fetch(`${API_BASE}/commands`);
        allCommands = await response.json();
        renderCommands();
    } catch (error) {
        console.error('コマンド読み込みエラー:', error);
    }
}

// UIを更新
function updateUI() {
    if (!gameState) return;

    // ターン
    document.getElementById('current-turn').textContent = gameState.turn;

    // 資源
    document.getElementById('resource-gold').textContent = gameState.resources.gold;
    document.getElementById('resource-population').textContent = gameState.resources.population;
    document.getElementById('resource-military').textContent = gameState.resources.military_power;
    document.getElementById('resource-diplomacy').textContent = gameState.resources.diplomatic_influence;

    // 各分野
    for (const [sector, data] of Object.entries(gameState.sectors)) {
        document.getElementById(`${sector}-level`).textContent = data.level;
        document.getElementById(`${sector}-progress`).style.width = `${data.progress}%`;

        const delegateName = data.delegated_to
            ? allNPCs.find(npc => npc.id === data.delegated_to)?.name || '不明'
            : 'なし';
        document.getElementById(`${sector}-delegate`).textContent = delegateName;
    }

    // イベントログ
    renderEventLog();
}

// イベントログをレンダリング
function renderEventLog() {
    const eventList = document.getElementById('event-list');
    eventList.innerHTML = '';

    if (gameState.event_log) {
        gameState.event_log.slice().reverse().forEach(event => {
            const eventItem = document.createElement('div');
            eventItem.className = 'event-item';
            eventItem.textContent = event;
            eventList.appendChild(eventItem);
        });
    }
}

// NPCリストをレンダリング
function renderNPCList() {
    const container = document.getElementById('npc-list-container');
    container.innerHTML = '';

    allNPCs.forEach(npc => {
        const card = document.createElement('div');
        card.className = 'npc-card';

        const specialty = getSectorEmoji(npc.specialty);
        const personalityText = Object.entries(npc.personality)
            .map(([key, value]) => `${getPersonalityName(key)}: ${value}`)
            .join(', ');

        card.innerHTML = `
            <h4>${npc.name}</h4>
            <span class="npc-specialty">${specialty} ${getSectorName(npc.specialty)}</span>
            <div class="npc-stats">
                <div>性格: ${personalityText}</div>
                <div>忠誠度: ${npc.loyalty} | 経験値: ${npc.experience}</div>
            </div>
        `;
        container.appendChild(card);
    });
}

// コマンドをレンダリング
function renderCommands() {
    const sectors = ['economy', 'diplomacy', 'military'];

    sectors.forEach(sector => {
        const container = document.getElementById(`${sector}-commands`);
        container.innerHTML = '';

        // 委任されているかチェック
        const isDelegated = gameState && gameState.sectors[sector].delegated_to !== null;

        if (isDelegated) {
            // 委任されている場合はメッセージを表示
            const message = document.createElement('div');
            message.className = 'delegated-message';
            message.textContent = '👤 NPCに委任中 - 自動で行動します';
            container.appendChild(message);
            return;
        }

        const sectorCommands = allCommands.filter(cmd => cmd.sector === sector);

        sectorCommands.forEach(cmd => {
            const btn = document.createElement('button');
            btn.className = 'command-btn';
            btn.dataset.commandId = cmd.id;
            btn.dataset.sector = sector;
            btn.onclick = () => selectCommand(sector, cmd.id);

            const costText = Object.entries(cmd.cost)
                .map(([res, val]) => `${getResourceName(res)}: ${val}`)
                .join(', ');

            const effectText = Object.entries(cmd.effect)
                .map(([res, val]) => `${getResourceName(res)}: +${val}`)
                .join(', ');

            btn.innerHTML = `
                <h4>${cmd.name}</h4>
                <p>${cmd.description}</p>
                <div class="command-cost">コスト: ${costText}</div>
                <div class="command-effect">効果: ${effectText}</div>
            `;

            container.appendChild(btn);
        });
    });

    updateCommandButtons();
}

// コマンドボタンの有効/無効を更新
function updateCommandButtons() {
    if (!gameState) return;

    const sectors = ['economy', 'diplomacy', 'military'];

    sectors.forEach(sector => {
        const sectorCommands = allCommands.filter(cmd => cmd.sector === sector);

        sectorCommands.forEach(cmd => {
            const btn = document.querySelector(`button[data-command-id="${cmd.id}"]`);
            if (!btn) return;

            // 選択状態を反映
            if (selectedCommands[sector] === cmd.id) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }

            // リソース確認
            let canExecute = true;
            for (const [resource, cost] of Object.entries(cmd.cost)) {
                if ((gameState.resources[resource] || 0) < cost) {
                    canExecute = false;
                    break;
                }
            }

            if (canExecute) {
                btn.classList.remove('disabled');
            } else {
                btn.classList.add('disabled');
            }
        });
    });
}

// コマンドを選択
function selectCommand(sector, commandId) {
    // 委任されている場合は選択不可
    if (gameState && gameState.sectors[sector].delegated_to !== null) {
        alert('この分野はNPCに委任されています');
        return;
    }

    // 同じコマンドをクリックした場合は選択解除
    if (selectedCommands[sector] === commandId) {
        selectedCommands[sector] = null;
    } else {
        selectedCommands[sector] = commandId;
    }

    updateCommandButtons();
}

// 委任モーダルを表示
function showDelegationModal(sector) {
    currentDelegationSector = sector;
    const modal = document.getElementById('delegation-modal');
    const sectorName = getSectorName(sector);

    document.getElementById('modal-sector-name').textContent = `${getSectorEmoji(sector)} ${sectorName}分野に委任するNPCを選択`;

    const selection = document.getElementById('npc-selection');
    selection.innerHTML = '';

    // 該当分野が得意なNPCを優先表示
    const sortedNPCs = [...allNPCs].sort((a, b) => {
        if (a.specialty === sector && b.specialty !== sector) return -1;
        if (a.specialty !== sector && b.specialty === sector) return 1;
        return 0;
    });

    sortedNPCs.forEach(npc => {
        const btn = document.createElement('button');
        btn.className = 'npc-select-btn';
        btn.onclick = () => delegateToNPC(npc.id);

        const isSpecialist = npc.specialty === sector ? '⭐ ' : '';
        const personalityText = Object.entries(npc.personality)
            .map(([key, value]) => `${getPersonalityName(key)}: ${value}`)
            .join(', ');

        btn.innerHTML = `
            <h4>${isSpecialist}${npc.name}</h4>
            <div>専門: ${getSectorName(npc.specialty)}</div>
            <div>性格: ${personalityText}</div>
        `;

        selection.appendChild(btn);
    });

    modal.style.display = 'block';
}

// 委任モーダルを閉じる
function closeDelegationModal() {
    document.getElementById('delegation-modal').style.display = 'none';
    currentDelegationSector = null;
}

// NPCに委任
async function delegateToNPC(npcId) {
    if (!currentDelegationSector) return;

    try {
        const response = await fetch(`${API_BASE}/delegate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sector: currentDelegationSector,
                npc_id: npcId
            })
        });

        const result = await response.json();

        if (result.success) {
            gameState = result.state;
            // 委任した分野の選択をクリア
            selectedCommands[currentDelegationSector] = null;
            updateUI();
            renderCommands();
            closeDelegationModal();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('委任エラー:', error);
    }
}

// 次のターン
async function nextTurn() {
    try {
        // 選択されたコマンドを収集
        const playerCommands = {};
        for (const [sector, commandId] of Object.entries(selectedCommands)) {
            if (commandId !== null && gameState.sectors[sector].delegated_to === null) {
                playerCommands[sector] = commandId;
            }
        }

        const response = await fetch(`${API_BASE}/next_turn`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_commands: playerCommands })
        });

        const result = await response.json();

        if (result.success) {
            gameState = result.state;

            // 選択をクリア
            selectedCommands = {
                economy: null,
                diplomacy: null,
                military: null
            };

            updateUI();
            renderCommands();

            if (result.npc_actions && result.npc_actions.length > 0) {
                console.log('NPC実行:', result.npc_actions);
            }
            if (result.player_actions && result.player_actions.length > 0) {
                console.log('プレイヤー実行:', result.player_actions);
            }
        } else {
            alert(result.message || 'ターン進行に失敗しました');
        }
    } catch (error) {
        console.error('ターン進行エラー:', error);
        alert('ターン進行中にエラーが発生しました');
    }
}

// ゲームリセット
async function resetGame() {
    if (!confirm('ゲームをリセットしますか?')) return;

    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            gameState = result.state;
            updateUI();
            updateCommandButtons();
        }
    } catch (error) {
        console.error('リセットエラー:', error);
    }
}

// ヘルパー関数
function getSectorName(sector) {
    const names = {
        economy: '経済',
        diplomacy: '外交',
        military: '軍事'
    };
    return names[sector] || sector;
}

function getSectorEmoji(sector) {
    const emojis = {
        economy: '💰',
        diplomacy: '🤝',
        military: '⚔️'
    };
    return emojis[sector] || '📋';
}

function getResourceName(resource) {
    const names = {
        gold: '資金',
        population: '人口',
        military_power: '軍事力',
        diplomatic_influence: '外交影響力',
        progress: '進捗'
    };
    return names[resource] || resource;
}

function getPersonalityName(personality) {
    const names = {
        aggressive: '積極性',
        cautious: '慎重性',
        balanced: 'バランス'
    };
    return names[personality] || personality;
}

// NPC採用モーダルを表示
function showRecruitModal() {
    const modal = document.getElementById('recruit-modal');
    modal.style.display = 'block';
}

// NPC採用モーダルを閉じる
function closeRecruitModal() {
    document.getElementById('recruit-modal').style.display = 'none';
}

// NPCを採用
async function recruitNPC(specialty) {
    try {
        const response = await fetch(`${API_BASE}/recruit_npc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ specialty: specialty })
        });

        const result = await response.json();

        if (result.success) {
            gameState = result.state;
            allNPCs = result.all_npcs;
            updateUI();
            updateCommandButtons();
            renderNPCList();
            closeRecruitModal();

            alert(`✅ ${result.message}\n\n専門: ${getSectorName(result.npc.specialty)}\n性格: ${Object.entries(result.npc.personality).map(([k, v]) => `${getPersonalityName(k)}: ${v}`).join(', ')}`);
        } else {
            alert(`❌ ${result.message}`);
        }
    } catch (error) {
        console.error('NPC採用エラー:', error);
        alert('NPC採用中にエラーが発生しました');
    }
}
