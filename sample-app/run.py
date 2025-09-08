#!/usr/bin/env python3
"""
写真アプリケーション起動スクリプト
"""
if __name__ == '__main__':
    from app import app, db, create_default_user
    
    with app.app_context():
        # データベーステーブルを作成
        db.create_all()
        # デフォルトユーザーを作成
        create_default_user()
    
    # Waitressサーバーで起動
    from waitress import serve
    print("写真アプリケーションを起動中...")
    print("ブラウザで http://localhost:8080 にアクセスしてください")
    print("デフォルトアカウント: admin / admin123")
    print("停止するには Ctrl+C を押してください")
    serve(app, host='0.0.0.0', port=8080)
