# ProxyPolitics

🏛️ **NPC委任型内政ゲーム**

各分野（経済・外交・軍事）の政策をNPCに委任して国を発展させるブラウザゲームです。

## 特徴

- **NPC委任システム**: 各分野の政策決定をNPCキャラクターに委任できます
- **個性豊かなNPC**: NPCはそれぞれ専門分野と性格（積極的、慎重、バランス型）を持っています
- **3つの分野**: 経済、外交、軍事の各分野を管理
- **戦略的プレイ**: 自分でコマンドを選ぶか、NPCに任せるかを選択可能
- **リアルタイム進行**: ターン制で進行し、NPCが自動的に判断して行動します

## セットアップ

### 必要要件

- Python 3.8以上
- pip

### インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd ProxyPolitics
```

2. 依存パッケージをインストール
```bash
pip install -r backend/requirements.txt
```

### 起動方法

#### 通常の起動方法

1. バックエンドサーバーを起動
```bash
cd backend
python app.py
```

2. ブラウザで以下のURLにアクセス
```
http://localhost:5000
```

#### 仮想環境（venv）を使用する場合（推奨）

**Linux/macOS:**
```bash
# 初回のみ: 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install -r backend/requirements.txt

# サーバーを起動
cd backend
python app.py

# 終了時は仮想環境を無効化
deactivate
```

**Windows:**
```bash
# 初回のみ: 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
venv\Scripts\activate

# 依存パッケージをインストール
pip install -r backend\requirements.txt

# サーバーを起動
cd backend
python app.py

# 終了時は仮想環境を無効化
deactivate
```

**Note:** 2回目以降は仮想環境の有効化から始めればOKです。仮想環境が有効な状態では、コマンドプロンプトの先頭に `(venv)` と表示されます。

## ゲームの遊び方

### 基本操作

1. **コマンド実行**: 各分野のカードにあるコマンドボタンをクリックして実行
2. **NPC委任**: 各分野の「変更」ボタンからNPCを選んで委任
3. **ターン進行**: 「次のターンへ」ボタンでターンを進める（委任されたNPCが自動で行動）

### リソース

- **💰 資金**: コマンド実行に必要な主要リソース
- **👥 人口**: 国の人口（一部コマンドで消費）
- **⚔️ 軍事力**: 国の軍事的な強さ
- **🤝 外交影響力**: 外交面での影響力

### 分野

#### 💰 経済
経済発展に関するコマンド。資金を増やしたり、交易を促進したりします。

主なコマンド:
- **市場投資**: 資金を投資して経済成長
- **徴税**: 税金を徴収（人口減少のリスクあり）
- **交易促進**: 交易で収入と影響力を獲得

#### 🤝 外交
外交関係の構築。影響力を高めて国際的な地位を向上させます。

主なコマンド:
- **外交交渉**: 他国と交渉して影響力を獲得
- **同盟締結**: 大きな影響力を得る（コストも大きい）
- **文化交流**: 人口と影響力を同時に増やす

#### ⚔️ 軍事
軍事力の強化。国の防衛力を高めます。

主なコマンド:
- **兵士募集**: 人口を軍事力に転換
- **軍事訓練**: 効率的に戦力を向上
- **防衛強化**: 要塞建設で大きく防衛力アップ

### NPCシステム

各NPCは以下の特性を持ちます:

- **専門分野**: 得意な分野（経済/外交/軍事）
- **性格**:
  - **積極性**: 効果の高いコマンドを好む
  - **慎重性**: コストパフォーマンスを重視
  - **バランス**: バランス良く選択

委任されたNPCは、ターン進行時に自動的にコマンドを選択・実行します。

### デフォルトNPC

- **田中商人** (経済専門/慎重型)
- **佐藤将軍** (軍事専門/積極型)
- **鈴木外交官** (外交専門/バランス型)
- **高橋総督** (経済専門/バランス型)
- **伊藤参謀** (軍事専門/慎重型)

## 技術スタック

- **バックエンド**: Python + Flask
- **フロントエンド**: HTML + CSS + Vanilla JavaScript
- **API**: RESTful API

## プロジェクト構造

```
ProxyPolitics/
├── backend/
│   ├── app.py                  # Flaskアプリケーション
│   ├── models/
│   │   ├── game_state.py      # ゲーム状態管理
│   │   └── npc.py             # NPCモデル
│   ├── logic/
│   │   ├── command_processor.py  # コマンド処理
│   │   └── npc_ai.py             # NPCのAI判断
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── tests/
│   ├── test_game_logic.py      # ゲームロジックのテスト
│   ├── test_npc_recruitment.py # NPC採用のテスト
│   └── test_turn_based_system.py # ターンベースシステムのテスト
├── .github/
│   └── workflows/
│       └── tests.yml           # CI/CDワークフロー
└── README.md
```

## テスト

プロジェクトはpytestを使用してテストされています。

### テストの実行

```bash
# 依存パッケージをインストール（pytest含む）
pip install -r backend/requirements.txt

# 全テストを実行
pytest

# カバレッジ付きで実行
pytest --cov=backend --cov-report=term

# 詳細な出力で実行
pytest -v
```

### テストスイート

- **test_game_logic.py**: ゲームの基本ロジック、委任、コマンド実行
- **test_npc_recruitment.py**: NPC生成と採用機能
- **test_turn_based_system.py**: ターンベース選択システム

### CI/CD

プルリクエストとmainブランチへのプッシュ時に、GitHub Actionsで自動的にテストが実行されます。

- Python 3.9, 3.10, 3.11でテスト
- カバレッジレポートを生成
- テスト失敗時はマージをブロック

## API エンドポイント

- `GET /api/state` - ゲーム状態取得
- `GET /api/npcs` - NPC一覧取得
- `GET /api/commands` - コマンド一覧取得
- `POST /api/delegate` - 分野にNPCを委任
- `POST /api/execute` - コマンド実行
- `POST /api/next_turn` - 次のターンへ進行
- `POST /api/reset` - ゲームリセット

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します！

## 今後の拡張予定

- [ ] セーブ/ロード機能
- [ ] より多くのNPCとコマンド
- [ ] イベントシステム
- [ ] マルチプレイヤー対応
- [ ] NPCの成長システム
- [ ] ランダムイベント