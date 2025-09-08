"""
テスト実行時間追跡ユーティリティ
任意のassertの場所に一行差し込むだけで時間測定が可能
並列実行時の統計計算用にJSONログ出力対応
"""

import time
import threading
import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import logging

class TimeTracker:
    """
    テスト実行時間を追跡するクラス
    一行差し込むだけで使用可能
    並列実行時の統計計算用にJSONログ出力対応
    """
    
    def __init__(self, output_dir: str = "performance_logs"):
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        self._start_time: Optional[float] = None
        self._last_checkpoint: Optional[float] = None
        self._lock = threading.Lock()
        self._test_name: Optional[str] = None
        self._task_id: str = ""
        self._output_dir = output_dir
        
        # 出力ディレクトリ作成
        os.makedirs(output_dir, exist_ok=True)
        
        # タスクIDの生成（ECS環境対応）
        self._task_id = self._generate_task_id()
        
        # ログ設定
        self.logger = logging.getLogger(f"TimeTracker-{threading.current_thread().ident}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s UTC - [⏱️ TimeTracker] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _generate_task_id(self) -> str:
        """タスクIDを生成（ECS環境やローカル環境に対応）"""
        # ECS環境のタスクARNから取得
        ecs_task_arn = os.environ.get('ECS_TASK_ARN', '')
        if ecs_task_arn:
            return ecs_task_arn.split('/')[-1]
        
        # コンテナIDから取得
        container_id = os.environ.get('HOSTNAME', '')
        if container_id:
            return container_id
        
        # ローカル環境用のフォールバック
        thread_id = threading.current_thread().ident
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        return f"local_{thread_id}_{timestamp}"
    
    def start(self, test_name: str = None) -> 'TimeTracker':
        """
        時間測定を開始
        """
        with self._lock:
            self._start_time = time.time()
            self._last_checkpoint = self._start_time
            self._checkpoints.clear()
            self._test_name = test_name or "unknown_test"
            
            start_time_str = datetime.now(timezone.utc).isoformat()
            self.logger.info(f"🚀 測定開始 [{self._test_name}] - Task: {self._task_id} - {start_time_str}")
            
        return self
    
    def checkpoint(self, name: str, message: str = None) -> float:
        """
        チェックポイントを記録
        
        Args:
            name: チェックポイントの識別名
            message: 追加メッセージ
            
        Returns:
            前回のチェックポイントからの経過時間（秒）
        """
        if self._start_time is None:
            self.start()
            
        with self._lock:
            current_time = time.time()
            
            # 前回からの差分時間
            time_since_last = current_time - self._last_checkpoint
            
            # 開始からの通過時間
            total_elapsed = current_time - self._start_time
            
            # チェックポイント情報を保存
            self._checkpoints[name] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'time_since_last': time_since_last,
                'total_elapsed': total_elapsed,
                'message': message
            }
            
            # ログ出力
            msg = f"📍 {name}: +{time_since_last:.3f}s (総時間: {total_elapsed:.3f}s)"
            if message:
                msg += f" - {message}"
            self.logger.info(msg)
            
            # 最後のチェックポイント時間を更新
            self._last_checkpoint = current_time
            
            return time_since_last
    
    def get_summary(self) -> Dict[str, Any]:
        """
        測定結果のサマリーを取得
        """
        if self._start_time is None:
            return {}
            
        with self._lock:
            total_time = time.time() - self._start_time
            
            return {
                'total_execution_time': total_time,
                'checkpoints': self._checkpoints.copy(),
                'checkpoint_count': len(self._checkpoints)
            }
    
    def finish(self, test_name: str = None) -> Dict[str, Any]:
        """
        測定を終了してサマリーを出力
        JSONログファイルも生成
        """
        summary = self.get_summary()
        
        if summary:
            final_test_name = test_name or self._test_name or "unknown_test"
            self.logger.info(f"🏁 測定終了 [{final_test_name}] - 総時間: {summary['total_execution_time']:.3f}s")
            self.logger.info(f"📊 チェックポイント数: {summary['checkpoint_count']}")
            
            # JSONログファイルの生成
            self._save_json_log(final_test_name, summary)
            
        return summary
    
    def _save_json_log(self, test_name: str, summary: Dict[str, Any]):
        """JSONログファイルを保存（並列実行分析用）"""
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')[:-3]  # ミリ秒まで
            filename = f"execution_{self._task_id}_{timestamp}.json"
            filepath = os.path.join(self._output_dir, filename)
            
            # 並列実行分析用の構造化データ
            log_data = {
                'test_name': test_name,
                'task_id': self._task_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_execution_time': summary['total_execution_time'],
                'checkpoint_count': summary['checkpoint_count'],
                'checkpoints': summary['checkpoints'],
                'environment': {
                    'ecs_task_arn': os.environ.get('ECS_TASK_ARN', ''),
                    'hostname': os.environ.get('HOSTNAME', ''),
                    'python_version': os.environ.get('PYTHON_VERSION', ''),
                    'thread_id': threading.current_thread().ident
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 JSONログ保存: {filename}")
            
            # 構造化ログも出力（ログ収集システム向け）
            structured_log = {
                'event_type': 'test_execution_complete',
                'test_name': test_name,
                'task_id': self._task_id,
                'total_time': summary['total_execution_time'],
                'checkpoint_count': summary['checkpoint_count']
            }
            self.logger.info(f"📋 STRUCTURED_LOG: {json.dumps(structured_log, ensure_ascii=False)}")
            
        except Exception as e:
            self.logger.error(f"❌ JSONログ保存エラー: {e}")


# グローバルインスタンス（スレッドローカル対応）
_thread_local = threading.local()

def get_tracker(output_dir: str = "performance_logs") -> TimeTracker:
    """スレッドローカルなTimeTrackerインスタンスを取得"""
    if not hasattr(_thread_local, 'tracker'):
        _thread_local.tracker = TimeTracker(output_dir)
    return _thread_local.tracker


# 一行差し込み用の便利関数
def track(name: str, message: str = None, output_dir: str = "performance_logs") -> float:
    """
    一行差し込み用のトラッキング関数
    
    使用例:
        from tests.time_tracker import track
        
        # テスト内で
        track("login_start", "ログインページアクセス")
        # ... テストコード ...
        track("login_complete", "ログイン完了")
        # ... テストコード ...
        track("upload_start", "ファイルアップロード開始")
    
    Args:
        name: チェックポイントの識別名
        message: 追加のメッセージ
        output_dir: ログ出力ディレクトリ
        
    Returns:
        前回のチェックポイントからの経過時間（秒）
    """
    return get_tracker(output_dir).checkpoint(name, message)


def start_tracking(test_name: str = None, output_dir: str = "performance_logs") -> TimeTracker:
    """
    測定を開始
    
    使用例:
        from tests.time_tracker import start_tracking
        
        def test_something():
            start_tracking("test_something")
            # ... テストコード ...
    """
    return get_tracker(output_dir).start(test_name)


def finish_tracking(test_name: str = None, output_dir: str = "performance_logs") -> Dict[str, Any]:
    """
    測定を終了
    
    使用例:
        from tests.time_tracker import finish_tracking
        
        def test_something():
            # ... テストコード ...
            summary = finish_tracking("test_something")
    """
    return get_tracker(output_dir).finish(test_name)


def get_summary(output_dir: str = "performance_logs") -> Dict[str, Any]:
    """現在の測定サマリーを取得"""
    return get_tracker(output_dir).get_summary()


# デコレータ版
def time_test(test_name: str = None):
    """
    テスト関数全体の時間を測定するデコレータ
    
    使用例:
        from tests.time_tracker import time_test
        
        @time_test("complete_workflow")
        def test_complete_workflow(self):
            # ... テストコード ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            name = test_name or func.__name__
            start_tracking(name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                finish_tracking(name)
        return wrapper
    return decorator


# pytest用フィクスチャ
def pytest_time_tracker(request):
    """
    pytest用のフィクスチャ
    
    使用例:
        def test_something(pytest_time_tracker):
            pytest_time_tracker("step1", "最初のステップ")
            # ... テストコード ...
    """
    test_name = request.node.name
    start_tracking(test_name)
    
    def track_func(name: str, message: str = None):
        return track(name, message)
    
    yield track_func
    
    finish_tracking(test_name)
