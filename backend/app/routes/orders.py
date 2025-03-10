from flask import Blueprint, request, jsonify
from app import db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from app.utils.admin import admin_required
from app.services.order_service import OrderService
from app.utils.pagination import get_pagination_params
import datetime

orders_bp = Blueprint('orders', __name__)

# Validation schemas
class OrderItemSchema(Schema):
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))

class OrderSchema(Schema):
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))
    shipping_address = fields.String(required=True)
    billing_address = fields.String(required=True)

class OrderStatusSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf([status.value for status in OrderStatus]))

# Routes
@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    schema = OrderSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    # Use order service to create the order
    order, error = OrderService.create_order(
        user_id=user_id,
        items_data=data['items'],
        shipping_address=data['shipping_address'],
        billing_address=data['billing_address']
    )
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({
        "message": "Order created successfully",
        "order": order.to_dict()
    }), 201

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_user_orders():
    """Get all orders for the current user"""
    user_id = get_jwt_identity()
    
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    return jsonify([order.to_dict() for order in orders]), 200

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order for the current user"""
    user_id = get_jwt_identity()
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({"message": "Order not found"}), 404
    
    return jsonify(order.to_dict()), 200

@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order (if still pending)"""
    user_id = get_jwt_identity()
    
    order, error = OrderService.cancel_order(order_id, user_id)
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({
        "message": "Order cancelled successfully",
        "order": order.to_dict()
    }), 200

# Admin routes
@orders_bp.route('/admin/all', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders():
    """Get all orders (admin only)"""
    
    # Pagination
    page, per_page = get_pagination_params()
    
    # Filtering
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id', type=int)
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    
    # Build query
    query = Order.query
    
    if status:
        try:
            status_enum = OrderStatus(status)
            query = query.filter(Order.status == status_enum)
        except ValueError:
            pass
    
    if start_date:
        try:
            start_date = datetime.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Order.created_at >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Order.created_at <= end_date)
        except ValueError:
            pass
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    if min_amount:
        query = query.filter(Order.total_amount >= min_amount)
    
    if max_amount:
        query = query.filter(Order.total_amount <= max_amount)
    
    # Execute query with pagination
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        "orders": [order.to_dict() for order in orders.items],
        "pagination": {
            "total": orders.total,
            "pages": orders.pages,
            "current_page": orders.page
        }
    }), 200

@orders_bp.route('/admin/<int:order_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_order_status(order_id):
    """Update order status (admin only)"""
    
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({"message": "Order not found"}), 404
    
    schema = OrderStatusSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    
    try:
        new_status = OrderStatus(data['status'])
    except ValueError:
        return jsonify({"message": "Invalid status value"}), 400
    
    # Use order service to update status
    order, error = OrderService.update_order_status(order_id, new_status)
    
    if error:
        return jsonify({"message": error}), 400
    
    return jsonify({
        "message": "Order status updated successfully",
        "order": order.to_dict()
    }), 200

@orders_bp.route('/admin/statistics', methods=['GET'])
@jwt_required()
@admin_required
def get_order_statistics():
    """Get order statistics for admin dashboard"""
    # Time range filter
    days = request.args.get('days', 30, type=int)
    start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    
    # Total orders
    total_orders = Order.query.filter(Order.created_at >= start_date).count()
    
    # Orders by status
    orders_by_status = {}
    for status in OrderStatus:
        count = Order.query.filter(Order.status == status, Order.created_at >= start_date).count()
        orders_by_status[status.value] = count
    
    # Total revenue
    revenue_result = db.session.query(db.func.sum(Order.total_amount)).\
        filter(Order.created_at >= start_date).\
        filter(Order.status != OrderStatus.CANCELLED).first()
    total_revenue = revenue_result[0] if revenue_result[0] else 0
    
    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders else 0
    
    # Daily orders and revenue for the time period
    daily_stats = []
    for i in range(days):
        day_date = start_date + datetime.timedelta(days=i)
        next_day = day_date + datetime.timedelta(days=1)
        
        day_orders = Order.query.filter(Order.created_at >= day_date, Order.created_at < next_day).count()
        
        day_revenue_result = db.session.query(db.func.sum(Order.total_amount)).\
            filter(Order.created_at >= day_date, Order.created_at < next_day).\
            filter(Order.status != OrderStatus.CANCELLED).first()
        day_revenue = day_revenue_result[0] if day_revenue_result[0] else 0
        
        daily_stats.append({
            'date': day_date.strftime('%Y-%m-%d'),
            'orders': day_orders,
            'revenue': day_revenue
        })
    
    return jsonify({
        'total_orders': total_orders,
        'orders_by_status': orders_by_status,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'daily_stats': daily_stats,
        'days': days
    }), 200

@orders_bp.route('/<int:order_id>/track', methods=['GET'])
@jwt_required()
def track_order(order_id):
    """Get order tracking information"""
    user_id = get_jwt_identity()
    
    # Allow admins to track any order
    user = User.query.get(user_id)
    is_admin = getattr(user, 'is_admin', False)
    
    if is_admin:
        order = Order.query.get(order_id)
    else:
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({"message": "Order not found"}), 404
    
    # Generate tracking info based on order status
    tracking_info = {
        'order_id': order.id,
        'status': order.status.value,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat(),
        'estimated_delivery': None,
        'tracking_steps': []
    }
    
    # Add tracking steps based on order status
    tracking_info['tracking_steps'].append({
        'status': 'Order Placed',
        'completed': True,
        'date': order.created_at.isoformat()
    })
    
    if order.status in [OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
        # Calculate a date for processing (1 day after creation)
        processing_date = order.created_at + datetime.timedelta(days=1)
        tracking_info['tracking_steps'].append({
            'status': 'Processing',
            'completed': True,
            'date': processing_date.isoformat()
        })
    else:
        tracking_info['tracking_steps'].append({
            'status': 'Processing',
            'completed': False,
            'date': None
        })
    
    if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
        # Calculate a date for shipping (2 days after creation)
        shipping_date = order.created_at + datetime.timedelta(days=2)
        tracking_info['tracking_steps'].append({
            'status': 'Shipped',
            'completed': True,
            'date': shipping_date.isoformat()
        })
        
        # Set estimated delivery date (5 days after creation)
        tracking_info['estimated_delivery'] = (order.created_at + datetime.timedelta(days=5)).isoformat()
    else:
        tracking_info['tracking_steps'].append({
            'status': 'Shipped',
            'completed': False,
            'date': None
        })
    
    if order.status == OrderStatus.DELIVERED:
        # Calculate a date for delivery (5 days after creation or earlier if already set)
        delivery_date = order.updated_at if order.status == OrderStatus.DELIVERED else order.created_at + datetime.timedelta(days=5)
        tracking_info['tracking_steps'].append({
            'status': 'Delivered',
            'completed': True,
            'date': delivery_date.isoformat()
        })
    else:
        tracking_info['tracking_steps'].append({
            'status': 'Delivered',
            'completed': False,
            'date': None
        })
    
    if order.status == OrderStatus.CANCELLED:
        cancellation_date = order.updated_at
        tracking_info['tracking_steps'].append({
            'status': 'Cancelled',
            'completed': True,
            'date': cancellation_date.isoformat()
        })
    
    return jsonify(tracking_info), 200
