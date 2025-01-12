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
docker run -d -p 5000:5000 --name inventory inventory-manager
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

## Configuration ⚙️

Default settings in 

config.py

:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SQLALCHEMY_DATABASE_URI = 'sqlite:///inventory.db'
```

## License 📄

MIT License

---
Made with ❤️ by daMustermann