from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from sqlalchemy.exc import SQLAlchemyError
import re
import functools

cards_bp = Blueprint('cards', __name__)

# Helper function to validate card details
def validate_card_details(data):
    errors = {}
    
    # Validate card number (simple check for this example)
    card_number = data.get('card_number', '')
    if not card_number or not re.match(r'^\d{13,19}$', card_number.replace(' ', '')):
        errors['card_number'] = 'Invalid card number'
    
    # Validate expiry date (MM/YY or MM/YYYY format)
    expiry_date = data.get('expiry_date', '')
    if not expiry_date or not re.match(r'^(0[1-9]|1[0-2])/(\d{2}|\d{4})$', expiry_date):
        errors['expiry_date'] = 'Invalid expiry date format (MM/YY or MM/YYYY)'
    
    # Validate CVV (3-4 digits)
    cvv = data.get('cvv', '')
    if not cvv or not re.match(r'^\d{3,4}$', cvv):
        errors['cvv'] = 'Invalid CVV'
    
    # Validate cardholder name
    cardholder_name = data.get('cardholder_name', '')
    if not cardholder_name or len(cardholder_name) < 3:
        errors['cardholder_name'] = 'Invalid cardholder name'
    
    return errors

# Custom decorator to handle both JWT and demo token
def custom_jwt_required(fn):
    @functools.wraps(fn)
    def decorator(*args, **kwargs):
        # Check if using demo token
        auth_header = request.headers.get('Authorization', '')
        if auth_header and 'Bearer demo-jwt-token' in auth_header:
            # Set user_id to 1 for John Doe
            request.user_id = 1
            print("Using demo token for user ID 1")
            return fn(*args, **kwargs)
        
        # Otherwise use normal JWT validation
        try:
            verify_jwt_in_request()
            request.user_id = get_jwt_identity()
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"JWT validation error: {e}")
            return jsonify({"error": "Invalid or missing token"}), 401
    
    return decorator

# Get all cards for the current user
@cards_bp.route('/user/cards', methods=['GET'])
@custom_jwt_required
def get_user_cards():
    user_id = request.user_id
    
    print(f"Fetching cards for user ID: {user_id}")
    
    try:
        # Execute raw SQL query to get all cards for the user
        cursor = db.session.execute(
            """
            SELECT id, card_type, last_four, expiry_date, cardholder_name, 
                   is_default, subscription_id, created_at
            FROM cards 
            WHERE user_id = :user_id
            ORDER BY is_default DESC
            """,
            {"user_id": user_id}
        )
        
        cards = [dict(row) for row in cursor]
        
        print(f"Found {len(cards)} cards for user {user_id}")
        
        # Format dates for JSON response
        for card in cards:
            if 'created_at' in card and card['created_at']:
                # Check if created_at is already a string
                if not isinstance(card['created_at'], str):
                    card['created_at'] = card['created_at'].isoformat()
        
        return jsonify(cards), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Get a specific card by ID
@cards_bp.route('/user/cards/<int:card_id>', methods=['GET'])
@custom_jwt_required
def get_card(card_id):
    user_id = request.user_id
    
    try:
        # Execute raw SQL query to get the specific card
        cursor = db.session.execute(
            """
            SELECT id, card_type, last_four, expiry_date, cardholder_name, 
                   is_default, subscription_id, created_at
            FROM cards 
            WHERE id = :card_id AND user_id = :user_id
            """,
            {"card_id": card_id, "user_id": user_id}
        )
        
        card = dict(cursor.fetchone()) if cursor.rowcount > 0 else None
        
        if not card:
            return jsonify({"error": "Card not found"}), 404
        
        # Format dates for JSON response
        if 'created_at' in card and card['created_at']:
            # Check if created_at is already a string
            if not isinstance(card['created_at'], str):
                card['created_at'] = card['created_at'].isoformat()
        
        return jsonify(card), 200
    
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

# Add a new card
@cards_bp.route('/user/cards', methods=['POST'])
@custom_jwt_required
def add_card():
    user_id = request.user_id
    data = request.json
    
    # Validate card details
    validation_errors = validate_card_details(data)
    if validation_errors:
        return jsonify({"errors": validation_errors}), 400
    
    try:
        # Process card details (in a real app, you'd tokenize card data using a payment processor)
        card_number = data.get('card_number', '').replace(' ', '')
        last_four = card_number[-4:] if card_number else None
        
        # Detect card type based on first digit (simplified)
        card_type = 'Unknown'
        if card_number:
            first_digit = card_number[0]
            if first_digit == '4':
                card_type = 'Visa'
            elif first_digit == '5':
                card_type = 'Mastercard'
            elif first_digit == '3' and card_number.startswith(('34', '37')):
                card_type = 'American Express'
            elif first_digit == '6':
                card_type = 'Discover'
        
        # If this is the first card for the user or is_default is true, set it as the default
        cursor = db.session.execute(
            "SELECT COUNT(*) as card_count FROM cards WHERE user_id = :user_id",
            {"user_id": user_id}
        )
        result = cursor.fetchone()
        is_first_card = result['card_count'] == 0 if result else True
        
        is_default = data.get('is_default', False) or is_first_card
        
        # If setting this card as default, update other cards to not be default
        if is_default:
            db.session.execute(
                "UPDATE cards SET is_default = FALSE WHERE user_id = :user_id",
                {"user_id": user_id}
            )
        
        # Insert the new card
        cursor = db.session.execute(
            """
            INSERT INTO cards (
                user_id, card_type, last_four, expiry_date, 
                cardholder_name, is_default, created_at
            ) VALUES (
                :user_id, :card_type, :last_four, :expiry_date, 
                :cardholder_name, :is_default, CURRENT_TIMESTAMP
            ) RETURNING id
            """,
            {
                "user_id": user_id,
                "card_type": card_type,
                "last_four": last_four,
                "expiry_date": data.get('expiry_date'),
                "cardholder_name": data.get('cardholder_name'),
                "is_default": is_default
            }
        )
        
        new_card_id = cursor.fetchone()['id']
        db.session.commit()
        
        # Get the newly created card
        cursor = db.session.execute(
            """
            SELECT id, card_type, last_four, expiry_date, cardholder_name, 
                   is_default, created_at
            FROM cards 
            WHERE id = :card_id
            """,
            {"card_id": new_card_id}
        )
        
        new_card = dict(cursor.fetchone())
        
        # Format dates for JSON response
        if 'created_at' in new_card and new_card['created_at']:
            # Check if created_at is already a string
            if not isinstance(new_card['created_at'], str):
                new_card['created_at'] = new_card['created_at'].isoformat()
        
        return jsonify(new_card), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Update a card
@cards_bp.route('/user/cards/<int:card_id>', methods=['PUT'])
@custom_jwt_required
def update_card(card_id):
    user_id = request.user_id
    data = request.json
    
    try:
        # Check if the card belongs to the user
        cursor = db.session.execute(
            "SELECT id FROM cards WHERE id = :card_id AND user_id = :user_id",
            {"card_id": card_id, "user_id": user_id}
        )
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Card not found"}), 404
        
        # Build the update query dynamically based on the provided fields
        update_fields = []
        params = {"card_id": card_id}
        
        if 'expiry_date' in data:
            update_fields.append("expiry_date = :expiry_date")
            params["expiry_date"] = data['expiry_date']
        
        if 'cardholder_name' in data:
            update_fields.append("cardholder_name = :cardholder_name")
            params["cardholder_name"] = data['cardholder_name']
        
        if 'is_default' in data and data['is_default']:
            # If setting this card as default, update other cards to not be default
            db.session.execute(
                "UPDATE cards SET is_default = FALSE WHERE user_id = :user_id",
                {"user_id": user_id}
            )
            update_fields.append("is_default = TRUE")
        
        if not update_fields:
            return jsonify({"message": "No fields to update"}), 200
        
        # Execute the update query
        query = f"UPDATE cards SET {', '.join(update_fields)} WHERE id = :card_id"
        db.session.execute(query, params)
        db.session.commit()
        
        # Get the updated card
        cursor = db.session.execute(
            """
            SELECT id, card_type, last_four, expiry_date, cardholder_name, 
                   is_default, created_at
            FROM cards 
            WHERE id = :card_id
            """,
            {"card_id": card_id}
        )
        
        updated_card = dict(cursor.fetchone())
        
        # Format dates for JSON response
        if 'created_at' in updated_card and updated_card['created_at']:
            # Check if created_at is already a string
            if not isinstance(updated_card['created_at'], str):
                updated_card['created_at'] = updated_card['created_at'].isoformat()
        
        return jsonify(updated_card), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Delete a card
@cards_bp.route('/user/cards/<int:card_id>', methods=['DELETE'])
@custom_jwt_required
def delete_card(card_id):
    user_id = request.user_id
    
    try:
        # Check if the card exists and belongs to the user
        cursor = db.session.execute(
            "SELECT id, is_default FROM cards WHERE id = :card_id AND user_id = :user_id",
            {"card_id": card_id, "user_id": user_id}
        )
        
        card = cursor.fetchone()
        if not card:
            return jsonify({"error": "Card not found"}), 404
        
        # Delete the card
        db.session.execute(
            "DELETE FROM cards WHERE id = :card_id",
            {"card_id": card_id}
        )
        
        # If the deleted card was the default, set another card as default if available
        if card['is_default']:
            cursor = db.session.execute(
                "SELECT id FROM cards WHERE user_id = :user_id LIMIT 1",
                {"user_id": user_id}
            )
            
            new_default = cursor.fetchone()
            if new_default:
                db.session.execute(
                    "UPDATE cards SET is_default = TRUE WHERE id = :card_id",
                    {"card_id": new_default['id']}
                )
        
        db.session.commit()
        
        return jsonify({"message": "Card deleted successfully"}), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Set a card as the default
@cards_bp.route('/user/cards/<int:card_id>/default', methods=['PUT'])
@custom_jwt_required
def set_default_card(card_id):
    user_id = request.user_id
    
    try:
        # Check if the card exists and belongs to the user
        cursor = db.session.execute(
            "SELECT id FROM cards WHERE id = :card_id AND user_id = :user_id",
            {"card_id": card_id, "user_id": user_id}
        )
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Card not found"}), 404
        
        # Set all cards for this user as non-default
        db.session.execute(
            "UPDATE cards SET is_default = FALSE WHERE user_id = :user_id",
            {"user_id": user_id}
        )
        
        # Set the selected card as default
        db.session.execute(
            "UPDATE cards SET is_default = TRUE WHERE id = :card_id",
            {"card_id": card_id}
        )
        
        db.session.commit()
        
        return jsonify({"message": "Card set as default successfully"}), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
