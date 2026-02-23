from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza 
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI') or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

with app.app_context():
    db.create_all()

# 404 error
def not_found_response():
    return make_response(jsonify({"error": "Restaurant not found"}), 404)

# validation errors
def validation_error_response(errors):
    return make_response(jsonify({"errors": errors}), 400)

@app.route('/')
def index():
    return '<h1>Pizza Restaurants API</h1>'

# GET /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    response_body = [r.to_dict(include_relationships=False) for r in restaurants]
    return make_response(jsonify(response_body), 200)

# GET /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return not_found_response()
    
    response_body = restaurant.to_dict(include_relationships=True)
    return make_response(jsonify(response_body), 200)

# DELETE /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return not_found_response()
    
    db.session.delete(restaurant)
    db.session.commit()
    
    # return an empty response body with HTTP status code 204 for No Content
    return make_response('', 204)

# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
   
    response_body = [p.to_dict() for p in pizzas]
    return make_response(jsonify(response_body), 200)

# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json() or {}
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Validating price is in range 1 - 30
    try:
        price = float(price)
        if price < 1 or price > 30:
            return validation_error_response(["validation errors"])
    except (TypeError, ValueError):
        return validation_error_response(["validation errors"])

    restaurant = Restaurant.query.get(restaurant_id)
    pizza = Pizza.query.get(pizza_id)
    if not restaurant or not pizza:
        return validation_error_response(["validation errors"])

    try:
        new_rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_rp)
        db.session.commit()

        # Include relationships so that the pizza and restaurant classes exist
        return jsonify(new_rp.to_dict(include_relationships=True)), 201

    except Exception as e:
        db.session.rollback()
        return validation_error_response(["validation errors"])

if __name__ == '__main__':
    app.run(port=5555, debug=True)

