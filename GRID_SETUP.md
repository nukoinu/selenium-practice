# Selenium Grid 並列テスト環境

Docker を使用した Selenium Grid による並列テスト環境です。20 並列での実行が可能です。

## 環境構成

- **Selenium Hub**: 1 台（ポート 4444）
- **Chrome Node**: 10 台（各 2 セッション = 20 並列）
- **Firefox Node**: 10 台（各 2 セッション = 20 並列）
- **合計**: 40 並列セッション対応

## セットアップ

### 1. 環境起動

```bash
# Selenium Grid環境を起動
docker compose --profile grid up -d

# 起動確認（60秒程度待つ）
./grid-monitor.sh status
```

### 2. Web UI での確認

- **Grid Console**: http://localhost:4444/ui
- **Grid API**: http://localhost:4444/status

## テスト実行

### 1. 基本的な並列テスト

```bash
# 20並列でテスト実行
./run-grid-tests.sh
```

### 2. 手動でのテスト実行

```bash
# Docker内でテスト実行
docker compose --profile grid exec test-runner-grid python -m pytest tests/test_parallel_grid.py -v -s -n 20 --dist loadfile

# 特定のテストのみ実行
docker compose --profile grid exec test-runner-grid python -m pytest tests/test_parallel_grid.py::TestParallelGrid::test_homepage_access -v -s -n 10
```

### 3. 負荷テスト

```bash
# デフォルト設定（20並列、5分間）
./run-load-test.sh

# カスタム設定（並列数、実行時間（秒）を指定）
./run-load-test.sh 30 600
```

## 監視

### Grid状態監視

```bash
# 現在の状態を表示
./grid-monitor.sh status

# ノード詳細情報を表示
./grid-monitor.sh nodes

# 継続監視モード
./grid-monitor.sh monitor
```

### ログ確認

```bash
# Grid Hub ログ
docker compose --profile grid logs selenium-hub

# 特定のノードログ
docker compose --profile grid logs chrome-node-1
docker compose --profile grid logs firefox-node-1

# 全ログをフォロー
docker compose --profile grid logs -f
```

## テストファイル

### `tests/test_parallel_grid.py`

並列実行対応のテストファイル：

- ✅ **TestParallelGrid**: Chrome/Firefox両対応の並列テスト
  - `test_homepage_access`: ホームページアクセステスト
  - `test_login_workflow`: ログインワークフローテスト
  - `test_invalid_login`: 無効ログインテスト
  - `test_navigation_links`: ナビゲーションテスト
  - `test_registration_page_access`: 登録ページテスト
  - `test_mypage_access_after_login`: マイページテスト

- ⚡ **TestLoadTesting**: 負荷テスト用
  - `test_concurrent_homepage_access`: 同時アクセステスト

## パフォーマンス最適化

### ノード設定の調整

各ノードのセッション数を変更する場合：

```yaml
# compose.yml内で調整
environment:
  - SE_NODE_MAX_SESSIONS=4  # デフォルト: 2
```

### 並列数の調整

```bash
# より多くの並列実行
docker compose --profile grid exec test-runner-grid python -m pytest tests/test_parallel_grid.py -v -s -n 40

# より少ない並列実行
docker compose --profile grid exec test-runner-grid python -m pytest tests/test_parallel_grid.py -v -s -n 10
```

## トラブルシューティング

### 1. Grid起動の問題

```bash
# 全てのコンテナを停止・削除
docker compose --profile grid down --remove-orphans

# 再起動
docker compose --profile grid up -d

# 状態確認
./grid-monitor.sh status
```

### 2. ノード接続の問題

```bash
# 特定のノードを再起動
docker compose --profile grid restart chrome-node-1

# ログ確認
docker compose --profile grid logs chrome-node-1
```

### 3. セッション不足

```bash
# 現在のセッション使用状況を確認
./grid-monitor.sh nodes

# セッション数を増やす（compose.yml編集後）
docker compose --profile grid up -d --scale chrome-node-1=2
```

## レポート

テスト実行後、以下のレポートが生成されます：

- `tests/report.html`: 通常テストレポート
- `tests/load_test_report.html`: 負荷テストレポート
- `performance_logs/`: パフォーマンスログ

## 従来の単体テスト

既存の単体テスト環境も利用可能：

```bash
# 従来のスタンドアロンテスト
docker compose --profile test up --abort-on-container-exit
```

## 環境停止

```bash
# Grid環境停止
docker compose --profile grid down

# 全ての環境を停止
docker compose down --remove-orphans
```
