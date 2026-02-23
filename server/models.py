from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

db = SQLAlchemy() 

# Restaurant
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    address = db.Column(db.String)

    #relationships
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan'
    )
    #serialize
    _serialize_rules = ('-restaurant_pizzas', '-restaurant_pizzas.restaurant')

    def to_dict(self, include_relationships=False):
        data = {"id": self.id, "name": self.name, "address": self.address}
        if include_relationships:
            data["restaurant_pizzas"] = [rp.to_dict() for rp in self.restaurant_pizzas]
        return data


# Pizza
class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    #relationships
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan'
    )

    # serialize
    _serialize_rules = ('-restaurant_pizzas',)

    def to_dict(self, include_relationships=False):
        data = {"id": self.id, "name": self.name, "ingredients": self.ingredients}
        if include_relationships:
            data["restaurant_pizzas"] = [rp.to_dict() for rp in self.restaurant_pizzas]
        return data

# RestaurantPizza - linking Restaurant database and Pizza database together
class RestaurantPizza(db.Model):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")

    #validate
    @validates('price')
    def validate_price(self, key, value):
        if value is None or not isinstance(value, (int, float)) or value < 1 or value > 30:
            raise ValueError("Price must be a number between 1 and 30")
        return value

    def to_dict(self, include_relationships=False):
        d = {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id
        }
        if include_relationships:
            d["pizza"] = self.pizza.to_dict()
            d["restaurant"] = self.restaurant.to_dict()
        return d