import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';
import { AuthContext } from '../contexts/AuthContext';
import { getUserCards, updateCard, saveCard } from '../services/payment/cardService';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';

const Checkout = () => {
  const navigate = useNavigate();
  const { cartItems, totalPrice, clearCart } = useContext(CartContext);
  const { currentUser } = useContext(AuthContext);
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [savedCards, setSavedCards] = useState([]);
  const [selectedCard, setSelectedCard] = useState('');
  
  // PayPal initial options
  const initialOptions = {
    clientId: "AdlchHuRCMtJU8TEV1808gahBAlgSLZJULcVEl5-sOgIwLNbIGqK6L4PvBW3v-eE8zLn9LYaLtWsIZP3", // Replace with your PayPal client ID in production
    currency: "USD",
    intent: "capture",
  };
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    address: '',
    city: '',
    zipCode: '',
    cardNumber: '',
    expiryDate: '',
    cvv: '',
    saveCard: true // Default to true for better user experience
  });
  const [isLoading, setIsLoading] = useState(false);

  // Fetch user's saved cards when component mounts
  useEffect(() => {
    // For testing purposes, we'll skip the authentication check
    console.log('Skipping authentication check for testing');
    setSavedCards([]);
  }, []);

  // Prefill form data from user's profile if logged in
  useEffect(() => {
    if (currentUser) {
      setFormData(prevState => ({
        ...prevState,
        firstName: currentUser.first_name || '',
        lastName: currentUser.last_name || '',
        email: currentUser.email || ''
      }));
    }
  }, [currentUser]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleCardSelection = (e) => {
    const cardId = e.target.value;
    setSelectedCard(cardId);
    
    if (cardId === 'new') {
      // Clear card fields if "Use new card" is selected
      setFormData(prevState => ({
        ...prevState,
        cardNumber: '',
        expiryDate: '',
        cvv: ''
      }));
    } else {
      // Find the selected card and prefill form data
      const card = savedCards.find(c => c.id.toString() === cardId);
      if (card) {
        // For existing cards, we'll show the last four digits but allow editing
        // In a real app, you might want to validate any changes to the card number
        setFormData(prevState => ({
          ...prevState,
          cardNumber: `**** **** **** ${card.last_four}`,
          expiryDate: card.expiry_date,
          // CVV is a security field and should not be prefilled
          cvv: ''
        }));
      }
    }
  };

  const calculateTotal = () => {
    try {
      if (!cartItems || !Array.isArray(cartItems)) {
        console.error("Invalid cart items:", cartItems);
        return "0.00";
      }
      
      return cartItems.reduce((total, item) => {
        // Validate item data
        if (!item || typeof item.price !== 'number' || typeof item.quantity !== 'number') {
          console.error("Invalid item in cart:", item);
          return total;
        }
        return total + (item.price * item.quantity);
      }, 0).toFixed(2);
    } catch (error) {
      console.error("Error calculating total:", error);
      return "0.00";
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (paymentMethod === 'credit_card') {
      try {
        // If using an existing card and the data has changed, update the card
        if (selectedCard && selectedCard !== 'new' && currentUser) {
          const card = savedCards.find(c => c.id.toString() === selectedCard);
          
          // Check if card data has been modified
          if (card && formData.expiryDate !== card.expiry_date) {
            console.log('Updating card with new information');
            
            // Update the card with new information
            await updateCard(currentUser.id, selectedCard, {
              expiryDate: formData.expiryDate
            });
            
            console.log('Card updated successfully');
          }
        }
        
        // If using a new card and the user wants to save it, save the card
        if (currentUser && (selectedCard === 'new' || !savedCards.length) && formData.saveCard) {
          console.log('Saving new card for future use');
          
          try {
            // Format the card data for saving
            const cardData = {
              cardNumber: formData.cardNumber,
              expiryDate: formData.expiryDate,
              cvv: formData.cvv,
              cardholderName: `${formData.firstName} ${formData.lastName}`,
              isDefault: false // Don't make it default automatically
            };
            
            // Save the card
            const saveResponse = await saveCard(currentUser.id, cardData);
            
            if (saveResponse.success) {
              console.log('Card saved successfully:', saveResponse.data);
            } else {
              console.error('Failed to save card:', saveResponse.error);
            }
          } catch (saveError) {
            console.error('Error saving card:', saveError);
            // Continue with payment even if card saving fails
          }
        }
        
        // Process credit card payment
        console.log('Processing credit card payment with data:', {
          ...formData,
          selectedCard: selectedCard !== 'new' ? selectedCard : 'New card'
        });
        
        // In a real implementation, you'd send this data to your backend
        // and handle payment processing
        
        // Clear the cart and navigate to order confirmation
        clearCart();
        navigate('/order-confirmation');
      } catch (error) {
        console.error('Error processing payment:', error);
        alert('There was an error processing your payment. Please try again.');
      }
    }
    // PayPal is handled separately by the PayPal component
  };


  if (cartItems.length === 0) {
    return (
      <div className="text-center mt-5">
        <h2>Your cart is empty</h2>
        <button 
          className="btn btn-primary mt-3" 
          onClick={() => navigate('/')}
        >
          Continue Shopping
        </button>
      </div>
    );
  }

  return (
    <div className="container">
      <h2 className="mb-4">Checkout</h2>
      
      <div className="row">
        <div className="col-md-8">
          <form onSubmit={handleSubmit}>
            <h4>Shipping Information</h4>
            <div className="row mb-3">
              <div className="col">
                <label htmlFor="firstName" className="form-label">First Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="col">
                <label htmlFor="lastName" className="form-label">Last Name</label>
                <input
                  type="text"
                  className="form-control"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            
            <div className="mb-3">
              <label htmlFor="email" className="form-label">Email</label>
              <input
                type="email"
                className="form-control"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="mb-3">
              <label htmlFor="address" className="form-label">Address</label>
              <input
                type="text"
                className="form-control"
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="row mb-3">
              <div className="col">
                <label htmlFor="city" className="form-label">City</label>
                <input
                  type="text"
                  className="form-control"
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="col">
                <label htmlFor="zipCode" className="form-label">Zip Code</label>
                <input
                  type="text"
                  className="form-control"
                  id="zipCode"
                  name="zipCode"
                  value={formData.zipCode}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            
            <h4 className="mt-4">Payment Method</h4>
            <div className="mb-3">
              <div className="form-check mb-2">
                <input
                  className="form-check-input"
                  type="radio"
                  name="paymentMethod"
                  id="creditCard"
                  value="credit_card"
                  checked={paymentMethod === 'credit_card'}
                  onChange={() => setPaymentMethod('credit_card')}
                />
                <label className="form-check-label" htmlFor="creditCard">
                  Credit Card
                </label>
              </div>
              <div className="form-check mb-2">
                <input
                  className="form-check-input"
                  type="radio"
                  name="paymentMethod"
                  id="paypal"
                  value="paypal"
                  checked={paymentMethod === 'paypal'}
                  onChange={() => setPaymentMethod('paypal')}
                />
                <label className="form-check-label" htmlFor="paypal">
                  PayPal
                </label>
              </div>
            </div>
            
            {paymentMethod === 'paypal' && (
              <div className="mb-4">
                <PayPalScriptProvider options={initialOptions}>
                  <PayPalButtons 
                    style={{ 
                      layout: "vertical",
                      tagline: false
                    }}
                    createOrder={(data, actions) => {
                      return actions.order.create({
                        purchase_units: [
                          {
                            amount: {
                              value: calculateTotal(),
                            },
                            description: `Order with ${cartItems.length} items`,
                          },
                        ],
                      });
                    }}
                    onApprove={(data, actions) => {
                      return actions.order.capture().then((details) => {
                        // Handle successful payment
                        const name = details.payer.name.given_name;
                        alert(`Transaction completed by ${name}`);
                        clearCart();
                        navigate('/order-confirmation');
                      });
                    }}
                    onError={(err) => {
                      console.error('PayPal Checkout Error:', err);
                      alert('There was an error processing your payment. Please try again.');
                    }}
                  />
                </PayPalScriptProvider>
              </div>
            )}
            
            {paymentMethod === 'credit_card' && (
              <>
                {/* Card Selection Dropdown for existing users */}
                {currentUser && savedCards.length > 0 && (
                  <div className="mb-3">
                    <label htmlFor="savedCards" className="form-label">Select Payment Method</label>
                    <select
                      className="form-select"
                      id="savedCards"
                      value={selectedCard}
                      onChange={handleCardSelection}
                      required
                    >
                      <option value="">Select a card</option>
                      {savedCards.map(card => (
                        <option key={card.id} value={card.id.toString()}>
                          {card.card_type} **** {card.last_four} | Expires: {card.expiry_date} {card.is_default ? '(Default)' : ''}
                        </option>
                      ))}
                      <option value="new">+ Use a new card</option>
                    </select>
                  </div>
                )}

                {/* Show card form if no saved cards, not logged in, or "new card" is selected */}
                {(!currentUser || savedCards.length === 0 || selectedCard === 'new') && (
                  <>
                    <div className="mb-3">
                      <label htmlFor="cardNumber" className="form-label">Card Number</label>
                      <input
                        type="text"
                        className="form-control"
                        id="cardNumber"
                        name="cardNumber"
                        value={formData.cardNumber}
                        onChange={handleChange}
                        placeholder="XXXX XXXX XXXX XXXX"
                        required={paymentMethod === 'credit_card' && (!currentUser || selectedCard === 'new' || savedCards.length === 0)}
                      />
                    </div>
                    
                    <div className="row mb-3">
                      <div className="col">
                        <label htmlFor="expiryDate" className="form-label">Expiry Date</label>
                        <input
                          type="text"
                          className="form-control"
                          id="expiryDate"
                          name="expiryDate"
                          value={formData.expiryDate}
                          onChange={handleChange}
                          placeholder="MM/YYYY"
                          required={paymentMethod === 'credit_card' && (!currentUser || selectedCard === 'new' || savedCards.length === 0)}
                        />
                      </div>
                      <div className="col">
                        <label htmlFor="cvv" className="form-label">CVV</label>
                        <input
                          type="text"
                          className="form-control"
                          id="cvv"
                          name="cvv"
                          value={formData.cvv}
                          onChange={handleChange}
                          placeholder="123"
                          required={paymentMethod === 'credit_card'}
                        />
                      </div>
                    </div>
                  </>
                )}

                {/* For saved cards, show editable fields */}
                {currentUser && selectedCard !== 'new' && selectedCard !== '' && (
                  <>
                    <div className="mb-3">
                      <label htmlFor="cardNumber" className="form-label">Card Number</label>
                      <input
                        type="text"
                        className="form-control"
                        id="cardNumber"
                        name="cardNumber"
                        value={formData.cardNumber}
                        onChange={handleChange}
                        placeholder="XXXX XXXX XXXX XXXX"
                        required={paymentMethod === 'credit_card'}
                        disabled={true} // Card number is not editable for security reasons
                      />
                      <small className="text-muted">For security reasons, you cannot edit the card number.</small>
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="expiryDate" className="form-label">Expiry Date</label>
                      <input
                        type="text"
                        className="form-control"
                        id="expiryDate"
                        name="expiryDate"
                        value={formData.expiryDate}
                        onChange={handleChange}
                        placeholder="MM/YYYY"
                        required={paymentMethod === 'credit_card'}
                      />
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="cvv" className="form-label">CVV</label>
                      <input
                        type="text"
                        className="form-control"
                        id="cvv"
                        name="cvv"
                        value={formData.cvv}
                        onChange={handleChange}
                        placeholder="123"
                        required={paymentMethod === 'credit_card'}
                      />
                    </div>
                  </>
                )}

                {/* Option to save card for logged in users */}
                {currentUser && (!savedCards.length || selectedCard === 'new') && (
                  <div className="mb-3 form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="saveCard"
                      name="saveCard"
                      checked={formData.saveCard}
                      onChange={handleChange}
                    />
                    <label className="form-check-label" htmlFor="saveCard">
                      Save this card for future purchases
                    </label>
                  </div>
                )}
                
                <button type="submit" className="btn btn-primary mt-4">Place Order</button>
              </>
            )}
            
          </form>
        </div>
        
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5>Order Summary</h5>
            </div>
            <div className="card-body">
              {Array.isArray(cartItems) ? cartItems.map(item => {
                try {
                  if (!item || !item.id || typeof item.price !== 'number' || typeof item.quantity !== 'number') {
                    console.error("Invalid item in cart:", item);
                    return null;
                  }
                  return (
                    <div key={item.id} className="d-flex justify-content-between mb-2">
                      <span>{item.name || 'Unknown Product'} x {item.quantity}</span>
                      <span>${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                  );
                } catch (error) {
                  console.error("Error rendering cart item:", error);
                  return null;
                }
              }) : (
                <div className="text-center">
                  <p>No items in cart</p>
                </div>
              )}
              <hr />
              <div className="d-flex justify-content-between">
                <strong>Total:</strong>
                <strong>${calculateTotal()}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
