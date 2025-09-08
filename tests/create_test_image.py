#!/usr/bin/env python3
"""
テスト用の画像ファイルを作成するスクリプト
"""

def create_test_image():
    # 簡単なJPEGファイルのヘッダーを作成
    # 実際の画像データではないが、ファイルアップロードのテストには十分
    jpeg_header = bytes([
        0xFF, 0xD8,  # JPEG開始マーカー
        0xFF, 0xE0,  # APP0セグメント
        0x00, 0x10,  # セグメント長
        0x4A, 0x46, 0x49, 0x46, 0x00,  # "JFIF"
        0x01, 0x01,  # バージョン
        0x01,        # 密度単位
        0x00, 0x48,  # X密度
        0x00, 0x48,  # Y密度
        0x00, 0x00,  # サムネイルサイズ
        0xFF, 0xD9   # JPEG終了マーカー
    ])
    
    with open('test_image.jpg', 'wb') as f:
        f.write(jpeg_header)
    
    print('テスト用画像ファイル test_image.jpg を作成しました')

if __name__ == '__main__':
    create_test_image()
