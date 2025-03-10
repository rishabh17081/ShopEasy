from app import db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product

class OrderService:
    @staticmethod
    def create_order(user_id, items_data, shipping_address, billing_address):
        """
        Create a new order
        
        Args:
            user_id: ID of the user placing the order
            items_data: List of dicts with product_id and quantity
            shipping_address: Shipping address for the order
            billing_address: Billing address for the order
            
        Returns:
            Tuple of (order, error_message)
        """
        # Validate items and calculate total
        total_amount = 0
        validated_items = []
        
        for item in items_data:
            product = Product.query.get(item['product_id'])
            
            if not product:
                return None, f"Product with ID {item['product_id']} not found"
            
            if product.inventory < item['quantity']:
                return None, f"Not enough inventory for {product.name}"
            
            validated_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': product.price
            })
            
            total_amount += product.price * item['quantity']
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            billing_address=billing_address,
            status=OrderStatus.PENDING
        )
        
        db.session.add(order)
        
        # Create order items and update inventory
        for item in validated_items:
            order_item = OrderItem(
                order=order,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
            
            # Update product inventory
            item['product'].inventory -= item['quantity']
        
        db.session.commit()
        
        return order, None
    
    @staticmethod
    def cancel_order(order_id, user_id=None):
        """
        Cancel an order and restore inventory
        
        Args:
            order_id: ID of the order to cancel
            user_id: If provided, verify the order belongs to this user
        
        Returns:
            Tuple of (order, error_message)
        """
        query = Order.query.filter_by(id=order_id)
        
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        
        order = query.first()
        
        if not order:
            return None, "Order not found"
        
        if order.status != OrderStatus.PENDING:
            return None, "Order cannot be cancelled in its current state"
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        
        # Return items to inventory
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.inventory += item.quantity
        
        db.session.commit()
        
        return order, None
    
    @staticmethod
    def update_order_status(order_id, new_status):
        """
        Update order status (admin only)
        
        Args:
            order_id: ID of the order to update
            new_status: New OrderStatus enum value
            
        Returns:
            Tuple of (order, error_message)
        """
        order = Order.query.get(order_id)
        
        if not order:
            return None, "Order not found"
        
        # Don't allow changing from CANCELLED
        if order.status == OrderStatus.CANCELLED:
            return None, "Cannot change status of a cancelled order"
        
        # Update status
        order.status = new_status
        db.session.commit()
        
        return order, None
