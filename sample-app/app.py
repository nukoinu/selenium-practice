import os
import uuid
from datetime import datetime
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# データベース設定
db = SQLAlchemy(app)

# ログイン管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'ログインが必要です。'

# ユーザーモデル
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    photos = db.relationship('Photo', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 写真モデル
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def resize_image(image_path, max_size=(800, 600)):
    """画像をリサイズして保存"""
    with Image.open(image_path) as img:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(image_path, optimize=True, quality=85)

# ルート設定
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('ログインしました。', 'success')
            return redirect(next_page) if next_page else redirect(url_for('mypage'))
        else:
            flash('ユーザー名またはパスワードが間違っています。', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # バリデーション
        if password != confirm_password:
            flash('パスワードが一致しません。', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('このユーザー名は既に使用されています。', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('このメールアドレスは既に登録されています。', 'error')
            return render_template('register.html')
        
        # 新しいユーザーを作成
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('アカウントが作成されました。ログインしてください。', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('home'))

@app.route('/mypage')
@login_required
def mypage():
    photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.uploaded_at.desc()).all()
    return render_template('mypage.html', photos=photos)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('ファイルが選択されていません。', 'error')
        return redirect(url_for('mypage'))
    
    file = request.files['file']
    if file.filename == '':
        flash('ファイルが選択されていません。', 'error')
        return redirect(url_for('mypage'))
    
    if file and allowed_file(file.filename):
        # ファイル名を安全にする
        original_filename = secure_filename(file.filename)
        filename = str(uuid.uuid4()) + '.' + original_filename.rsplit('.', 1)[1].lower()
        
        # アップロードディレクトリが存在しない場合は作成
        upload_dir = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # 画像をリサイズ
        try:
            resize_image(file_path)
        except Exception as e:
            flash(f'画像の処理中にエラーが発生しました: {str(e)}', 'error')
            os.remove(file_path)
            return redirect(url_for('mypage'))
        
        # データベースに保存
        photo = Photo(
            filename=filename,
            original_filename=original_filename,
            user_id=current_user.id
        )
        db.session.add(photo)
        db.session.commit()
        
        flash('写真がアップロードされました。', 'success')
    else:
        flash('許可されていないファイル形式です。', 'error')
    
    return redirect(url_for('mypage'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_dir = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_dir, filename)

@app.route('/delete_photo/<int:photo_id>')
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    
    if photo.user_id != current_user.id:
        flash('この写真を削除する権限がありません。', 'error')
        return redirect(url_for('mypage'))
    
    # ファイルを削除
    upload_dir = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
    file_path = os.path.join(upload_dir, photo.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # データベースから削除
    db.session.delete(photo)
    db.session.commit()
    
    flash('写真が削除されました。', 'success')
    return redirect(url_for('mypage'))

@app.route('/replace_photo/<int:photo_id>', methods=['POST'])
@login_required
def replace_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    
    if photo.user_id != current_user.id:
        flash('この写真を変更する権限がありません。', 'error')
        return redirect(url_for('mypage'))
    
    if 'file' not in request.files:
        flash('ファイルが選択されていません。', 'error')
        return redirect(url_for('mypage'))
    
    file = request.files['file']
    if file.filename == '':
        flash('ファイルが選択されていません。', 'error')
        return redirect(url_for('mypage'))
    
    if file and allowed_file(file.filename):
        # 古いファイルを削除
        upload_dir = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
        old_file_path = os.path.join(upload_dir, photo.filename)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
        
        # 新しいファイルを保存
        original_filename = secure_filename(file.filename)
        new_filename = str(uuid.uuid4()) + '.' + original_filename.rsplit('.', 1)[1].lower()
        new_file_path = os.path.join(upload_dir, new_filename)
        file.save(new_file_path)
        
        # 画像をリサイズ
        try:
            resize_image(new_file_path)
        except Exception as e:
            flash(f'画像の処理中にエラーが発生しました: {str(e)}', 'error')
            os.remove(new_file_path)
            return redirect(url_for('mypage'))
        
        # データベースを更新
        photo.filename = new_filename
        photo.original_filename = original_filename
        photo.uploaded_at = datetime.utcnow()
        db.session.commit()
        
        flash('写真が更新されました。', 'success')
    else:
        flash('許可されていないファイル形式です。', 'error')
    
    return redirect(url_for('mypage'))

def create_default_user():
    """デフォルトユーザーを作成"""
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('デフォルトユーザー (admin/admin123) を作成しました。')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_user()
    
    from waitress import serve
    print("サーバーを起動中... http://localhost:8080")
    serve(app, host='0.0.0.0', port=8080)
