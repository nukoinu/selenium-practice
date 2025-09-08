"""
並列実行のパフォーマンス分析デモスクリプト
複数のテスト実行ログを生成して統計分析を行う
"""

import os
import time
import random
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from tests.time_tracker import start_tracking, track, finish_tracking
from tests.performance_analyzer import PerformanceAnalyzer


def simulate_test_execution(test_id: int, base_delay: float = 0.1):
    """
    テスト実行をシミュレート
    
    Args:
        test_id: テストID
        base_delay: 基本遅延時間
    """
    test_name = f"parallel_test_{test_id}"
    
    # 測定開始
    start_tracking(test_name)
    
    # シミュレートされたテストステップ
    steps = [
        ("initialization", "初期化処理", 0.05),
        ("page_load", "ページ読み込み", 0.1),
        ("user_interaction", "ユーザー操作", 0.08),
        ("data_validation", "データ検証", 0.03),
        ("cleanup", "クリーンアップ", 0.02)
    ]
    
    for step_name, step_desc, step_delay in steps:
        track(step_name, step_desc)
        
        # ランダムな変動を加えて実際のテスト実行をシミュレート
        actual_delay = base_delay + step_delay + random.uniform(-0.02, 0.05)
        time.sleep(max(0.01, actual_delay))  # 最低10ms
    
    # 測定終了
    summary = finish_tracking(test_name)
    
    print(f"✅ テスト{test_id}完了 - 実行時間: {summary['total_execution_time']:.3f}秒")
    return summary


def run_parallel_tests(num_tests: int = 5, num_threads: int = 3):
    """
    並列テストを実行
    
    Args:
        num_tests: テスト実行回数
        num_threads: 並列スレッド数
    """
    print(f"🚀 並列テスト開始: {num_tests}回のテストを{num_threads}スレッドで実行")
    
    # パフォーマンスログディレクトリをクリア
    log_dir = "performance_logs"
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            if file.startswith("execution_"):
                os.remove(os.path.join(log_dir, file))
    
    # 並列実行
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        
        for i in range(num_tests):
            # テストごとに異なる基本遅延を設定
            base_delay = random.uniform(0.05, 0.15)
            future = executor.submit(simulate_test_execution, i + 1, base_delay)
            futures.append(future)
        
        # 全テストの完了を待機
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ テスト実行エラー: {e}")
    
    print(f"\\n🎉 全テスト完了: {len(results)}件のテストが実行されました")
    return results


def analyze_results():
    """並列実行結果を分析"""
    print("\\n📊 結果分析中...")
    
    analyzer = PerformanceAnalyzer()
    
    # 並列実行ログを分析
    analysis_result = analyzer.analyze_parallel_execution_logs("performance_logs")
    
    if analysis_result:
        # レポート生成と表示
        report = analyzer.generate_parallel_analysis_report(analysis_result)
        print(report)
        
        # ファイル保存
        json_path, report_path = analyzer.save_parallel_analysis(analysis_result)
        
        return analysis_result
    else:
        print("❌ 分析対象のデータが見つかりませんでした")
        return None


if __name__ == "__main__":
    print("🎯 並列実行パフォーマンス分析デモ")
    print("-" * 50)
    
    # 基本的な並列実行デモ
    print("\\n1️⃣ 基本的な並列実行デモ")
    run_parallel_tests(6, 3)
    analyze_results()
    
    print("\\n✨ デモ完了!")
    print("   performance_logs/ ディレクトリに詳細な分析結果が保存されました")
