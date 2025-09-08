FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# ポート8080を公開
EXPOSE 8080

# アプリケーションを起動
CMD ["python", "run.py"]
