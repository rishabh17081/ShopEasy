import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';
import PayPalButton from '../components/payment/PayPalButton';
import { savePaypalTransaction } from '../services/payment/paypalService';

const Checkout = () => {
  const navigate = useNavigate();
  const { cartItems, totalPrice, clearCart } = useContext(CartContext);
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    address: '',
    city: '',
    zipCode: '',
    cardNumber: '',
    expiryDate: '',
    cvv: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (paymentMethod === 'credit_card') {
      // Process credit card payment
      console.log('Processing credit card payment with data:', formData);
      
      // Clear the cart and navigate to order confirmation
      clearCart();
      navigate('/order-confirmation');
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
            
            {paymentMethod === 'credit_card' ? (
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
                      required={paymentMethod === 'credit_card'}
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
                
                <button type="submit" className="btn btn-primary mt-4">Place Order</button>
              </>
            ) : (
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