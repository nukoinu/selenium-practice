#!/bin/bash

# Selenium Grid トラブルシューティングスクリプト

echo "🔍 Selenium Grid 診断スクリプト"
echo "=================================="

# 1. Docker環境チェック
echo "📦 Docker環境チェック:"
docker --version
docker compose version

# 2. コンテナ状態確認
echo -e "\n🐳 Grid コンテナ状態:"
docker compose --profile grid ps

# 3. Grid Hub 接続確認
echo -e "\n🌐 Grid Hub 接続確認:"
if curl -s -u admin:admin http://localhost:4444/status > /dev/null; then
    echo "✅ Grid Hub 接続成功"
    
    # ノード数とセッション数を確認
    STATUS_JSON=$(curl -s -u admin:admin http://localhost:4444/status 2>/dev/null)
    if [ -n "$STATUS_JSON" ]; then
        echo "   Grid 状態データ取得成功"
        echo "   詳細情報は Grid UI で確認: http://localhost:4444/ui"
    else
        echo "   Grid 状態データ取得失敗"
    fi
else
    echo "❌ Grid Hub 接続失敗"
fi

# 4. 写真アプリ接続確認
echo -e "\n📱 写真アプリ接続確認:"
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ 写真アプリ接続成功"
else
    echo "❌ 写真アプリ接続失敗"
fi

# 5. 簡単なテスト実行
echo -e "\n🧪 簡単なテスト実行:"
echo "単一Chromeテストを実行中..."

TEST_RESULT=$(docker compose --profile grid run --rm test-runner-grid bash -c "
    pip install -q -r requirements-test.txt 2>/dev/null && 
    python -m pytest tests/test_parallel_grid.py::TestParallelGrid::test_homepage_access[chrome] -q --tb=no 2>/dev/null
" 2>/dev/null)

if echo "$TEST_RESULT" | grep -q "1 passed"; then
    echo "✅ 基本テスト成功"
else
    echo "❌ 基本テスト失敗"
    echo "詳細なエラー確認のため、以下を実行してください:"
    echo "docker compose --profile grid logs selenium-hub"
fi

# 6. リソース使用状況
echo -e "\n💾 リソース使用状況:"
echo "メモリ使用量:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep selenium | head -5

echo -e "\n📋 診断完了"
echo "=================================="
echo "問題が発生している場合は、以下の情報をお知らせください:"
echo "1. 具体的なエラーメッセージ"
echo "2. 実行しようとしたコマンド"
echo "3. 期待される動作と実際の動作の違い"
