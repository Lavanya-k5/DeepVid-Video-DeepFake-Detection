from flask import Flask, render_template, request, redirect, url_for,send_from_directory, session, flash,jsonify
import mysql.connector
import os
from detect_faces import process_video
from extract_crops import extract_video
from pred_efficient_b0 import main as predict_main
import cv2
from mysql.connector import MySQLConnection, Error
from mysql.connector.cursor import MySQLCursorDict

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'deepfake'
}

@app.route('/clear_flask_messages', methods=['POST'])
def clear_flask_messages():
    session.pop('_flashes', None)
    return jsonify({'success': True}), 200

# Initialize database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Route to check database connection
@app.route('/check_db_connection')
def check_db_connection():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Cannot connect to the database. Please try again.'})

def get_video_properties(video_path):
    cap = cv2.VideoCapture(video_path)# Open video file
    if cap.isOpened():
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))# Get total frames
        frame_rate = cap.get(cv2.CAP_PROP_FPS) # Get frame rate
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Get video dimensions (width x height)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        duration = total_frames / frame_rate      # Get video duration (in seconds)
        size_bytes = os.path.getsize(video_path)  # Get video size (in bytes)
        size_mb = size_bytes / (1024 * 1024)  # Convert size to human-readable format- Convert bytes to MB
        cap.release()    # Close video file

        return {
            'duration': round(duration, 2),
            'frame_rate': round(frame_rate, 2),
            'total_frames': total_frames,
            'width': width,
            'height': height,
            'size_mb': round(size_mb, 2)
        }
    else:
        cap.release()
        return None
    
def frames_exist(frames_path):
    # Check if the frames directory exists and contains at least one file
    return os.path.exists(frames_path) and any(os.scandir(frames_path))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if 'email' in session:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_class=MySQLCursorDict)
        cursor.execute("SELECT * FROM user_details WHERE user_type = 'User'")
        users = cursor.fetchall()
        conn.close()
        return render_template('admin.html', users=users)
    else:
        return redirect(url_for('login'))

@app.route('/delete_user/<email>', methods=['POST'])
def delete_user(email):
    if 'email' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_details WHERE Email_Id = %s", (email,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        # Attempt to establish a database connection
        conn = get_db_connection()
        if conn is None:
            flash('Cannot connect to the database. Please try again.')
            #return redirect(url_for('login'))
        cursor = conn.cursor(cursor_class=MySQLCursorDict)
        cursor.execute("SELECT * FROM user_details WHERE Email_Id = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['email'] = email
            if user['User_Type'] == 'Admin':  # Check if the user is an admin
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            flash('Cannot connect to the database. Please try again later.')
            return redirect(url_for('signup'))
        cursor = conn.cursor(cursor_class=MySQLCursorDict)
        # Check if the email already exists
        cursor.execute("SELECT * FROM user_details WHERE email_id = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            flash('Email already exists. \nPlease use a different email address.')
            return redirect(url_for('signup'))
        #cursor.execute("INSERT INTO user_details (Email_Id, password) VALUES (%s, %s)", (email, password))
        cursor.execute("INSERT INTO user_details (Email_Id, password, user_type) VALUES (%s, %s, %s)", (email, password, 'User'))
        conn.commit()
        conn.close()
        
        #session['email'] = email
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'email' not in session:
        flash('Please login to upload a video')
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            frames_per_video = request.form.get('frames_per_video')
            if not frames_per_video:
                frames_per_video = 5
            else:
                frames_per_video = int(frames_per_video) 

            video_folder = os.path.splitext(filename)[0]
            frames_path = os.path.join(app.config['UPLOAD_FOLDER'], video_folder)

            if not frames_exist(frames_path):
                process_video(file_path, app.config['UPLOAD_FOLDER'], "FacenetDetector")
                extract_video(file_path, app.config['UPLOAD_FOLDER'], app.config['UPLOAD_FOLDER'])
                
            model_path = "pre_trained_models/efficient_vit.pth"
            config_path = "configs/architecture.yaml"
            output_dir = "results/output"
            efficient_net = 0

            prediction = predict_main(frames_path, model_path, config_path, output_dir, frames_per_video, efficient_net)
            if prediction is None:  # No faces detected
                return redirect(url_for('results', {"no_faces": True}))
            return redirect(url_for('results', video=filename, prediction=prediction, video_folder=video_folder))
    return render_template('upload.html')

@app.route('/result', methods=['GET'])
def results():
    video = request.args.get('video')
    prediction = request.args.get('prediction')
    video_folder = request.args.get('video_folder')
    video_filename = os.path.basename(video)

    frames_path = os.path.join(app.config['UPLOAD_FOLDER'], "output", video_folder, "frames")
    frames = os.listdir(frames_path)

    faces_path = os.path.join(app.config['UPLOAD_FOLDER'], "output", video_folder, "faces")
    faces = os.listdir(faces_path)
    
    # Get video properties
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video)
    video_properties = get_video_properties(video_path)

    return render_template('result.html',
                            video=video_filename, prediction=prediction, frames=frames,faces=faces, 
                            frames_path=frames_path,faces_path=faces_path, video_folder=video_folder,
                              video_properties=video_properties)

@app.route('/results/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)