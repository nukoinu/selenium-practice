#!/bin/bash

# 負荷テスト実行スクリプト

echo "🔥 負荷テスト実行スクリプト"

# パラメータ設定
PARALLEL_COUNT=${1:-20}
TEST_DURATION=${2:-300}  # 5分
TEST_FILE=${3:-"tests/test_parallel_grid.py::TestLoadTesting"}

echo "⚙️ テスト設定:"
echo "  並列数: $PARALLEL_COUNT"
echo "  実行時間: $TEST_DURATION 秒"
echo "  テストファイル: $TEST_FILE"

# Selenium Grid起動確認
echo "🔍 Selenium Grid状態確認..."
GRID_STATUS=$(curl -s http://localhost:4444/status 2>/dev/null)

if [ -z "$GRID_STATUS" ]; then
    echo "❌ Selenium Gridが起動していません"
    echo "先に以下を実行してください: docker compose --profile grid up -d"
    exit 1
fi

echo "✅ Selenium Grid準備完了"

# 負荷テスト実行
echo "🚀 負荷テストを開始..."
echo "開始時刻: $(date)"

docker compose --profile grid exec test-runner-grid timeout $TEST_DURATION python -m pytest \
    $TEST_FILE \
    -v -s \
    -n $PARALLEL_COUNT \
    --dist loadfile \
    --html=/app/tests/load_test_report.html \
    --self-contained-html \
    --tb=short

echo "終了時刻: $(date)"
echo "✅ 負荷テスト完了"

# 結果の確認
echo "📊 負荷テスト結果:"
echo "レポート: tests/load_test_report.html"
echo "Grid UI: http://localhost:4444/ui"
