#!/bin/bash

echo "🚀 シンプルSeleniumテスト開始..."

# アプリのみ起動
docker compose up -d photo-app

echo "⏳ アプリ起動待機..."
sleep 5

# ヘルスチェック
if ! curl -s http://localhost:8080 > /dev/null; then
    echo "❌ アプリが起動していません"
    docker compose down
    exit 1
fi

echo "✅ アプリ準備完了"

# テスト実行（ローカルホストモードで）
echo "🧪 テスト実行..."
cd /home/nukoinu/src/selenium-practice
uv run pytest tests/test_firefox_simple.py -v -s

TEST_RESULT=$?

# クリーンアップ
docker compose down

[ $TEST_RESULT -eq 0 ] && echo "🎉 テスト成功!" || echo "❌ テスト失敗"
exit $TEST_RESULT
