from flask import Blueprint, request, jsonify
from app import db
from app.models.product import Product
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError

products_bp = Blueprint('products', __name__)

# Validation schemas
class ProductSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=3, max=100))
    description = fields.String(required=True)
    price = fields.Float(required=True, validate=validate.Range(min=0.01))
    image = fields.String()
    category = fields.String(required=True)
    inventory = fields.Integer(required=True, validate=validate.Range(min=0))

# Routes
@products_bp.route('', methods=['GET'])
def get_products():
    """Get all products or filter by category/search query"""
    category = request.args.get('category')
    search_query = request.args.get('query')
    
    query = Product.query
    
    if category and category.lower() != 'all':
        query = query.filter(Product.category.ilike(f'{category}'))
    
    if search_query:
        search_term = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.category.ilike(search_term)
            )
        )
    
    products = query.all()
    return jsonify([product.to_dict() for product in products]), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    return jsonify(product.to_dict()), 200

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique product categories"""
    categories = db.session.query(Product.category).distinct().all()
    return jsonify([category[0] for category in categories]), 200

# Admin routes (protected)
@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product (admin only)"""
    schema = ProductSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        image=data.get('image', 'https://via.placeholder.com/300x300?text=Product'),
        category=data['category'],
        inventory=data['inventory']
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        "message": "Product created successfully",
        "product": product.to_dict()
    }), 201

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product (admin only)"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    schema = ProductSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    # Update product fields
    product.name = data['name']
    product.description = data['description']
    product.price = data['price']
    product.image = data.get('image', product.image)
    product.category = data['category']
    product.inventory = data['inventory']
    
    db.session.commit()
    
    return jsonify({
        "message": "Product updated successfully",
        "product": product.to_dict()
    }), 200

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product (admin only)"""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({
        "message": "Product deleted successfully"
    }), 200
