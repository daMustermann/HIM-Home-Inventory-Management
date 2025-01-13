# Home Inventory Manager 🏠

A modern web application for managing your home inventory with an intuitive interface that works in both light and dark modes. Keep track of your items, their locations, and quantities with ease.

VERY EARLY VERSION

## Features 🚀

- 🌓 Dark/Light mode with system-wide persistence
- 🔍 Real-time search functionality
- 📸 Image upload support
- 📍 Location tracking
- 📊 Quantity management
- ✏️ Edit and update items
- 💾 Automatic SQLite database setup
- 📱 Responsive design
- 🔒 CSRF protection
- Location filtering & quick select
- AI-powered product suggestions

## Quick Start 🎯

1. Clone the repository:
```bash
git clone https://github.com/yourusername/home-inventory.git
cd home-inventory
```

2. Set up Python environment:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open http://localhost:5000 in your browser

## Docker Setup 🐳

1. Build the Docker image:
```bash
docker build -t inventory-manager .
```

2. Run the container:
```bash
docker run -p 5000:5000 inventory-app
```

## Tech Stack 💻

- **Backend**: Flask + SQLAlchemy
- **Frontend**: Bootstrap 4 + JavaScript
- **Database**: SQLite
- **Security**: Flask-WTF

## Features in Detail 📋

### Item Management
- Add items with images, descriptions, and locations
- Track quantities
- Edit existing items
- Upload item images

### Search Functionality
- Real-time search across all items
- Search by title, description, or location
- Instant results display

### Theme Support
- Switch between light and dark modes
- Theme persistence across sessions
- Smooth transition animations

## Technical Details 🔧

### Image Processing 🖼️
- Images are automatically processed on upload:
  - Converted to WebP format
  - Resized to max height of 800px
  - Aspect ratio preserved
  - PNG transparency handled
  - Quality set to 85%
  - WebP compression method 6 (best quality)
- Support for URL image imports

### AI Integration
- Google's Gemini AI for product suggestions
- Intelligent title and description generation
- Smart product categorization

### File Types
Supported image formats:
- PNG (with transparency support)
- JPG/JPEG
- GIF
- Images from URLs

## Dependencies 📦

```txt
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-WTF==1.0.0
Pillow==10.1.0
Werkzeug==2.0.1
SQLAlchemy==1.4.23
google-generativeai==0.3.0
python-dotenv==1.0.0
requests==2.31.0
```




## Configuration ⚙️

Default settings in 

config.py

:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SQLALCHEMY_DATABASE_URI = 'sqlite:///inventory.db'
```

## Dependencies 📦

```txt
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-WTF==1.0.0
Pillow==10.1.0
Werkzeug==2.0.1
SQLAlchemy==1.4.23
```

## License 📄

MIT License

---
Made with ❤️ by daMustermann
