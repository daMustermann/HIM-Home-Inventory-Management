# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from config import Config
from models import db, Item
import base64
from werkzeug.utils import secure_filename
from flask import jsonify
from sqlalchemy import or_

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            try:
                title = request.form['title']
                description = request.form['description']
                location = request.form['location']
                image_file = request.files['image']
                
                if image_file and allowed_file(image_file.filename):
                    image_data = image_file.read()
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

    @app.route('/search')  # Moved inside create_app()
    def search():
        query = request.args.get('query', '')
        if not query:
            return jsonify([])
        
        # Search in both title and description
        search_query = f"%{query}%"
        items = Item.query.filter(
            or_(
                Item.title.ilike(search_query),
                Item.description.ilike(search_query),
                Item.location.ilike(search_query)
            )
        ).limit(10).all()
    
        results = []
        for item in items:
            results.append({
                'id': item.id,
                'title': item.title,
                'description': item.description[:100] + '...' if item.description and len(item.description) > 100 else item.description,
                'location': item.location
            })
    
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
                image_file = request.files['image']
                if image_file:
                    item.image = image_file.read()
                db.session.commit()
                flash('Item updated successfully!', 'success')
                return redirect(url_for('item', item_id=item.id))
            except Exception as e:
                print(f"Error updating item: {e}")
                flash('Error updating item. Please try again.', 'danger')
                return redirect(url_for('edit_item', item_id=item.id))
        return render_template('edit_item.html', item=item)

    @app.route('/item/<int:item_id>/update_quantity', methods=['POST'])
    def update_quantity(item_id):
        item = Item.query.get_or_404(item_id)
        try:
            new_quantity = int(request.form['quantity'])
            item.quantity = new_quantity
            db.session.commit()
            return jsonify({'message': 'Quantity updated successfully'}), 200
        except Exception as e:
            print(f"Error updating quantity: {e}")
            return jsonify({'message': 'Error updating quantity'}), 500

    return app


    

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')