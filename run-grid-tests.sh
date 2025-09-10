#!/bin/bash

# Selenium Grid並列テスト実行スクリプト

echo "🚀 Selenium Grid並列テスト環境を起動中..."

# 古いコンテナを停止・削除
echo "📦 既存のコンテナを停止・削除中..."
docker compose --profile grid down --remove-orphans

# Selenium Grid環境を起動
echo "🌐 Selenium Grid環境を起動中..."
docker compose --profile grid up -d

echo "⏳ Selenium Gridの起動を待機中（60秒）..."
sleep 60

# Grid状態の確認
echo "🔍 Selenium Grid状態を確認中..."
curl -s http://localhost:4444/status || echo "Grid状態の取得に失敗しました"

# テスト実行
echo "🧪 並列テストを実行中（20並列）..."
docker compose --profile grid run --rm test-runner-grid python -m pytest tests/test_parallel_grid.py -v -s -n 20 --dist loadfile --html=/app/tests/report.html --self-contained-html 

# 結果の確認
echo "📊 テスト結果:"
echo "Grid UI: http://localhost:4444"
echo "Grid Console: http://localhost:4444/ui"

echo "✅ テスト実行完了"
