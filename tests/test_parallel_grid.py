"""
Selenium Gridを使用した並列テスト
Chrome, Firefox両対応の並列実行テスト
"""

import pytest
import time
import os
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from tests.time_tracker import track, start_tracking, finish_tracking


class TestParallelGrid:
    """Selenium Gridでの並列テストクラス"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, browser_type):
        """テストの前後処理"""
        # Selenium Grid URL（環境変数から取得）
        selenium_grid_url = os.environ.get('SELENIUM_GRID_URL', 'http://admin:admin@localhost:4444/wd/hub')
        
        # ブラウザオプションの設定
        if browser_type == "chrome":
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
        else:  # firefox
            options = FirefoxOptions()
            options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        
        # Remote WebDriverを使用
        print(f"🔗 Selenium Grid URL: {selenium_grid_url}")
        print(f"🌐 ブラウザ: {browser_type}")
        
        self.driver = webdriver.Remote(
            command_executor=selenium_grid_url,
            options=options
        )
        
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(30)
        
        # ベースURL設定（環境変数から取得）
        self.base_url = os.environ.get('PHOTO_APP_URL', 'http://localhost:8080')
        
        # テスト識別子
        self.test_id = str(uuid.uuid4())[:8]
        print(f"🆔 テストID: {self.test_id}")
        
        yield
        
        # テスト終了後の処理
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"WebDriver終了エラー: {e}")

    @pytest.mark.parametrize("browser_type", ["chrome", "firefox"])
    def test_homepage_access(self, browser_type):
        """ホームページアクセステスト"""
        print(f"\\n[{self.test_id}] 🏠 ホームページアクセステスト ({browser_type})")
        
        start_tracking(f"homepage_access_{self.test_id}")
        
        # ホームページアクセス
        self.driver.get(self.base_url)
        track(f"homepage_loaded_{self.test_id}", "ホームページ読み込み完了")
        
        # ページタイトルの確認
        assert "写真アプリ" in self.driver.title
        print(f"✓ [{self.test_id}] ホームページのタイトルを確認しました")
        
        # ナビゲーションバーの存在確認
        navbar = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "nav"))
        )
        assert navbar is not None
        print(f"✓ [{self.test_id}] ナビゲーションバーが表示されています")
        
        summary = finish_tracking(f"homepage_access_{self.test_id}")
        print(f"📊 [{self.test_id}] 実行時間: {summary.get('total_execution_time', 0):.3f}秒")

    @pytest.mark.parametrize("browser_type", ["chrome", "firefox"])
    def test_login_workflow(self, browser_type):
        """ログインワークフローテスト"""
        print(f"\\n[{self.test_id}] 🔐 ログインワークフローテスト ({browser_type})")
        
        start_tracking(f"login_workflow_{self.test_id}")
        
        # ログインページへ移動
        self.driver.get(f"{self.base_url}/login")
        track(f"login_page_loaded_{self.test_id}", "ログインページ読み込み完了")
        
        # ログインフォームの確認
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        
        # ログイン実行
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        login_button.click()
        track(f"login_submitted_{self.test_id}", "ログイン情報送信完了")
        
        # ログイン成功の確認
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/mypage")
        )
        assert "/mypage" in self.driver.current_url
        print(f"✓ [{self.test_id}] ログインに成功しました")
        
        summary = finish_tracking(f"login_workflow_{self.test_id}")
        print(f"📊 [{self.test_id}] 実行時間: {summary.get('total_execution_time', 0):.3f}秒")

    @pytest.mark.parametrize("browser_type", ["chrome", "firefox"])  
    def test_invalid_login(self, browser_type):
        """無効なログイン情報でのテスト"""
        print(f"\\n[{self.test_id}] 🚫 無効ログインテスト ({browser_type})")
        
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
        time.sleep(2)  # エラーメッセージの表示を待つ
        
        # ログインページに留まることを確認
        assert "/login" in self.driver.current_url
        print(f"✓ [{self.test_id}] 無効ログインが正しく処理されました")

    @pytest.mark.parametrize("browser_type", ["chrome", "firefox"])
    def test_navigation_links(self, browser_type):
        """ナビゲーションリンクのテスト"""
        print(f"\\n[{self.test_id}] 🧭 ナビゲーションテスト ({browser_type})")
        
        # ホームページアクセス
        self.driver.get(self.base_url)
        
        # ログインリンクのテスト
        login_link = self.driver.find_element(By.LINK_TEXT, "ログイン")
        login_link.click()
        
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/login")
        )
        assert "/login" in self.driver.current_url
        print(f"✓ [{self.test_id}] ログインページへの遷移を確認")
        
        # ホームリンクのテスト
        self.driver.get(self.base_url)
        home_link = self.driver.find_element(By.LINK_TEXT, "ホーム")
        home_link.click()
        
        assert self.base_url in self.driver.current_url
        print(f"✓ [{self.test_id}] ホームページへの遷移を確認")

    @pytest.mark.parametrize("browser_type", ["chrome", "firefox"])
    def test_registration_page_access(self, browser_type):
        """登録ページアクセステスト"""
        print(f"\\n[{self.test_id}] 📝 登録ページアクセステスト ({browser_type})")
        
        # ホームページから登録ページへ
        self.driver.get(self.base_url)
        register_link = self.driver.find_element(By.LINK_TEXT, "新規登録")
        register_link.click()
        
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/register")
        )
        assert "/register" in self.driver.current_url
        
        # 登録フォームの要素確認
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        confirm_field = self.driver.find_element(By.NAME, "confirm_password")
        
        assert username_field is not None
        assert password_field is not None
        assert confirm_field is not None
        
        print(f"✓ [{self.test_id}] 登録ページと登録フォームを確認しました")

    @pytest.mark.parametrize("browser_type", ["chrome"])  # Chrome only for upload test
    def test_mypage_access_after_login(self, browser_type):
        """ログイン後のマイページアクセステスト"""
        print(f"\\n[{self.test_id}] 👤 マイページアクセステスト ({browser_type})")
        
        # ログイン
        self._login()
        
        # マイページの要素確認
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # ページタイトルの確認
        h1_element = self.driver.find_element(By.TAG_NAME, "h1")
        assert "マイページ" in h1_element.text
        
        # ファイルアップロードフォームの確認
        file_input = self.driver.find_element(By.NAME, "file")
        assert file_input is not None
        
        print(f"✓ [{self.test_id}] マイページの表示を確認しました")

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


# 負荷テスト用のクラス
class TestLoadTesting:
    """負荷テスト用のクラス"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """テストの前後処理"""
        selenium_grid_url = os.environ.get('SELENIUM_GRID_URL', 'http://admin:admin@localhost:4444/wd/hub')
        
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Remote(
            command_executor=selenium_grid_url,
            options=options
        )
        
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(30)
        self.base_url = os.environ.get('PHOTO_APP_URL', 'http://localhost:8080')
        self.test_id = str(uuid.uuid4())[:8]
        
        yield
        
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"WebDriver終了エラー: {e}")

    @pytest.mark.parametrize("iteration", range(10))
    def test_concurrent_homepage_access(self, iteration):
        """同時ホームページアクセステスト"""
        print(f"\\n[{self.test_id}] 🚀 同時アクセステスト #{iteration}")
        
        start_time = time.time()
        
        # ホームページアクセス
        self.driver.get(self.base_url)
        
        # ページロード確認
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "nav"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        print(f"✓ [{self.test_id}] アクセス #{iteration} 完了 - {load_time:.3f}秒")
        
        # パフォーマンス閾値チェック
        assert load_time < 10.0, f"ページロード時間が長すぎます: {load_time:.3f}秒"


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v", "-s", "-n", "auto"])
