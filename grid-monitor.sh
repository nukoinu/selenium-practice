#!/bin/bash

# Selenium Grid監視スクリプト

echo "🔍 Selenium Grid監視スクリプト"

# Grid Hubの状態確認
check_grid_status() {
    echo "📊 Selenium Grid状態:"
    STATUS_RESPONSE=$(curl -s http://localhost:4444/status 2>/dev/null)
    if [ -n "$STATUS_RESPONSE" ]; then
        echo "✅ Grid Hub 接続成功"
        echo "詳細情報は Grid UI で確認: http://localhost:4444/ui"
    else
        echo "❌ Grid状態の取得に失敗しました"
    fi
}

# ノード詳細情報
check_nodes_detail() {
    echo "🖥️ ノード詳細情報:"
    NODES_RESPONSE=$(curl -s http://localhost:4444/status 2>/dev/null)
    if [ -n "$NODES_RESPONSE" ]; then
        echo "✅ ノード情報取得成功"
        echo "詳細情報は Grid UI で確認: http://localhost:4444/ui"
    else
        echo "❌ ノード情報の取得に失敗しました"
    fi
}

# 継続監視モード
monitor_mode() {
    echo "🔄 継続監視モードを開始（Ctrl+Cで終了）"
    while true; do
        clear
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Selenium Grid監視"
        echo "=================================="
        check_grid_status
        echo ""
        sleep 5
    done
}

# 引数に応じて実行
case "$1" in
    "status")
        check_grid_status
        ;;
    "nodes")
        check_nodes_detail
        ;;
    "monitor")
        monitor_mode
        ;;
    *)
        echo "使用方法:"
        echo "  $0 status   - Grid状態を表示"
        echo "  $0 nodes    - ノード詳細を表示"
        echo "  $0 monitor  - 継続監視モード"
        echo ""
        echo "Grid UI: http://localhost:4444"
        echo "Grid Console: http://localhost:4444/ui"
        ;;
esac
