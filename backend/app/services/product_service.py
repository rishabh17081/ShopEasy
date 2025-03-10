from app import db
from app.models.product import Product

class ProductService:
    @staticmethod
    def get_products(category=None, search_query=None):
        """
        Get products with optional filtering
        
        Args:
            category: Filter by category
            search_query: Search in name, description, and category
            
        Returns:
            List of Product objects
        """
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
        
        return query.all()
    
    @staticmethod
    def create_product(data):
        """
        Create a new product
        
        Args:
            data: Dictionary with product details
            
        Returns:
            Product object
        """
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
        
        return product
    
    @staticmethod
    def update_product(product_id, data):
        """
        Update an existing product
        
        Args:
            product_id: ID of the product to update
            data: Dictionary with updated product details
            
        Returns:
            Tuple of (product, error_message)
        """
        product = Product.query.get(product_id)
        
        if not product:
            return None, "Product not found"
        
        # Update product fields
        product.name = data['name']
        product.description = data['description']
        product.price = data['price']
        product.image = data.get('image', product.image)
        product.category = data['category']
        product.inventory = data['inventory']
        
        db.session.commit()
        
        return product, None
    
    @staticmethod
    def delete_product(product_id):
        """
        Delete a product
        
        Args:
            product_id: ID of the product to delete
            
        Returns:
            Boolean indicating success
        """
        product = Product.query.get(product_id)
        
        if not product:
            return False
        
        db.session.delete(product)
        db.session.commit()
        
        return True
