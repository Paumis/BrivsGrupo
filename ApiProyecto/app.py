from flask import Flask, jsonify, request, redirect, url_for, render_template
from flaskr.modelos import db, MenuItem, Menu, Order, OrderDetail, Staff, Mesa, Admin
from flaskr import create_app
from datetime import datetime

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
# Inicio Usuarios
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = Staff.query.filter_by(username=username).first()

    if user is None:
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            return redirect(url_for('admin_dashboard'))
        else:
            return jsonify({"error": "Credenciales de inicio de sesión incorrectas"}), 401
    else:
        role = user.role.lower()
        if role == 'chef':
            return redirect(url_for('chef_dashboard'))
        elif role == 'mesero':
            return redirect(url_for('mesero_dashboard'))
        else:
            return jsonify({"error": "Rol de usuario no válido"}), 401

@app.route('/admin_dashboard')
def admin_dashboard():
    return jsonify({"message": "Bienvenido al panel de control del administrador"})

@app.route('/chef_dashboard')
def chef_dashboard():
    return jsonify({"message": "Bienvenido al panel de control del chef"})

@app.route('/mesero_dashboard')
def mesero_dashboard():
    return jsonify({"message": "Bienvenido al panel de control del mesero"})
@app.route('/menu', defaults={'menu_id': None})
@app.route('/menu/<int:menu_id>')
def menu_items(menu_id=None):
    if menu_id is not None:
        menu = Menu.query.filter_by(menuID=menu_id).first()
        if menu:
            menu_items = MenuItem.query.filter_by(menuID=menu_id).all()
            serialized_menu = menu.serialize()
            return jsonify({"menu": serialized_menu, "menu_items": [item.serialize() for item in menu_items]})
        else:
            return jsonify({"error": "Categoría no encontrada"}), 404
    else:
        all_menus = Menu.query.all()
        serialized_menus = [menu.serialize() for menu in all_menus]
        return jsonify({"menus": serialized_menus})

if __name__ == '__main__':
    app.run(debug=True)
#agregar nuevo pedido
@app.route('/agregar_pedido', methods=['POST'])
def agregar_pedido():
    data = request.json
    mesa_id = data.get('mesaID')
    order_details = data.get('order_details', [])

    nuevo_pedido = Order(status='ready', total=data.get('total'), order_date=datetime.now(), mesaID=mesa_id)

    try:
        db.session.add(nuevo_pedido)
        db.session.commit()

        for detail in order_details:
            item_id = detail.get('itemID')
            quantity = detail.get('quantity')
            order_detail = OrderDetail(orderID=nuevo_pedido.orderID, itemID=item_id, quantity=quantity, mesaID=mesa_id)
            db.session.add(order_detail)

        db.session.commit()
        return jsonify({"message": "Nuevo pedido agregado correctamente", "order_id": nuevo_pedido.orderID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


#Admin agregar nueva categoria
@app.route('/agregar_categoria', methods=['POST'])
def agregar_categoria():
    data = request.json
    nombre_categoria = data.get('nombre_categoria')

    if not nombre_categoria:
        return jsonify({"error": "El nombre de la categoría es requerido"}), 400

    nueva_categoria = Menu(menuName=nombre_categoria)

    try:
        db.session.add(nueva_categoria)
        db.session.commit()
        return jsonify({"message": "Nueva categoría agregada correctamente", "categoria_id": nueva_categoria.menuID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

#Admin agregar nuevo plato
@app.route('/agregar_plato', methods=['POST'])
def agregar_plato():
    data = request.json
    menu_id = data.get('menu_id')
    plato_nombre = data.get('plato_nombre')
    precio = data.get('precio')

    if not menu_id or not plato_nombre or not precio:
        return jsonify({"error": "Todos los campos son requeridos"}), 400
    categoria = Menu.query.get(menu_id)
    if not categoria:
        return jsonify({"error": "La categoría especificada no existe"}), 404

    nuevo_plato = MenuItem(menuID=menu_id, menuItemName=plato_nombre, price=precio)

    try:
        db.session.add(nuevo_plato)
        db.session.commit()
        return jsonify({"message": "Nuevo plato agregado correctamente", "plato_id": nuevo_plato.itemID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
#
if __name__ == '__main__':
    app.run(debug=True)
