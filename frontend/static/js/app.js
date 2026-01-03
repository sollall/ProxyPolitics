// ProxyPolitics - フロントエンドJavaScript

// グローバル変数
let gameState = {};
let allNPCs = [];
let allCommands = [];
let currentView = 'empire'; // 'empire' or 'city'
let currentSectorForDelegation = '';

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    loadGameState();
    setupEventListeners();
});

function setupEventListeners() {
    // 帝国ビューのイベント
    document.getElementById('empire-reset-btn').addEventListener('click', resetGame);

    // 都市ビューのイベント
    document.getElementById('next-turn-btn').addEventListener('click', nextTurn);
}

// ==================== ビュー切り替え ====================

function switchToEmpireView() {
    currentView = 'empire';
    document.getElementById('empire-view').classList.remove('hidden');
    document.getElementById('city-view').classList.add('hidden');
    document.getElementById('empire-view-btn').classList.add('active');
    document.getElementById('city-view-btn').classList.remove('active');
    updateEmpireView();
}

function switchToCityView(cityId = null) {
    if (cityId) {
        // 都市を切り替え
        fetch(`/api/cities/${cityId}/switch`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                gameState = data.state;
                showCityView();
            }
        });
    } else {
        showCityView();
    }
}

function showCityView() {
    currentView = 'city';
    document.getElementById('empire-view').classList.add('hidden');
    document.getElementById('city-view').classList.remove('hidden');
    document.getElementById('empire-view-btn').classList.remove('active');
    document.getElementById('city-view-btn').classList.add('active');
    updateCityView();
}

// ==================== ゲーム状態の読み込みと更新 ====================

function loadGameState() {
    Promise.all([
        fetch('/api/state').then(r => r.json()),
        fetch('/api/npcs').then(r => r.json()),
        fetch('/api/commands').then(r => r.json())
    ]).then(([state, npcs, commands]) => {
        gameState = state;
        allNPCs = npcs;
        allCommands = commands;

        if (currentView === 'empire') {
            updateEmpireView();
        } else {
            updateCityView();
        }
    });
}

// ==================== 帝国ビューの更新 ====================

function updateEmpireView() {
    // ターン数
    document.getElementById('empire-turn').textContent = gameState.turn;

    // 帝国リソース
    document.getElementById('empire-gold').textContent = gameState.resources.gold;

    // 政治体制スライダー
    if (gameState.ideology) {
        const axisMapping = {
            'capital': 'capital',
            'power': 'power',
            'legitimacy': 'legitimacy',
            'power_subject': 'power-subject'
        };

        Object.entries(axisMapping).forEach(([dataKey, htmlKey]) => {
            const slider = document.getElementById(`ideology-${htmlKey}`);
            const valueDisplay = document.getElementById(`${htmlKey}-value`);
            if (slider && valueDisplay && gameState.ideology[dataKey] !== undefined) {
                slider.value = gameState.ideology[dataKey];
                valueDisplay.textContent = gameState.ideology[dataKey];
            }
        });
    }

    // 体制分類
    if (gameState.regime) {
        const regimeNameEl = document.getElementById('regime-name');
        if (regimeNameEl) {
            regimeNameEl.textContent = gameState.regime;
        }
    }

    // 市場政策チェックボックス
    if (gameState.market_policies) {
        Object.entries(gameState.market_policies).forEach(([policy, isActive]) => {
            const checkbox = document.getElementById(`policy-${policy}`);
            if (checkbox) {
                checkbox.checked = isActive;
            }
        });
    }

    // 権力政策チェックボックス
    if (gameState.power_policies) {
        Object.entries(gameState.power_policies).forEach(([policy, isActive]) => {
            const checkbox = document.getElementById(`power-policy-${policy}`);
            if (checkbox) {
                checkbox.checked = isActive;
            }
        });
    }

    // 都市リスト
    updateCitiesList();

    // 地図を更新
    updateEmpireMap();

    // NPC一覧
    updateEmpireNPCList();

    // イベントログ
    updateEmpireEventLog();
}

function updateCitiesList() {
    const citiesList = document.getElementById('cities-list');
    citiesList.innerHTML = '';

    for (const [cityId, city] of Object.entries(gameState.cities)) {
        const cityCard = document.createElement('div');
        cityCard.className = 'city-card';
        cityCard.onclick = () => switchToCityView(cityId);

        cityCard.innerHTML = `
            <h4>${city.name}</h4>
            <div class="city-card-info">
                <div>👥 人口: ${city.resources.population}</div>
                <div>⚔️ 軍事力: ${city.resources.military_power}</div>
                <div>🤝 外交影響力: ${city.resources.diplomatic_influence}</div>
            </div>
        `;

        citiesList.appendChild(cityCard);
    }
}

function updateEmpireMap() {
    const mapContainer = document.getElementById('map-cities');
    mapContainer.innerHTML = '';

    const cityEntries = Object.entries(gameState.cities);
    const numCities = cityEntries.length;

    cityEntries.forEach(([cityId, city], index) => {
        // 都市の位置を計算（円形に配置）
        let x, y;
        if (numCities === 1) {
            // 首都のみの場合は中央に配置
            x = 400;
            y = 250;
        } else {
            // 複数の都市は円形に配置
            const angle = (index / numCities) * 2 * Math.PI - Math.PI / 2;
            const radius = 180;
            x = 400 + Math.cos(angle) * radius;
            y = 250 + Math.sin(angle) * radius;
        }

        // 都市グループを作成
        const cityGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        cityGroup.setAttribute('class', 'map-city');
        cityGroup.setAttribute('data-city-id', cityId);
        cityGroup.style.cursor = 'pointer';

        // クリックイベント
        cityGroup.onclick = () => switchToCityView(cityId);

        // 都市マーカー（外側の円）
        const outerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        outerCircle.setAttribute('cx', x);
        outerCircle.setAttribute('cy', y);
        outerCircle.setAttribute('r', '25');
        outerCircle.setAttribute('fill', '#667eea');
        outerCircle.setAttribute('opacity', '0.3');
        outerCircle.setAttribute('class', 'city-marker-outer');

        // 都市マーカー（内側の円）
        const innerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        innerCircle.setAttribute('cx', x);
        innerCircle.setAttribute('cy', y);
        innerCircle.setAttribute('r', '15');
        innerCircle.setAttribute('fill', '#667eea');
        innerCircle.setAttribute('class', 'city-marker-inner');

        // 都市名テキスト
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', x);
        text.setAttribute('y', y + 40);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('class', 'city-label');
        text.textContent = city.name;

        // 人口表示
        const popText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        popText.setAttribute('x', x);
        popText.setAttribute('y', y + 55);
        popText.setAttribute('text-anchor', 'middle');
        popText.setAttribute('class', 'city-population');
        popText.textContent = `👥 ${city.resources.population}`;

        cityGroup.appendChild(outerCircle);
        cityGroup.appendChild(innerCircle);
        cityGroup.appendChild(text);
        cityGroup.appendChild(popText);
        mapContainer.appendChild(cityGroup);
    });
}

function updateEmpireNPCList() {
    const npcList = document.getElementById('empire-npc-list');
    npcList.innerHTML = '';

    allNPCs.forEach(npc => {
        const npcCard = document.createElement('div');
        npcCard.className = 'npc-card';

        const personalityText = Object.entries(npc.personality)
            .map(([key, value]) => `${key}: ${value}`)
            .join(', ');

        npcCard.innerHTML = `
            <div class="npc-card-name">${npc.name}</div>
            <div class="npc-card-specialty">${getSpecialtyName(npc.specialty)}</div>
            <div class="npc-card-personality">${personalityText}</div>
        `;

        npcList.appendChild(npcCard);
    });
}

function updateEmpireEventLog() {
    const eventList = document.getElementById('empire-event-list');
    eventList.innerHTML = '';

    gameState.event_log.forEach(event => {
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        eventItem.textContent = event;
        eventList.appendChild(eventItem);
    });
}

// ==================== 都市ビューの更新 ====================

function updateCityView() {
    const currentCity = gameState.cities[gameState.current_city_id];
    if (!currentCity) return;

    // 都市名
    document.getElementById('city-name').textContent = currentCity.name;

    // ターン数
    document.getElementById('city-turn').textContent = gameState.turn;

    // リソース
    document.getElementById('city-gold').textContent = gameState.resources.gold;
    document.getElementById('resource-population').textContent = currentCity.resources.population;
    document.getElementById('resource-military').textContent = currentCity.resources.military_power;
    document.getElementById('resource-diplomacy').textContent = currentCity.resources.diplomatic_influence;

    // 各分野
    ['economy', 'diplomacy', 'military'].forEach(sector => {
        const sectorData = currentCity.sectors[sector];
        document.getElementById(`${sector}-level`).textContent = sectorData.level;
        document.getElementById(`${sector}-progress`).style.width = `${sectorData.progress}%`;

        const delegateName = sectorData.delegated_to
            ? allNPCs.find(npc => npc.id === sectorData.delegated_to)?.name || '不明'
            : 'なし';
        document.getElementById(`${sector}-delegate`).textContent = delegateName;

        // コマンド選択を更新
        updateCommandSelect(sector, sectorData.delegated_to);
    });

    // イベントログ
    updateCityEventLog();
}

function updateCommandSelect(sector, delegated_to) {
    const select = document.getElementById(`${sector}-command`);
    select.innerHTML = '<option value="">コマンドを選択...</option>';

    // 委任されている場合は無効化
    if (delegated_to) {
        select.disabled = true;
        select.innerHTML = '<option value="">委任中</option>';
        return;
    }

    select.disabled = false;
    const sectorCommands = allCommands.filter(cmd => cmd.sector === sector);
    sectorCommands.forEach(cmd => {
        const option = document.createElement('option');
        option.value = cmd.id;
        option.textContent = `${cmd.name} (${formatCost(cmd.cost)})`;
        select.appendChild(option);
    });
}

function updateCityEventLog() {
    const eventList = document.getElementById('city-event-list');
    eventList.innerHTML = '';

    gameState.event_log.forEach(event => {
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        eventItem.textContent = event;
        eventList.appendChild(eventItem);
    });
}

// ==================== ターン進行 ====================

function nextTurn() {
    const playerCommands = {};

    // 各分野の選択されたコマンドを取得
    ['economy', 'diplomacy', 'military'].forEach(sector => {
        const select = document.getElementById(`${sector}-command`);
        if (select.value) {
            playerCommands[sector] = select.value;
        }
    });

    fetch('/api/next_turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_commands: playerCommands })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data.state;
            updateCityView();

            // 選択をクリア
            ['economy', 'diplomacy', 'military'].forEach(sector => {
                const select = document.getElementById(`${sector}-command`);
                if (!select.disabled) {
                    select.value = '';
                }
            });
        }
    });
}

// ==================== NPC委任 ====================

function showDelegateModal(sector) {
    currentSectorForDelegation = sector;
    const modal = document.getElementById('delegate-modal');
    const npcList = document.getElementById('npc-list');
    npcList.innerHTML = '';

    // 委任解除ボタン
    const undelegateBtn = document.createElement('button');
    undelegateBtn.className = 'btn btn-secondary';
    undelegateBtn.textContent = '委任解除';
    undelegateBtn.onclick = () => delegateToNPC(null);
    npcList.appendChild(undelegateBtn);

    // NPC一覧
    allNPCs.forEach(npc => {
        const npcBtn = document.createElement('button');
        npcBtn.className = 'npc-option-btn';
        npcBtn.textContent = `${npc.name} (${getSpecialtyName(npc.specialty)})`;
        npcBtn.onclick = () => delegateToNPC(npc.id);
        npcList.appendChild(npcBtn);
    });

    modal.style.display = 'block';
}

function closeDelegateModal() {
    document.getElementById('delegate-modal').style.display = 'none';
}

function delegateToNPC(npcId) {
    fetch('/api/delegate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sector: currentSectorForDelegation,
            npc_id: npcId,
            city_id: gameState.current_city_id
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data.state;
            updateCityView();
            closeDelegateModal();
        }
    });
}

// ==================== 都市追加 ====================

function showAddCityModal() {
    document.getElementById('add-city-modal').style.display = 'block';
}

function closeAddCityModal() {
    document.getElementById('add-city-modal').style.display = 'none';
    document.getElementById('new-city-name').value = '';
}

function addCity() {
    const name = document.getElementById('new-city-name').value || '新しい都市';

    fetch('/api/cities/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data.state;
            updateEmpireView();
            closeAddCityModal();
        } else {
            alert(data.message);
        }
    });
}

// ==================== NPC採用 ====================

function showRecruitModal() {
    document.getElementById('recruit-modal').style.display = 'block';
}

function closeRecruitModal() {
    document.getElementById('recruit-modal').style.display = 'none';
    document.getElementById('recruit-specialty').value = '';
}

function recruitNPC() {
    const specialty = document.getElementById('recruit-specialty').value || null;

    fetch('/api/recruit_npc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ specialty: specialty })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data.state;
            allNPCs = data.all_npcs;
            updateEmpireView();
            closeRecruitModal();
        } else {
            alert(data.message);
        }
    });
}

// ==================== リセット ====================

function resetGame() {
    if (!confirm('ゲームをリセットしますか？')) return;

    fetch('/api/reset', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadGameState();
        }
    });
}

// ==================== 政治体制 ====================

function updateIdeology(axis, value) {
    // power_subject は HTML では power-subject として扱う
    const htmlKey = axis === 'power_subject' ? 'power-subject' : axis;

    // スライダーの値表示を更新
    const valueDisplay = document.getElementById(`${htmlKey}-value`);
    if (valueDisplay) {
        valueDisplay.textContent = value;
    }

    // サーバーに送信
    fetch('/api/ideology', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            axis: axis,
            value: parseInt(value)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data.state;
            updateEmpireView();
        }
    });
}

function toggleMarketPolicy(policy) {
    // サーバーに送信
    fetch('/api/market_policy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            policy: policy
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data.state;
            updateEmpireView();
        }
    });
}

function togglePowerPolicy(policy) {
    // サーバーに送信
    fetch('/api/power_policy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            policy: policy
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            gameState = data.state;
            updateEmpireView();
        }
    });
}

// ==================== ユーティリティ関数 ====================

function formatCost(cost) {
    return Object.entries(cost)
        .map(([resource, value]) => `${getResourceName(resource)} ${value}`)
        .join(', ');
}

function getResourceName(resource) {
    const names = {
        'gold': '💰',
        'population': '👥',
        'military_power': '⚔️',
        'diplomatic_influence': '🤝'
    };
    return names[resource] || resource;
}

function getSpecialtyName(specialty) {
    const names = {
        'economy': '経済',
        'diplomacy': '外交',
        'military': '軍事'
    };
    return names[specialty] || specialty;
}

// モーダルの外をクリックで閉じる
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}
