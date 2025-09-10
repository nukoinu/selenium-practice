# Selenium練習プロジェクト

ChromeブラウザとSelenium Gridを使用したWebアプリケーションテスト環境です。

## 🚀 構成

- **写真アプリ** - Flask製のWebアプリケーション
- **Selenium Grid** - Chrome/Firefox ノードによる並列テスト環境（最大40並列）
- **自動テスト** - pytest + Selenium WebDriver
- **Docker環境** - 完全コンテナ化された実行環境

## 🌐 テスト環境

### 1. 従来のシンプルテスト
- スタンドアロンChrome環境での基本テスト

### 2. 🆕 Selenium Grid並列テスト (NEW!)
- **Selenium Hub**: 1台
- **Chrome Nodes**: 10台（各2セッション）
- **Firefox Nodes**: 10台（各2セッション）
- **最大40並列実行可能**

## 📋 機能テスト

- ✅ ホームページアクセス
- ✅ ログイン機能
- ✅ 無効なログイン情報のエラーハンドリング
- ✅ ログアウト機能（ドロップダウンメニュー対応）
- ✅ ナビゲーションテスト
- ✅ 登録ページアクセス
- ✅ マイページアクセス
- ⚡ 負荷テスト（同時アクセス）

## 🔧 使用方法

### シンプルテスト実行

```bash
# 従来のスタンドアロンテスト
./run-tests.sh
```

### 🆕 Selenium Grid並列テスト

```bash
# Grid環境起動とテスト実行
./run-grid-tests.sh

# Grid状態監視
./grid-monitor.sh status
./grid-monitor.sh monitor

# 負荷テスト実行
./run-load-test.sh
```

### 手動確認

```bash
# アプリのみ起動
docker compose up photo-app

# ブラウザで確認
# http://localhost:8080
# ログイン: admin / admin123

# Grid Console確認
# http://localhost:4444/ui
```

## 📁 ファイル構成

```
├── compose.yml             # Docker Compose設定（Grid対応）
├── run-tests.sh            # 従来テスト実行スクリプト
├── run-grid-tests.sh       # Grid並列テスト実行スクリプト
├── run-load-test.sh        # 負荷テスト実行スクリプト
├── grid-monitor.sh         # Grid監視スクリプト
├── GRID_SETUP.md          # Grid環境詳細ドキュメント
├── requirements-test.txt   # テスト用Python依存関係
├── sample-app/             # 写真アプリケーション
│   ├── app.py             # Flaskアプリ
│   ├── Dockerfile         # アプリ用Docker設定
│   └── templates/         # HTMLテンプレート
└── tests/
    ├── test_chrome_app.py      # Chromeテスト（従来）
    ├── test_parallel_grid.py   # Grid並列テスト（NEW!）
    ├── test_image.jpg          # テスト用画像
    └── conftest.py             # pytest設定
```

## 🎯 特徴

### 従来環境
- **高速実行** - 約3秒でテスト完了
- **シンプル構成** - Docker Composeで一発起動
- **安定動作** - Selenium Grid公式イメージ使用

### 🆕 Grid環境
- **超高速並列実行** - 20～40並列での大規模テスト
- **マルチブラウザ対応** - Chrome/Firefox同時テスト
- **負荷テスト対応** - 高負荷での動作確認
- **監視機能** - リアルタイムでの実行状況確認
- **スケーラブル** - ノード数の動的調整可能

## 📊 パフォーマンス

### 従来環境
- 単一テスト: ~3秒
- 全テスト: ~15秒

### Grid環境
- 20並列: ~5秒（従来の1/3の時間）
- 40並列: ~3秒（最大性能）
- 負荷テスト: 数百同時アクセス対応

## 📖 詳細ドキュメント

- **Grid環境**: [GRID_SETUP.md](GRID_SETUP.md)
- **テスト準備**: [テスト準備.md](テスト準備.md)
