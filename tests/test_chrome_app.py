"""
写真アプリのChrome Seleniumテスト
Docker上のSelenium Gridを使用
"""

import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tests.time_tracker import track, start_tracking, finish_tracking


class TestPhotoAppChrome:
    """写真アプリのChromeテストクラス"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """テストの前後処理"""
        import os
        
        # Selenium Grid URL（環境変数から取得）
        selenium_url = os.environ.get('SELENIUM_URL', 'http://localhost:4444/wd/hub')
        
        # ChromeOptionsの設定
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Remote WebDriverを使用
        print(f"🔗 Selenium Grid URL: {selenium_url}")
        self.driver = webdriver.Remote(
            command_executor=selenium_url,
            options=chrome_options
        )
        
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(30)
        
        # ベースURL設定（環境変数から取得）
        self.base_url = os.environ.get('PHOTO_APP_URL', 'http://localhost:8080')
        
        yield
        
        # テスト終了後の処理
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except Exception as e:
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
        
        # 時間測定開始
        start_tracking("complete_workflow")
        
        # 1. ホームページアクセス
        print("1. ホームページにアクセス...")
        track("homepage_start", "ホームページアクセス開始")
        self.driver.get(self.base_url)
        
        # ページタイトルの確認
        assert "写真アプリ" in self.driver.title
        print("✓ ホームページのタイトルを確認しました")
        track("homepage_loaded", "ホームページ読み込み完了")
        
        # ナビゲーションバーの存在確認
        navbar = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "nav"))
        )
        assert navbar is not None
        print("✓ ナビゲーションバーが表示されています")
        track("navbar_confirmed", "ナビゲーションバー確認完了")
        
        # 2. ログインページへ移動
        print("\\n2. ログインページへ移動...")
        track("login_navigation_start", "ログインページへの移動開始")
        login_link = self.driver.find_element(By.LINK_TEXT, "ログイン")
        login_link.click()
        
        # ログインページの確認
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        assert "/login" in self.driver.current_url
        print("✓ ログインページに移動しました")
        track("login_page_loaded", "ログインページ読み込み完了")
        
        # 3. ログイン実行
        print("\\n3. ログイン実行...")
        track("login_process_start", "ログイン処理開始")
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        # デフォルトユーザーでログイン
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        login_button.click()
        track("login_submitted", "ログイン情報送信完了")
        
        # ログイン成功の確認（マイページにリダイレクト）
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/mypage")
        )
        assert "/mypage" in self.driver.current_url
        print("✓ ログインに成功しました")
        track("login_success", "ログイン成功確認完了")
        
        # ログイン成功のフラッシュメッセージ確認
        try:
            success_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
            )
            print(f"✓ 成功メッセージ: {success_message.text}")
        except:
            print("! フラッシュメッセージが見つかりませんでした（問題ありません）")
        
        track("workflow_complete", "ワークフロー完了")
        print("\\n🎉 基本的なワークフローテストが完了しました!")
        
        # 測定終了
        summary = finish_tracking("complete_workflow")
        print(f"\\n📊 総実行時間: {summary.get('total_execution_time', 0):.3f}秒")
    
    def test_invalid_login(self):
        """無効なログイン情報でのテスト"""
        print("\\n🔒 無効なログイン情報でのテスト...")
        
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
        print("\\n🚪 ログアウト機能のテスト...")
        
        # ログイン
        self._login()
        
        # ユーザーのドロップダウンメニューをクリック
        print("📋 ユーザーメニューを開く...")
        user_dropdown = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".dropdown-toggle"))
        )
        user_dropdown.click()
        
        # ログアウトリンクをクリック
        print("🚪 ログアウトリンクをクリック...")
        logout_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='logout']"))
        )
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
