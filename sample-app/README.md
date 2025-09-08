# 写真アプリ

Flask + Bootstrap 5.3を使用したWebベースの写真管理アプリケーションです。

## 機能

- **ホームページ**: アプリケーションの紹介とナビゲーション
- **ユーザー認証**: ログイン・新規登録・ログアウト機能
- **マイページ**: ユーザーの写真ギャラリー
- **写真アップロード**: 画像ファイルのアップロード（自動リサイズ機能付き）
- **写真管理**: アップロード済み写真の閲覧・削除・差し替え

## 技術スタック

- **言語**: Python 3.13
- **パッケージ管理**: uv
- **フレームワーク**: Flask 3.x
- **UI**: Bootstrap 5.3
- **データベース**: SQLite
- **認証**: Flask-Login
- **画像処理**: Pillow
- **WSGIサーバー**: Waitress

## セットアップ

### 1. プロジェクトのセットアップ（uvを使用）

プロジェクトルートディレクトリ（pyproject.tomlがある場所）で以下を実行：

```bash
# 依存関係の同期（仮想環境の作成も含む）
uv sync

# 仮想環境の有効化
source .venv/bin/activate  # Linux/Mac
# または
.venv\\Scripts\\activate  # Windows
```

### 開発依存関係もインストールする場合：

```bash
# 開発用の依存関係も含めてインストール
uv sync --extra dev
```

### 2. アプリケーションの起動

sample-appディレクトリに移動してから実行：

```bash
cd sample-app
python run.py
```

または

```bash
cd sample-app
python app.py
```

### 3. ブラウザでアクセス

http://localhost:8080 にアクセスしてください。

## デフォルトアカウント

テスト用のアカウントが自動で作成されます：

- **ユーザー名**: admin
- **パスワード**: admin123

## ディレクトリ構造

```
sample-app/
├── app.py              # メインアプリケーション
├── config.py           # 設定ファイル
├── run.py              # 起動スクリプト
├── requirements.txt    # 依存関係（参考用：実際の管理はプロジェクトルートのpyproject.toml）
├── templates/          # HTMLテンプレート
│   ├── base.html      # ベーステンプレート
│   ├── home.html      # ホームページ
│   ├── login.html     # ログインページ
│   ├── register.html  # 新規登録ページ
│   └── mypage.html    # マイページ
├── static/            # 静的ファイル（CSS, JS, 画像）
└── uploads/           # アップロードされた写真の保存先
```

## 対応画像形式

- JPG/JPEG
- PNG
- GIF
- WebP

最大ファイルサイズ: 16MB

## 主な機能詳細

### 写真アップロード
- ファイル形式とサイズの自動チェック
- 画像の自動リサイズ（最大800x600px）
- 重複を避けるためのユニークファイル名生成

### 写真管理
- グリッド表示での写真一覧
- モーダルでの拡大表示
- 写真の削除機能
- 写真の差し替え機能（元の写真を新しい写真で置き換え）

### セキュリティ
- パスワードハッシュ化（Werkzeug）
- セッション管理（Flask-Login）
- ファイルアップロードの安全性チェック
- CSRF保護

## 本番環境での注意点

1. `config.py`の`SECRET_KEY`を強力なものに変更
2. データベースをSQLiteからPostgreSQLやMySQLに変更を検討
3. HTTPSの使用
4. 適切なファイルパーミッションの設定
5. リバースプロキシ（Nginx等）の使用を推奨

## ライセンス

MIT License
