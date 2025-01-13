# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from config import Config
from models import db, Item, Location  # Add Location import
import base64
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_
from flask_wtf.csrf import generate_csrf
from flask_wtf import FlaskForm
from PIL import Image
import io
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os
import logging  # Add near other imports
import requests
from io import BytesIO

load_dotenv()  # Add this near the top of file with other imports

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Replace with secure key
    csrf = CSRFProtect(app)
    
    db.init_app(app)

    @app.context_processor
    def utility_processor():
        return dict(csrf_token=generate_csrf)

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def process_image(image_file):
        try:
            # Read the image
            image = Image.open(image_file)
            
            # Convert to RGB if needed (for PNG transparency)
            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            
            # Calculate new dimensions
            aspect_ratio = image.size[0] / image.size[1]
            new_height = min(800, image.size[1])
            new_width = int(aspect_ratio * new_height)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to BytesIO
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logging.error(f"Image processing error: {str(e)}")
            return None

    def download_image_from_url(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BytesIO(response.content)
        except Exception as e:
            logging.error(f"Error downloading image: {str(e)}")
            return None

    def download_and_process_image_url(url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            return process_image(image_data)
        except Exception as e:
            logging.error(f"Error downloading image from URL: {str(e)}")
            return None

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            try:
                title = request.form['title']
                description = request.form['description']
                location = request.form['location']
                image_file = request.files['image']
                
                if image_file and allowed_file(image_file.filename):
                    image_data = process_image(image_file)
                else:
                    image_data = None

                quantity = int(request.form['quantity'])  # Get quantity

                new_item = Item(title=title, description=description, location=location, image=image_data)
                db.session.add(new_item)
                db.session.commit()
                flash('Item added successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                print(f"Error adding item: {e}")
                flash('Error adding item. Please try again.', 'danger')
                return redirect(url_for('index'))

        page = request.args.get('page', 1, type=int)
        location = request.args.get('location', '')
        sort = request.args.get('sort', 'date_desc')
        
        query = Item.query
        
        # Apply filters
        if location:
            query = query.filter(Item.location == location)
        
        # Apply sorting
        if sort == 'date_desc':
            query = query.order_by(Item.created_at.desc())
        elif sort == 'date_asc':
            query = query.order_by(Item.created_at.asc())
        elif sort == 'title_asc':
            query = query.order_by(Item.title.asc())
        elif sort == 'title_desc':
            query = query.order_by(Item.title.desc())
        
        # Get unique locations for filter dropdown
        locations = db.session.query(Item.location).distinct().all()
        locations = [loc[0] for loc in locations if loc[0]]
        
        items = query.paginate(page=page, per_page=10)
        return render_template('index.html', items=items, locations=locations, base64=base64)

    @app.route('/item/<int:item_id>')
    def item(item_id):
        item = Item.query.get_or_404(item_id)
        return render_template('item.html', item=item, base64=base64)

    @app.route('/delete/<int:item_id>', methods=['POST'])
    def delete_item(item_id):
        try:
            item = Item.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            flash('Item deleted successfully', 'success')
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/search')
    def search():
        query = request.args.get('q', '')
        if not query:
            return jsonify([])
            
        items = Item.query.filter(
            or_(
                Item.title.ilike(f'%{query}%'),
                Item.description.ilike(f'%{query}%'),
                Item.location.ilike(f'%{query}%')
            )
        ).limit(5).all()
        
        results = [{
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'location': item.location
        } for item in items]
        
        return jsonify(results)

    @app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
    def edit_item(item_id):
        item = Item.query.get_or_404(item_id)
        if request.method == 'POST':
            try:
                item.title = request.form['title']
                item.description = request.form['description']
                item.location = request.form['location']
                item.quantity = int(request.form['quantity'])
                
                # Add debug logging
                print("Processing image upload in edit route")
                image_file = request.files.get('image')
                if image_file and image_file.filename:
                    print(f"Image file received: {image_file.filename}")
                    if allowed_file(image_file.filename):
                        print("File type allowed, processing image")
                        image_data = process_image(image_file)
                        item.image = image_data
                        print("Image processed and saved")
                    else:
                        print(f"File type not allowed: {image_file.filename}")
                
                db.session.commit()
                flash('Item updated successfully!', 'success')
                return redirect(url_for('item', item_id=item.id))
            except Exception as e:
                print(f"Error updating item: {str(e)}")
                db.session.rollback()
                flash('Error updating item. Please try again.', 'danger')
                return redirect(url_for('edit_item', item_id=item.id))
        
        return render_template('edit_item.html', item=item)

    @app.route('/item/<int:item_id>/update_quantity', methods=['POST'])
    def update_quantity(item_id):
        item = Item.query.get_or_404(item_id)
        try:
            data = request.get_json()
            new_quantity = int(data.get('quantity', 1))
            item.quantity = new_quantity
            db.session.commit()
            return jsonify({'quantity': item.quantity})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # Configure Gemini API
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')

    @app.route('/get_suggestions', methods=['POST'])
    def get_suggestions():
        try:
            data = request.get_json()
            title = data.get('title')
            
            # Modified prompt focusing on title and description
            prompt = f"""Generate 3 detailed product suggestions for '{title}'.
            Return ONLY a JSON array with this exact structure:
            [
                {{
                    "title": "Detailed Product Name with Brand and Model",
                    "description": "Comprehensive 2-3 sentence description with key features and specifications",
                    "image_url": "https://via.placeholder.com/400x300?text=Product+Image"
                }}
            ]"""
            
            response = model.generate_content(prompt)
            raw_response = response.text.strip()
            
            # Process response and extract JSON
            start_idx = raw_response.find('[')
            end_idx = raw_response.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = raw_response[start_idx:end_idx]
                suggestions = json.loads(json_str)
                
                # Add placeholder images
                for suggestion in suggestions:
                    suggestion['image_url'] = f"https://via.placeholder.com/400x300?text={suggestion['title'].replace(' ', '+')}"
                
                return jsonify(suggestions)
                
            raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            logging.error(f"Error generating suggestions: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/add-item', methods=['GET'])
    def add_item():
        return render_template('add_item.html')

    @app.route('/add-item', methods=['POST'])
    def add_item_post():
        try:
            # Process image
            image_data = None
            if 'image' in request.files and request.files['image'].filename:
                image_file = request.files['image']
                if allowed_file(image_file.filename):
                    image_data = process_image(image_file)
            elif image_url := request.form.get('image_url'):
                if downloaded := download_image_from_url(image_url):
                    image_data = process_image(downloaded)

            # Create new item
            new_item = Item(
                title=request.form['title'],
                description=request.form.get('description', ''),
                location=request.form.get('location', ''),
                quantity=int(request.form.get('quantity', 1)),
                image=image_data
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('index')})
            else:
                flash('Item added successfully!', 'success')
                return redirect(url_for('index'))
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding item: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)}), 400
            else:
                flash(f'Error adding item: {str(e)}', 'danger')
                return redirect(url_for('add_item'))

    @app.route('/edit-item/<int:item_id>', methods=['POST'])
    def edit_item_post(item_id):
        try:
            item = Item.query.get_or_404(item_id)
            
            item.title = request.form['title']
            item.description = request.form['description']
            item.location = request.form['location']
            item.quantity = int(request.form.get('quantity', 1))
            
            # Handle image from file or URL
            if 'image' in request.files and request.files['image'].filename:
                image_file = request.files['image']
                if allowed_file(image_file.filename):
                    item.image = process_image(image_file)
            elif image_url := request.form.get('image_url'):
                if image_data := download_and_process_image_url(image_url):
                    item.image = image_data
            
            db.session.commit()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('item', item_id=item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating item: {str(e)}', 'danger')
            return redirect(url_for('edit_item', item_id=item_id))

    @app.route('/locations', methods=['GET'])
    def get_locations():
        locations = Location.query.order_by(Location.name).all()
        return jsonify([loc.name for loc in locations])

    @app.route('/locations', methods=['POST'])
    def add_location():
        data = request.get_json()
        location_name = data.get('name')
        if location_name and not Location.query.filter_by(name=location_name).first():
            location = Location(name=location_name)
            db.session.add(location)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False})

    return app

# Add logging configuration after app creation
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')