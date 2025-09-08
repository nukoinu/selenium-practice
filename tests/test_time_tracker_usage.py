"""
時間追跡機能の使用例とテスト
"""

import pytest
import time
from tests.time_tracker import track, start_tracking, finish_tracking, time_test


class TestTimeTrackerUsage:
    """時間追跡機能の使用例"""
    
    def test_simple_tracking(self):
        """シンプルな時間追跡の例"""
        
        # 測定開始
        start_tracking("simple_test")
        
        # 各ステップで一行追加するだけ
        track("step1", "最初の処理開始")
        time.sleep(0.1)  # 何らかの処理
        assert True
        
        track("step2", "2番目の処理開始")
        time.sleep(0.2)  # 何らかの処理
        assert True
        
        track("step3", "3番目の処理開始")
        time.sleep(0.15)  # 何らかの処理
        assert True
        
        # 測定終了
        summary = finish_tracking("simple_test")
        
        # 結果確認
        assert summary['total_execution_time'] > 0.4
        assert len(summary['checkpoints']) == 3
        
        print(f"\\n📊 テスト結果:")
        print(f"   - 総実行時間: {summary['total_execution_time']:.3f}秒")
        print(f"   - チェックポイント数: {summary['checkpoint_count']}")
    
    @time_test("decorated_test")
    def test_with_decorator(self):
        """デコレータを使用した時間測定の例"""
        
        # デコレータが自動的に測定開始/終了
        track("process_start", "処理開始")
        time.sleep(0.1)
        assert True
        
        track("validation", "バリデーション")
        time.sleep(0.05)
        assert True
        
        track("cleanup", "クリーンアップ")
        time.sleep(0.03)
        assert True
    
    def test_assert_with_tracking(self):
        """assertと組み合わせた使用例"""
        
        start_tracking("assert_test")
        
        # assert文の直前に一行追加
        track("before_assertion1", "最初のアサーション前")
        assert 1 + 1 == 2
        
        track("before_assertion2", "2番目のアサーション前")
        assert "test" in "testing"
        
        track("before_assertion3", "3番目のアサーション前")
        result = [1, 2, 3]
        assert len(result) == 3
        
        track("all_assertions_complete", "全アサーション完了")
        
        summary = finish_tracking("assert_test")
        print(f"\\n✅ 全アサーション完了 - 総時間: {summary['total_execution_time']:.3f}秒")
    
    def test_conditional_tracking(self):
        """条件付き処理での使用例"""
        
        start_tracking("conditional_test")
        
        # 条件分岐での測定
        test_data = [1, 2, 3, 4, 5]
        
        track("data_preparation", "テストデータ準備完了")
        
        for i, item in enumerate(test_data):
            track(f"item_{i+1}_start", f"アイテム{item}の処理開始")
            
            if item % 2 == 0:
                # 偶数の場合
                time.sleep(0.02)
                assert item % 2 == 0
                track(f"item_{i+1}_even", f"偶数{item}の処理完了")
            else:
                # 奇数の場合
                time.sleep(0.01)
                assert item % 2 == 1
                track(f"item_{i+1}_odd", f"奇数{item}の処理完了")
        
        track("loop_complete", "ループ処理完了")
        
        summary = finish_tracking("conditional_test")
        
        # 各アイテムの処理時間を確認
        checkpoints = summary['checkpoints']
        even_items = [cp for name, cp in checkpoints.items() if 'even' in name]
        odd_items = [cp for name, cp in checkpoints.items() if 'odd' in name]
        
        print(f"\\n📈 処理結果:")
        print(f"   - 偶数処理: {len(even_items)}回")
        print(f"   - 奇数処理: {len(odd_items)}回")
        print(f"   - 総実行時間: {summary['total_execution_time']:.3f}秒")


def test_standalone_usage():
    """関数レベルでの独立した使用例"""
    
    # ファイルの先頭でimport
    # from tests.time_tracker import track, start_tracking, finish_tracking
    
    start_tracking("standalone_function")
    
    # 何らかの初期化処理
    track("initialization", "初期化処理")
    initial_data = {"status": "init"}
    assert initial_data["status"] == "init"
    
    # メイン処理
    track("main_process", "メイン処理開始")
    time.sleep(0.05)
    initial_data["status"] = "processing"
    assert initial_data["status"] == "processing"
    
    # 終了処理
    track("finalization", "終了処理")
    initial_data["status"] = "complete"
    assert initial_data["status"] == "complete"
    
    # 測定終了
    summary = finish_tracking("standalone_function")
    
    print(f"\\n🎯 独立関数テスト完了:")
    print(f"   - 実行時間: {summary['total_execution_time']:.3f}秒")
    print(f"   - チェックポイント: {summary['checkpoint_count']}個")


if __name__ == "__main__":
    # 直接実行時のテスト
    pytest.main([__file__, "-v", "-s"])
