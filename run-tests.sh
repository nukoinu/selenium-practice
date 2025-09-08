#!/bin/bash

echo "🚀 高速Chrome Seleniumテスト開始..."

# 全体を起動
docker compose --profile test up -d

echo "⏳ サービス起動待機（10秒）..."
sleep 10

# テスト実行
echo "🧪 テスト実行..."
docker compose --profile test run --rm test-runner

TEST_RESULT=$?

# クリーンアップ
docker compose down

[ $TEST_RESULT -eq 0 ] && echo "🎉 テスト成功!" || echo "❌ テスト失敗"
exit $TEST_RESULT
