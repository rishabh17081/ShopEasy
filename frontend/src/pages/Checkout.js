import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';
import { AuthContext } from '../contexts/AuthContext';
import PayPalButton from '../components/payment/PayPalButton';
import { savePaypalTransaction } from '../services/payment/paypalService';
import { getUserCards, updateCard } from '../services/payment/cardService';

const Checkout = () => {
  const navigate = useNavigate();
  const { cartItems, totalPrice, clearCart } = useContext(CartContext);
  const { currentUser } = useContext(AuthContext);
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [savedCards, setSavedCards] = useState([]);
  const [selectedCard, setSelectedCard] = useState('');
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
    saveCard: false
  });
  const [isLoading, setIsLoading] = useState(false);

  // Fetch user's saved cards when component mounts
  useEffect(() => {
    const fetchUserCards = async () => {
      console.log('Current user in Checkout:', currentUser);
      console.log('Access token exists:', !!localStorage.getItem('accessToken'));
      
      if (currentUser && localStorage.getItem('accessToken')) {
        setIsLoading(true);
        try {
          console.log('Fetching cards for user ID:', currentUser.id);
          const response = await getUserCards(currentUser.id);
          console.log('getUserCards response:', response);
          
          if (response.success) {
            console.log('Setting saved cards:', response.data);
            setSavedCards(response.data);
            
            if (response.data.length === 0) {
              console.warn('No cards returned from API even though user should have cards');
            }
          } else {
            // Handle the case where the API call was not successful
            console.error('Failed to fetch saved cards:', response.error);
            setSavedCards([]);
          }
        } catch (error) {
          console.error('Exception fetching saved cards:', error);
          // Don't let API interceptor redirect, just handle the error here
          setSavedCards([]);
        } finally {
          setIsLoading(false);
        }
      } else {
        // User is not authenticated, just set empty cards array
        console.log('User not authenticated, setting empty cards array');
        setSavedCards([]);
      }
    };

    fetchUserCards();
  }, [currentUser]);

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
    return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2);
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

  const handlePayPalSuccess = async (data, details) => {
    console.log('PayPal payment successful', data, details);
    
    // Save order details to your backend
    const orderData = {
      paymentId: data.orderID,
      payerInfo: details.payer,
      shippingAddress: formData,
      items: cartItems,
      totalAmount: calculateTotal(),
      date: new Date().toISOString()
    };
    
    try {
      // Save the transaction to your backend
      const result = await savePaypalTransaction(orderData);
      console.log('Transaction saved:', result);
      
      // Clear the cart and navigate to order confirmation
      clearCart();
      navigate('/order-confirmation', { 
        state: { 
          paymentId: data.orderID,
          payerName: details.payer.name.given_name + ' ' + details.payer.name.surname,
          amount: calculateTotal()
        } 
      });
    } catch (error) {
      console.error('Error saving transaction:', error);
      alert('Payment was processed but we had trouble saving your order. Please contact support.');
    }
  };

  const handlePayPalError = (error) => {
    console.error('PayPal payment error:', error);
    alert('There was an error processing your PayPal payment. Please try again.');
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
              <div className="form-check">
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
                          placeholder="MM/YY"
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
                        placeholder="MM/YY"
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
                {currentUser && selectedCard === 'new' && (
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
            
            {paymentMethod === 'paypal' && (
              <div className="mt-4">
                <p>Click the PayPal button below to complete your payment:</p>
                <PayPalButton 
                  amount={calculateTotal()} 
                  onSuccess={handlePayPalSuccess} 
                  onError={handlePayPalError} 
                />
              </div>
            )}
          </form>
        </div>
        
        <div className="col-md-4">
          <div className="card">
            <div className="card-header">
              <h5>Order Summary</h5>
            </div>
            <div className="card-body">
              {cartItems.map(item => (
                <div key={item.id} className="d-flex justify-content-between mb-2">
                  <span>{item.name} x {item.quantity}</span>
                  <span>${(item.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
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
