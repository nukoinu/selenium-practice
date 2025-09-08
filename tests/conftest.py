"""
pytest設定ファイル
"""

import pytest

def pytest_configure(config):
    """pytest設定"""
    # カスタムマーカーの登録
    config.addinivalue_line(
        "markers", "slow: マークのあるテストは実行に時間がかかります"
    )
    config.addinivalue_line(
        "markers", "integration: 統合テスト"
    )

def pytest_collection_modifyitems(config, items):
    """テスト収集後の処理"""
    for item in items:
        # Seleniumテストには自動的にslowマーカーを追加
        if "selenium" in item.nodeid.lower() or "test_photo_app" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.integration)
