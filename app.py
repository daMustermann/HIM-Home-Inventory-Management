# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from config import Config
from models import db, Item
import base64
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_
from flask_wtf.csrf import generate_csrf
from flask_wtf import FlaskForm
from PIL import Image
import io

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
        # Read the image
        image = Image.open(image_file)
        
        # Convert to RGB if needed (for PNG transparency)
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        
        # Calculate new dimensions
        aspect_ratio = image.size[0] / image.size[1]
        new_height = min(800, image.size[1])  # Updated to 800px
        new_width = int(aspect_ratio * new_height)
        
        # Resize image
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save as WebP
        webp_buffer = io.BytesIO()
        image.save(webp_buffer, format='WebP', quality=85, method=6)
        return webp_buffer.getvalue()

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
        items = Item.query.order_by(Item.created_at.desc()).paginate(page=page, per_page=10)
        return render_template('index.html', items=items, base64=base64)

    @app.route('/item/<int:item_id>')
    def item(item_id):
        item = Item.query.get_or_404(item_id)
        return render_template('item.html', item=item, base64=base64)

    @app.route('/delete/<int:item_id>', methods=['POST'])
    def delete(item_id):
        item_to_delete = Item.query.get_or_404(item_id)
        try:
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('Item deleted successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error deleting item: {e}")
            flash('Error deleting item. Please try again.', 'danger')
            return redirect(url_for('index'))

    @app.route('/search')
    def search():
        query = request.args.get('q', '')
        if query:
            items = Item.query.filter(
                or_(
                    Item.title.ilike(f'%{query}%'),
                    Item.description.ilike(f'%{query}%'),
                    Item.location.ilike(f'%{query}%')
                )
            ).all()
            return jsonify([{
                'id': item.id,
                'title': item.title,
                'location': item.location
            } for item in items])
        return jsonify([])

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

    return app


    

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')