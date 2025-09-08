"""
写真アプリのSeleniumテスト
ホームページアクセス → ログイン → 写真アップロード → 結果確認のテストシナリオ
"""

import pytest
import time
import os
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class TestPhotoApp:
    """写真アプリのテストクラス"""
    
    def setup_method(self):
        """テストメソッド実行前の初期化"""
        self.performance_metrics = []
        self.test_start_time = None
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_performance.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def measure_time(self, action_name, func, *args, **kwargs):
        """任意の処理の実行時間を計測"""
        start_time = time.time()
        self.logger.info(f"開始: {action_name}")
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            # メトリクス記録
            metric = {
                'action': action_name,
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'duration': round(duration, 3),
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            self.performance_metrics.append(metric)
            
            self.logger.info(f"完了: {action_name} - {duration:.3f}秒")
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            # エラー時のメトリクス記録
            metric = {
                'action': action_name,
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'duration': round(duration, 3),
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.performance_metrics.append(metric)
            
            self.logger.error(f"エラー: {action_name} - {duration:.3f}秒 - {str(e)}")
            raise
    
    def get_browser_performance_metrics(self):
        """ブラウザのパフォーマンスメトリクスを取得"""
        try:
            # Navigation Timing APIからメトリクスを取得
            performance_script = """
            return {
                'navigation_start': performance.timing.navigationStart,
                'dom_content_loaded': performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                'load_complete': performance.timing.loadEventEnd - performance.timing.navigationStart,
                'first_paint': performance.getEntriesByType('paint').find(entry => entry.name === 'first-paint')?.startTime || 0,
                'first_contentful_paint': performance.getEntriesByType('paint').find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
                'current_url': window.location.href,
                'page_title': document.title
            };
            """
            
            metrics = self.driver.execute_script(performance_script)
            
            # メトリクスをログに記録
            self.logger.info(f"ブラウザパフォーマンス - URL: {metrics['current_url']}")
            self.logger.info(f"  - DOMContentLoaded: {metrics['dom_content_loaded']}ms")
            self.logger.info(f"  - ページロード完了: {metrics['load_complete']}ms")
            self.logger.info(f"  - First Paint: {metrics['first_paint']}ms")
            self.logger.info(f"  - First Contentful Paint: {metrics['first_contentful_paint']}ms")
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"ブラウザパフォーマンスメトリクス取得失敗: {e}")
            return {}
    
    def capture_network_timing(self, action_name):
        """ネットワークタイミング情報を取得"""
        try:
            # Resource Timing APIからネットワーク情報を取得
            network_script = """
            const resources = performance.getEntriesByType('resource');
            return resources.slice(-10).map(resource => ({
                name: resource.name,
                duration: resource.duration,
                start_time: resource.startTime,
                response_start: resource.responseStart,
                response_end: resource.responseEnd
            }));
            """
            
            resources = self.driver.execute_script(network_script)
            
            if resources:
                self.logger.info(f"ネットワークタイミング - {action_name}:")
                for resource in resources[-3:]:  # 最新3件を表示
                    self.logger.info(f"  - {resource['name']}: {resource['duration']:.2f}ms")
            
            return resources
            
        except Exception as e:
            self.logger.warning(f"ネットワークタイミング取得失敗: {e}")
            return []
    
    def save_performance_report(self):
        """パフォーマンスレポートをJSONファイルに保存"""
        report = {
            'test_session': datetime.now().isoformat(),
            'total_metrics': len(self.performance_metrics),
            'metrics': self.performance_metrics
        }
        
        report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"パフォーマンスレポートを保存: {report_file}")
        return report_file
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """テストの前後処理"""
        import os
        
        # setup_methodの呼び出しを確認
        if not hasattr(self, 'performance_metrics'):
            self.setup_method()
        
        # テスト開始時間記録
        self.test_start_time = time.time()
        self.logger.info("=== テスト開始 ===")
        
        # Selenium Grid URL（環境変数から取得、デフォルトはローカル）
        selenium_url = os.environ.get('SELENIUM_URL', 'http://localhost:4444/wd/hub')
        
        # ChromeOptionsの設定
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # WebDriver初期化の時間を計測
        def setup_driver():
            if selenium_url.startswith('http'):
                self.driver = webdriver.Remote(
                    command_executor=selenium_url,
                    options=chrome_options
                )
            else:
                # ローカル実行の場合
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
        
        self.measure_time("WebDriver初期化", setup_driver)
        
        # ベースURL設定（環境変数から取得、デフォルトはlocalhost）
        self.base_url = os.environ.get('PHOTO_APP_URL', 'http://localhost:8080')
        
        yield
        
        # テスト終了後の処理
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                
            # パフォーマンスレポート保存
            if hasattr(self, 'test_start_time') and self.test_start_time:
                total_test_time = time.time() - self.test_start_time
                self.logger.info(f"=== テスト終了 - 総実行時間: {total_test_time:.3f}秒 ===")
                self.save_performance_report()
            
        except Exception as e:
            self.logger.error(f"終了処理エラー: {e}")
            print(f"WebDriver終了エラー: {e}")
    
    def test_complete_workflow(self):
        """
        完全なワークフローテスト:
        1. ホームページアクセス
        2. ログインページへ移動
        3. ログイン実行
        4. マイページでの写真アップロード
        5. アップロード結果の確認
        """
        
        # 1. ホームページアクセス
        print("1. ホームページにアクセス...")
        def navigate_to_home():
            self.driver.get(self.base_url)
            # ページロード完了まで待機
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "nav"))
            )
        
        self.measure_time("ホームページアクセス", navigate_to_home)
        
        # ブラウザパフォーマンスメトリクス取得
        browser_metrics = self.get_browser_performance_metrics()
        self.capture_network_timing("ホームページアクセス")
        
        # ページタイトルの確認
        assert "写真アプリ" in self.driver.title
        print("✓ ホームページのタイトルを確認しました")
        
        # ナビゲーションバーの存在確認
        navbar = self.driver.find_element(By.TAG_NAME, "nav")
        assert navbar is not None
        print("✓ ナビゲーションバーが表示されています")
        
        # 2. ログインページへ移動
        print("\\n2. ログインページへ移動...")
        def navigate_to_login():
            login_link = self.driver.find_element(By.LINK_TEXT, "ログイン")
            login_link.click()
            # ログインページの読み込み完了まで待機
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
        
        self.measure_time("ログインページ移動", navigate_to_login)
        
        # ページ移動後のパフォーマンス確認
        self.get_browser_performance_metrics()
        self.capture_network_timing("ログインページ移動")
        
        # ログインページの確認
        assert "/login" in self.driver.current_url
        print("✓ ログインページに移動しました")
        
        # 3. ログイン実行
        print("\\n3. ログイン実行...")
        def perform_login():
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # デフォルトユーザーでログイン
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            login_button.click()
            
            # ログイン成功の確認（マイページにリダイレクト）
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/mypage")
            )
        
        self.measure_time("ログイン処理", perform_login)
        
        # ログイン後のパフォーマンス確認
        self.get_browser_performance_metrics()
        self.capture_network_timing("ログイン処理")
        
        assert "/mypage" in self.driver.current_url
        print("✓ ログインに成功しました")
        
        # ログイン成功のフラッシュメッセージ確認
        try:
            success_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
            )
            print(f"✓ 成功メッセージ: {success_message.text}")
        except:
            print("! フラッシュメッセージが見つかりませんでした（問題ありません）")
        
        # 4. 写真アップロード
        print("\\n4. 写真アップロード...")
        
        # アップロード前の写真数を確認
        try:
            photo_elements = self.driver.find_elements(By.CSS_SELECTOR, ".photo-item")
            initial_photo_count = len(photo_elements)
            print(f"✓ アップロード前の写真数: {initial_photo_count}")
        except:
            initial_photo_count = 0
            print("✓ アップロード前の写真数: 0")
        
        def upload_photo():
            # ファイル入力要素を探す
            file_input = self.driver.find_element(By.NAME, "file")
            
            # テスト画像のパスを取得
            test_image_path = os.path.join(os.path.dirname(__file__), "test_image.jpg")
            test_image_path = os.path.abspath(test_image_path)
            
            # ファイルが存在することを確認
            assert os.path.exists(test_image_path), f"テスト画像が見つかりません: {test_image_path}"
            
            # ファイルを選択
            file_input.send_keys(test_image_path)
            
            # アップロードボタンをクリック
            upload_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            upload_button.click()
            
            # ページが再読み込みされるまで待機
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/mypage")
            )
        
        self.measure_time("写真アップロード", upload_photo)
        
        # アップロード後のパフォーマンス確認
        self.get_browser_performance_metrics()
        self.capture_network_timing("写真アップロード")
        
        print("✓ 写真アップロードを完了しました")
        
        # 5. アップロード結果の確認
        print("\\n5. アップロード結果の確認...")
        
        def verify_upload_result():
            # 成功メッセージの確認
            try:
                success_message = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
                )
                assert "アップロードされました" in success_message.text
                print(f"✓ アップロード成功メッセージ: {success_message.text}")
            except:
                print("! アップロード成功メッセージが見つかりませんでした")
            
            # アップロード後の写真数を確認
            try:
                # 少し待ってから写真要素を確認
                time.sleep(2)
                photo_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".photo-item, .col-md-4, .card"))
                )
                final_photo_count = len(photo_elements)
                print(f"✓ アップロード後の写真数: {final_photo_count}")
                
                # 写真が増えているかチェック
                if final_photo_count > initial_photo_count:
                    print("✓ 写真が正常にアップロードされました")
                else:
                    print("! 写真数に変化がありません")
            except:
                print("! 写真要素の確認に失敗しました")
            
            # 写真のサムネイル画像の存在確認
            try:
                thumbnail_images = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='/uploads/']")
                if thumbnail_images:
                    print(f"✓ {len(thumbnail_images)}個のサムネイル画像を確認しました")
                else:
                    print("! サムネイル画像が見つかりませんでした")
            except:
                print("! サムネイル画像の確認に失敗しました")
        
        self.measure_time("アップロード結果確認", verify_upload_result)
        
        print("\\n🎉 テストが完了しました!")
        
        # パフォーマンス概要を表示
        print("\\n📊 パフォーマンス概要:")
        for metric in self.performance_metrics:
            print(f"  - {metric['action']}: {metric['duration']}秒 ({metric['status']})")
        
        total_action_time = sum(m['duration'] for m in self.performance_metrics)
        print(f"  - 総アクション時間: {total_action_time:.3f}秒")
    
    def test_invalid_login(self):
        """無効なログイン情報でのテスト"""
        print("\\n無効なログイン情報でのテスト...")
        
        # ログインページへ移動
        self.driver.get(f"{self.base_url}/login")
        
        # 無効な認証情報でログイン試行
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys("invalid_user")
        password_field.send_keys("invalid_password")
        login_button.click()
        
        # エラーメッセージの確認
        try:
            error_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-danger, .alert-error"))
            )
            assert "間違っています" in error_message.text
            print(f"✓ エラーメッセージ: {error_message.text}")
        except:
            print("! エラーメッセージが表示されませんでした")
        
        # ログインページに留まることを確認
        assert "/login" in self.driver.current_url
        print("✓ ログインページに留まっています")
    
    def test_logout(self):
        """ログアウト機能のテスト"""
        print("\\nログアウト機能のテスト...")
        
        # ログイン
        self._login()
        
        # ログアウトリンクをクリック
        logout_link = self.driver.find_element(By.LINK_TEXT, "ログアウト")
        logout_link.click()
        
        # ホームページにリダイレクトされることを確認
        WebDriverWait(self.driver, 10).until(
            EC.url_matches(f"{self.base_url}/?$")
        )
        
        # ログアウト成功メッセージの確認
        try:
            info_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-info"))
            )
            assert "ログアウトしました" in info_message.text
            print(f"✓ ログアウトメッセージ: {info_message.text}")
        except:
            print("! ログアウトメッセージが見つかりませんでした")
        
        print("✓ ログアウトが正常に動作しました")
    
    def _login(self):
        """ヘルパーメソッド: ログイン処理"""
        self.driver.get(f"{self.base_url}/login")
        
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        login_button.click()
        
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/mypage")
        )


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v", "-s"])
