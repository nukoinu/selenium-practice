# Selenium練習プロジェクト

ChromeブラウザをDocker上で動作させるSeleniumテスト環境です。

## 🚀 構成

- **写真アプリ** - Flask製のWebアプリケーション
- **Chrome Selenium** - Docker上のHeadless Chrome
- **自動テスト** - pytest + Selenium WebDriver

## 📋 機能テスト

- ✅ ホームページアクセス
- ✅ ログイン機能
- ✅ 無効なログイン情報のエラーハンドリング
- ✅ ログアウト機能（ドロップダウンメニュー対応）

## 🔧 使用方法

### テスト実行

```bash
./run-tests.sh
```

### 手動確認

```bash
# アプリのみ起動
docker compose up photo-app

# ブラウザで確認
# http://localhost:8080
# ログイン: admin / admin123
```

## 📁 ファイル構成

```
├── compose.yml           # Docker Compose設定
├── run-tests.sh          # テスト実行スクリプト
├── requirements-test.txt # テスト用Python依存関係
├── sample-app/           # 写真アプリケーション
│   ├── app.py           # Flaskアプリ
│   ├── Dockerfile       # アプリ用Docker設定
│   └── templates/       # HTMLテンプレート
└── tests/
    ├── test_chrome_app.py  # Chromeテスト（メイン）
    ├── test_image.jpg      # テスト用画像
    └── conftest.py         # pytest設定
```

## 🎯 特徴

- **高速実行** - 約3秒でテスト完了
- **シンプル構成** - Docker Composeで一発起動
- **安定動作** - Selenium Grid公式イメージ使用
