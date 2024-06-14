import os
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    disponible = db.Column(db.Boolean, nullable=False)
    imagen = db.Column(db.String(120), nullable=False)
    marca = db.Column(db.String(50), nullable=True)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    try:
        datos = request.form
        archivo_imagen = request.files['imagen']
        
        if not archivo_imagen or not allowed_file(archivo_imagen.filename):
            raise ValueError("Archivo de imagen no válido")

        nombre_archivo = secure_filename(archivo_imagen.filename)
        archivo_imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
        
        nuevo_producto = Producto(
            nombre=datos['nombre'],
            categoria=datos['categoria'],
            descripcion=datos['descripcion'],
            talla=datos['talla'],
            precio=float(datos['precio']),
            stock=int(datos['stock']),
            disponible=datos.get('disponible') == 'on',
            imagen=nombre_archivo,
            marca=datos['marca']
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({'mensaje': 'Producto creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    try:
        productos = Producto.query.all()
        productos_json = []
        for producto in productos:
            producto_dict = {
                'id': producto.id,
                'nombre': producto.nombre,
                'categoria': producto.categoria,
                'descripcion': producto.descripcion,
                'talla': producto.talla,
                'precio': producto.precio,
                'stock': producto.stock,
                'disponible': producto.disponible,
                'imagen': url_for('uploaded_file', filename=producto.imagen, _external=True),
                'marca': producto.marca
            }
            productos_json.append(producto_dict)
        
        return jsonify(productos_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    try:
        producto = Producto.query.get_or_404(id)
        db.session.delete(producto)
        db.session.commit()
        return jsonify({'mensaje': 'Producto eliminado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': 'No se pudo eliminar el producto'}), 500

@app.route('/api/productos/<int:id>', methods=['PUT'])
def editar_producto(id):
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404

        producto.nombre = request.form['nombre']
        producto.categoria = request.form['categoria']
        producto.descripcion = request.form['descripcion']
        producto.talla = request.form['talla']
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])
        producto.disponible = request.form.get('disponible') == 'on'
        producto.marca = request.form['marca']
        
        if 'imagen' in request.files:
            archivo_imagen = request.files['imagen']
            if allowed_file(archivo_imagen.filename):
                nombre_archivo = secure_filename(archivo_imagen.filename)
                archivo_imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
                producto.imagen = nombre_archivo

        db.session.commit()

        return jsonify({'mensaje': 'Producto actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
