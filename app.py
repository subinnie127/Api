import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

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

# Crear todas las tablas dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    try:
        datos = request.form
        archivo_imagen = request.files['imagen']
        
        if not archivo_imagen:
            raise ValueError("No se recibió la imagen")

        # Guardar la imagen en el servidor
        nombre_archivo = secure_filename(archivo_imagen.filename)
        ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo_imagen.save(ruta_imagen)
        
        nuevo_producto = Producto(
            nombre=datos['nombre'],
            categoria=datos['categoria'],
            descripcion=datos['descripcion'],
            talla=datos['talla'],
            precio=datos['precio'],
            stock=datos['stock'],
            disponible=datos['disponible'] == 'on',
            imagen=ruta_imagen
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({'mensaje': 'Producto creado exitosamente'}), 201
    except Exception as e:
        print(f"Error: {e}")
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
                'imagen': producto.imagen
            }
            productos_json.append(producto_dict)
        
        return jsonify(productos_json), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    try:
        producto = Producto.query.get_or_404(id)
        db.session.delete(producto)
        db.session.commit()
        return jsonify({'mensaje': 'Producto eliminado correctamente'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'No se pudo eliminar el producto'}), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
