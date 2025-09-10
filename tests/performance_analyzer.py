"""
パフォーマンステストレポート分析ツール
並列実行時の統計計算とレポート生成機能
"""

import json
import glob
import os
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# オプショナルインポート
try:
    import matplotlib.pyplot as plt
    import pandas as pd
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False


class PerformanceAnalyzer:
    """パフォーマンステストの結果を分析するクラス"""
    
    def __init__(self, report_directory="."):
        self.report_directory = report_directory
        self.reports = []
        self.load_reports()
    
    def analyze_parallel_execution_logs(self, log_directory: str = "performance_logs") -> Dict[str, Any]:
        """
        並列実行ログを分析して統計を計算
        
        Args:
            log_directory: ログファイルが格納されているディレクトリ
            
        Returns:
            チェックポイント別統計情報
        """
        # JSONログファイルを検索
        log_files = []
        pattern = os.path.join(log_directory, "execution_*.json")
        log_files = glob.glob(pattern)
        
        if not log_files:
            print(f"⚠️  {log_directory} にexecution_*.jsonファイルが見つかりません")
            return {}
        
        print(f"📊 {len(log_files)}個のログファイルを分析中...")
        
        # 全ログファイルからデータを収集
        all_executions = []
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_executions.append(data)
                    print(f"✓ 読み込み: {os.path.basename(log_file)}")
            except Exception as e:
                print(f"❌ エラー {log_file}: {e}")
        
        if not all_executions:
            return {}
        
        return self._calculate_parallel_statistics(all_executions)
    
    def _calculate_parallel_statistics(self, execution_data: List[Dict]) -> Dict[str, Any]:
        """並列実行データの統計計算"""
        checkpoint_times = defaultdict(list)
        total_times = []
        execution_info = []
        
        # データの集約
        for execution in execution_data:
            total_time = execution.get('total_execution_time', 0)
            total_times.append(total_time)
            
            execution_info.append({
                'test_name': execution.get('test_name', 'unknown'),
                'task_id': execution.get('task_id', 'unknown'),
                'timestamp': execution.get('timestamp', ''),
                'total_time': total_time
            })
            
            checkpoints = execution.get('checkpoints', {})
            for checkpoint_name, checkpoint_data in checkpoints.items():
                if isinstance(checkpoint_data, dict):
                    time_since_last = checkpoint_data.get('time_since_last', 0)
                    total_elapsed = checkpoint_data.get('total_elapsed', 0)
                    
                    checkpoint_times[checkpoint_name].append({
                        'time_since_last': time_since_last,
                        'total_elapsed': total_elapsed,
                        'task_id': execution.get('task_id', 'unknown'),
                        'timestamp': checkpoint_data.get('timestamp', '')
                    })
        
        # 統計計算
        result = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'total_executions': len(execution_data),
            'execution_details': execution_info,
            'overall_statistics': self._calculate_time_stats(total_times),
            'checkpoint_statistics': {},
            'summary': {}
        }
        
        # 各チェックポイントの統計
        checkpoint_summary = []
        for checkpoint_name, times in checkpoint_times.items():
            time_since_last_values = [t['time_since_last'] for t in times]
            total_elapsed_values = [t['total_elapsed'] for t in times]
            
            checkpoint_stats = {
                'count': len(times),
                'time_since_last': self._calculate_time_stats(time_since_last_values),
                'total_elapsed': self._calculate_time_stats(total_elapsed_values),
                'details': times
            }
            
            result['checkpoint_statistics'][checkpoint_name] = checkpoint_stats
            
            # サマリー用
            checkpoint_summary.append({
                'name': checkpoint_name,
                'avg_time_since_last': checkpoint_stats['time_since_last'].get('mean', 0),
                'avg_total_elapsed': checkpoint_stats['total_elapsed'].get('mean', 0),
                'count': len(times)
            })
        
        # サマリー情報
        result['summary'] = {
            'avg_total_execution_time': result['overall_statistics'].get('mean', 0),
            'total_checkpoints': len(checkpoint_times),
            'checkpoints_summary': sorted(checkpoint_summary, key=lambda x: x['avg_total_elapsed'])
        }
        
        return result
    
    def _calculate_time_stats(self, times: List[float]) -> Dict[str, float]:
        """時間統計の計算"""
        if not times:
            return {'count': 0}
        
        stats = {
            'count': len(times),
            'min': min(times),
            'max': max(times),
            'sum': sum(times),
            'mean': statistics.mean(times),
            'median': statistics.median(times)
        }
        
        if len(times) > 1:
            stats['std_dev'] = statistics.stdev(times)
        else:
            stats['std_dev'] = 0
            
        return stats
    
    def generate_parallel_analysis_report(self, analysis_result: Dict[str, Any]) -> str:
        """並列実行分析結果のレポート生成"""
        if not analysis_result:
            return "分析データがありません"
        
        lines = []
        lines.append("=" * 80)
        lines.append("📊 並列実行パフォーマンス分析レポート")
        lines.append("=" * 80)
        
        # 基本情報
        lines.append(f"分析日時: {analysis_result['analysis_timestamp']}")
        lines.append(f"実行回数: {analysis_result['total_executions']}")
        
        # 全体統計
        overall = analysis_result.get('overall_statistics', {})
        if overall.get('count', 0) > 0:
            lines.append("\\n🏃 全体実行時間統計:")
            lines.append(f"  平均実行時間: {overall['mean']:.3f}秒")
            lines.append(f"  最短実行時間: {overall['min']:.3f}秒")
            lines.append(f"  最長実行時間: {overall['max']:.3f}秒")
            lines.append(f"  中央値: {overall['median']:.3f}秒")
            lines.append(f"  標準偏差: {overall['std_dev']:.3f}秒")
            lines.append(f"  合計実行時間: {overall['sum']:.3f}秒")
        
        # チェックポイント別統計サマリー
        summary = analysis_result.get('summary', {})
        checkpoints_summary = summary.get('checkpoints_summary', [])
        if checkpoints_summary:
            lines.append("\\n📍 チェックポイント別実行時間ランキング:")
            lines.append("    (累積時間の平均値順)")
            for i, cp in enumerate(checkpoints_summary, 1):
                lines.append(f"  {i:2d}. {cp['name']:<30} "
                           f"平均: {cp['avg_total_elapsed']:.3f}秒 "
                           f"(前回から: {cp['avg_time_since_last']:.3f}秒) "
                           f"実行回数: {cp['count']}")
        
        # 詳細統計
        checkpoints = analysis_result.get('checkpoint_statistics', {})
        if checkpoints:
            lines.append("\\n📊 チェックポイント詳細統計:")
            
            for checkpoint_name, stats in checkpoints.items():
                lines.append(f"\\n  📌 {checkpoint_name}")
                lines.append(f"     実行回数: {stats['count']}")
                
                # 前回からの時間統計
                since_last = stats.get('time_since_last', {})
                if since_last.get('count', 0) > 0:
                    lines.append(f"     前回からの時間:")
                    lines.append(f"       平均: {since_last['mean']:.3f}秒")
                    lines.append(f"       範囲: {since_last['min']:.3f}秒 ～ {since_last['max']:.3f}秒")
                    lines.append(f"       標準偏差: {since_last['std_dev']:.3f}秒")
                
                # 累積時間統計
                total_elapsed = stats.get('total_elapsed', {})
                if total_elapsed.get('count', 0) > 0:
                    lines.append(f"     累積時間:")
                    lines.append(f"       平均: {total_elapsed['mean']:.3f}秒")
                    lines.append(f"       範囲: {total_elapsed['min']:.3f}秒 ～ {total_elapsed['max']:.3f}秒")
                    lines.append(f"       標準偏差: {total_elapsed['std_dev']:.3f}秒")
        
        # 実行詳細
        execution_details = analysis_result.get('execution_details', [])
        if execution_details:
            lines.append("\\n🔍 実行詳細:")
            for i, detail in enumerate(execution_details, 1):
                lines.append(f"  {i:2d}. テスト: {detail['test_name']:<20} "
                           f"タスク: {detail['task_id']:<15} "
                           f"実行時間: {detail['total_time']:.3f}秒")
        
        lines.append("\\n" + "=" * 80)
        
        return "\\n".join(lines)
    
    def save_parallel_analysis(self, analysis_result: Dict[str, Any], 
                              output_dir: str = "performance_logs") -> tuple:
        """並列分析結果をファイルに保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON形式で保存
        json_filename = f"parallel_analysis_{timestamp}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        # レポート形式で保存
        report = self.generate_parallel_analysis_report(analysis_result)
        report_filename = f"parallel_report_{timestamp}.txt"
        report_filepath = os.path.join(output_dir, report_filename)
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\\n💾 分析結果を保存:")
        print(f"   JSON: {json_filepath}")
        print(f"   レポート: {report_filepath}")
        
        return json_filepath, report_filepath

    def load_reports(self):
        """パフォーマンスレポートファイルを読み込み"""
        pattern = os.path.join(self.report_directory, "performance_report_*.json")
        report_files = glob.glob(pattern)
        
        for file_path in report_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    report['file_path'] = file_path
                    self.reports.append(report)
                    print(f"レポートを読み込み: {file_path}")
            except Exception as e:
                print(f"レポート読み込みエラー {file_path}: {e}")
    
    def analyze_trends(self):
        """時系列でのパフォーマンス傾向を分析"""
        if not HAS_PLOTTING:
            print("matplotlib/pandasが利用できません。基本的な分析のみ実行します。")
            return None, None
            
        if not self.reports:
            print("分析対象のレポートがありません")
            return None, None
        
        # 全ての計測データを収集
        all_metrics = []
        for report in self.reports:
            for metric in report['metrics']:
                metric['test_session'] = report['test_session']
                all_metrics.append(metric)
        
        if not all_metrics:
            print("分析対象のメトリクスがありません")
            return None, None
        
        # DataFrameに変換
        if HAS_PLOTTING:
            df = pd.DataFrame(all_metrics)
            
            # 時間データを変換
            df['test_session'] = pd.to_datetime(df['test_session'])
            
            # アクション別の平均実行時間
            print("\\n=== アクション別平均実行時間 ===")
            action_stats = df.groupby('action')['duration'].agg(['mean', 'std', 'min', 'max', 'count'])
            print(action_stats.round(3))
            
            return df, action_stats
        else:
            # pandas無しでの基本統計
            action_stats = {}
            actions = set(m['action'] for m in all_metrics)
            
            for action in actions:
                durations = [m['duration'] for m in all_metrics if m['action'] == action]
                action_stats[action] = {
                    'mean': statistics.mean(durations),
                    'std': statistics.stdev(durations) if len(durations) > 1 else 0,
                    'min': min(durations),
                    'max': max(durations),
                    'count': len(durations)
                }
            
            print("\\n=== アクション別平均実行時間 ===")
            for action, stats in action_stats.items():
                print(f"{action}: 平均={stats['mean']:.3f}s, 標準偏差={stats['std']:.3f}s, "
                      f"最小={stats['min']:.3f}s, 最大={stats['max']:.3f}s, 回数={stats['count']}")
            
            return all_metrics, action_stats
    
    def generate_charts(self, output_dir="performance_charts"):
        """パフォーマンスチャートを生成"""
        if not HAS_PLOTTING:
            print("matplotlib/pandasが利用できないため、チャート生成をスキップします")
            return
            
        if not self.reports:
            return
        
        # 出力ディレクトリ作成
        os.makedirs(output_dir, exist_ok=True)
        
        # データ分析
        df, action_stats = self.analyze_trends()
        
        if df is None or (HAS_PLOTTING and df.empty):
            return
        
        # 1. アクション別実行時間の棒グラフ
        plt.figure(figsize=(12, 6))
        action_means = action_stats['mean'].sort_values(ascending=False)
        action_means.plot(kind='bar')
        plt.title('アクション別平均実行時間')
        plt.xlabel('アクション')
        plt.ylabel('実行時間 (秒)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'action_duration_bar.png'))
        plt.close()
        
        # 2. 時系列での実行時間推移
        if len(self.reports) > 1:
            plt.figure(figsize=(14, 8))
            
            actions = df['action'].unique()
            colors = plt.cm.Set3(range(len(actions)))
            
            for i, action in enumerate(actions):
                action_data = df[df['action'] == action]
                plt.plot(action_data['test_session'], action_data['duration'], 
                        'o-', label=action, color=colors[i], alpha=0.7)
            
            plt.title('パフォーマンス推移（時系列）')
            plt.xlabel('テスト実行時刻')
            plt.ylabel('実行時間 (秒)')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'performance_trends.png'))
            plt.close()
        
        # 3. 実行時間分布のヒストグラム
        plt.figure(figsize=(10, 6))
        for action in df['action'].unique():
            action_data = df[df['action'] == action]['duration']
            plt.hist(action_data, alpha=0.7, label=action, bins=10)
        
        plt.title('実行時間分布')
        plt.xlabel('実行時間 (秒)')
        plt.ylabel('頻度')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'duration_distribution.png'))
        plt.close()
        
        print(f"\\nパフォーマンスチャートを生成: {output_dir}/")
        print("- action_duration_bar.png: アクション別平均実行時間")
        print("- performance_trends.png: 時系列推移")
        print("- duration_distribution.png: 実行時間分布")
    
    def generate_html_report(self, output_file="performance_report.html"):
        """HTMLレポートを生成"""
        if not self.reports:
            return
        
        df, action_stats = self.analyze_trends()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>パフォーマンステストレポート</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metrics {{ margin: 20px 0; }}
        .metric-item {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .chart {{ margin: 20px 0; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 パフォーマンステストレポート</h1>
        <p>生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>分析対象レポート数: {len(self.reports)}</p>
    </div>
    
    <div class="metrics">
        <h2>📊 アクション別統計</h2>
        <table>
            <tr>
                <th>アクション</th>
                <th>平均時間(秒)</th>
                <th>標準偏差</th>
                <th>最小時間</th>
                <th>最大時間</th>
                <th>実行回数</th>
            </tr>
"""
        
        for action, stats in action_stats.iterrows():
            html_content += f"""
            <tr>
                <td>{action}</td>
                <td>{stats['mean']:.3f}</td>
                <td>{stats['std']:.3f}</td>
                <td>{stats['min']:.3f}</td>
                <td>{stats['max']:.3f}</td>
                <td>{stats['count']}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <div class="chart">
        <h2>📈 チャート</h2>
        <p>チャートファイルは performance_charts/ ディレクトリに生成されます</p>
    </div>
    
    <div class="metrics">
        <h2>🔍 推奨改善点</h2>
"""
        
        # 改善提案の生成
        slowest_actions = action_stats.nlargest(3, 'mean')
        for action, stats in slowest_actions.iterrows():
            html_content += f"""
        <div class="metric-item">
            <strong>{action}</strong>: 平均{stats['mean']:.3f}秒
            - {self._get_improvement_suggestion(action, stats['mean'])}
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTMLレポートを生成: {output_file}")
    
    def _get_improvement_suggestion(self, action, duration):
        """アクションに応じた改善提案を生成"""
        suggestions = {
            "ホームページアクセス": "ページサイズの最適化、CDN利用を検討",
            "ログインページ移動": "ページ間のナビゲーション速度改善を検討",
            "ログイン処理": "認証処理の最適化、セッション管理の見直し",
            "写真アップロード": "ファイルサイズ圧縮、非同期アップロード実装",
            "アップロード結果確認": "UIの応答性改善、プログレッシブローディング"
        }
        
        base_suggestion = suggestions.get(action, "パフォーマンス最適化を検討")
        
        if duration > 5:
            return f"要改善: {base_suggestion}"
        elif duration > 2:
            return f"改善推奨: {base_suggestion}"
        else:
            return "良好"


def main():
    """メイン実行関数"""
    analyzer = PerformanceAnalyzer()
    
    # まず並列実行ログの分析を試行
    parallel_analysis = analyzer.analyze_parallel_execution_logs("performance_logs")
    
    if parallel_analysis:
        print("📊 並列実行ログを分析しています...")
        report = analyzer.generate_parallel_analysis_report(parallel_analysis)
        print(report)
        
        # ファイルに保存
        json_path, report_path = analyzer.save_parallel_analysis(parallel_analysis)
        print(f"\\n✅ 並列実行分析完了!")
        return
    
    # 並列実行ログがない場合は通常のレポート分析
    if not analyzer.reports:
        print("⚠️  分析対象のデータが見つかりません")
        print("以下のいずれかのファイルが必要です:")
        print("  - performance_logs/execution_*.json (並列実行ログ)")
        print("  - performance_report_*.json (通常のパフォーマンスレポート)")
        print("\\nテストを実行してからこのスクリプトを実行してください")
        return
    
    print("📊 通常のパフォーマンスレポートを分析しています...")
    
    # 分析実行
    analyzer.analyze_trends()
    
    # チャート生成（matplotlibが利用可能な場合）
    try:
        analyzer.generate_charts()
    except Exception as e:
        print(f"チャート生成をスキップ: {e}")
    
    # HTMLレポート生成
    analyzer.generate_html_report()
    
    print("\\n✅ 分析完了!")


if __name__ == "__main__":
    main()
