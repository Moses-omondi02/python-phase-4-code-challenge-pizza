#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])


@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    # Use db.session.get() instead of Restaurant.query.get() to eliminate warnings
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
    
    restaurant_data = restaurant.to_dict()
    restaurant_data['restaurant_pizzas'] = [rp.to_dict() for rp in restaurant_pizzas]
    
    return jsonify(restaurant_data)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    # Use db.session.get() instead of Restaurant.query.get() to eliminate warnings
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    db.session.delete(restaurant)
    db.session.commit()
    
    return make_response('', 204)


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_data = [{
        'id': pizza.id,
        'name': pizza.name,
        'ingredients': pizza.ingredients
    } for pizza in pizzas]
    return jsonify(pizzas_data)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    try:
        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        return make_response(jsonify(restaurant_pizza.to_dict()), 201)
        
    except ValueError as e:
        db.session.rollback()
    
        return make_response(jsonify({"errors": ["validation errors"]}), 400)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"errors": ["validation errors"]}), 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
