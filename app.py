from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for the session

# Define the path to the 'upload' directory
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_files(UPLOAD_FOLDER):
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.txt') or f.endswith('.csv')]  # Remove the quotes around UPLOAD_FOLDER
    return files

def file_exists(file_name):
    file_path = os.path.join('upload', file_name)
    return os.path.isfile(file_path)

# Function to read photo data from the specified file
def read_photos_from_txt(file_name):
    photos = []
    file_path = f'upload/{file_name}'  # Assuming 'upload' is your upload folder
    try:
        with open(file_path, 'r') as file:
            for index, line in enumerate(file):
                url, title, image, icon, channel = line.strip().split(',')
                photos.append({
                    'index': index + 1,
                    'url': url,
                    'title': title,
                    'image': image,
                    'icon': icon,
                    'channel': channel
                })
    except FileNotFoundError:
        return None  # Return None if the file is not found
    return photos

@app.route('/')
def index():
    # Set the default file_name to 'photos.txt' when not present in the session
    if 'file_name' not in session or not file_exists(session['file_name']):
        session['file_name'] = 'photos.txt'
    file_name = session['file_name']

    photos = read_photos_from_txt(file_name)
    num_photos = len(photos)  # Get the number of photos
    files = get_files(UPLOAD_FOLDER)
    return render_template('index.html', photos=photos, num_photos=num_photos, file_name=file_name, files=files)

# Define a route to handle form submission
@app.route('/load_photos', methods=['POST'])
def load_photos():
    # Get the user-entered file name or use 'photos.txt' as a default
    file_name = request.form.get('file_name')
    session['file_name'] = file_name  # Store the file name in the session
    return redirect(url_for('index'))  # Redirect back to the main page with the new file

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search')
    file_name = session['file_name']
    photos = read_photos_from_txt(file_name)
    results = [photo for photo in photos if search_query.lower() in photo['title'].lower()]
    return render_template('index.html', photos=results, search_query=search_query, file_name=file_name)

@app.route('/photo/<int:index>')
def display_photo(index):
    # Get the user-specified file name from the session
    file_name = session['file_name']
    
    if file_name:
        photos = read_photos_from_txt(file_name)
        if 1 <= index <= len(photos):
            photo = photos[index - 1]  # Adjust the index to match the list (0-based)
            return render_template('photo.html', photo=photo, file_name=file_name)

    return "Photo not found"

if __name__ == '__main__':
    app.run(debug=True)
