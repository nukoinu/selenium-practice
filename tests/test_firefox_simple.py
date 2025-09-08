"""
写真アプリの高速Seleniumテスト
"""

import pytest
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager


def test_photo_app():
    """写真アプリの基本テスト"""
    print("🧪 写真アプリテストを開始...")
    
    # FirefoxOptionsの設定
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    
    # WebDriverの初期化
    print("🔧 WebDriverを初期化中...")
    service = Service(GeckoDriverManager().install())
    
    driver = None
    try:
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.implicitly_wait(5)
        driver.set_page_load_timeout(15)
        
        print("✅ WebDriverの初期化が成功しました")
        
        # 写真アプリにアクセス
        base_url = "http://localhost:8080"
        print(f"🌐 {base_url} にアクセス中...")
        driver.get(base_url)
        
        # タイトル確認
        print(f"📄 ページタイトル: {driver.title}")
        assert "写真アプリ" in driver.title
        
        # ログインページへ移動
        print("🔓 ログインページへ移動...")
        login_link = driver.find_element(By.LINK_TEXT, "ログイン")
        login_link.click()
        
        # ログイン実行
        print("👤 ログイン実行...")
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        username.send_keys("admin")
        password.send_keys("admin123")
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # マイページに移動したことを確認
        WebDriverWait(driver, 10).until(
            EC.url_contains("/mypage")
        )
        print("✅ ログイン成功、マイページに移動しました")
        
        print("🎉 写真アプリの基本テストが成功しました！")
        
    except Exception as e:
        print(f"❌ テストが失敗しました: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            print("🧹 WebDriverを終了しました")


if __name__ == "__main__":
    test_photo_app()
