import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';
import { AuthContext } from '../contexts/AuthContext';
import PayPalButton from '../components/payment/PayPalButton';
import { savePaypalTransaction } from '../services/payment/paypalService';

const Cart = () => {
  const { cartItems, totalItems, totalPrice, updateQuantity, removeFromCart, clearCart } = useContext(CartContext);
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleCheckout = () => {
    if (!currentUser) {
      // Redirect to login if not logged in
      navigate('/login', { state: { from: '/checkout' } });
    } else {
      navigate('/checkout');
    }
  };

  const handlePayPalSuccess = async (data, details) => {
    console.log('PayPal payment successful', data, details);
    
    // Save order details to your backend
    const orderData = {
      paymentId: data.orderID,
      payerInfo: details.payer,
      items: cartItems,
      totalAmount: totalPrice.toFixed(2),
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
          amount: totalPrice.toFixed(2)
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
      <div className="container">
        <h1 className="mb-4">Your Cart</h1>
        <div className="alert alert-info">
          Your cart is empty. <Link to="/">Continue shopping</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1 className="mb-4">Your Cart</h1>
      
      <div className="card mb-4">
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th scope="col">Product</th>
                  <th scope="col">Price</th>
                  <th scope="col">Quantity</th>
                  <th scope="col">Total</th>
                  <th scope="col">Actions</th>
                </tr>
              </thead>
              <tbody>
                {cartItems.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="d-flex align-items-center">
                        <img 
                          src={item.image} 
                          alt={item.name} 
                          style={{ width: '50px', height: '50px', objectFit: 'cover' }}
                          className="me-3"
                        />
                        <div>
                          <h6 className="mb-0">{item.name}</h6>
                          <small className="text-muted">{item.category}</small>
                        </div>
                      </div>
                    </td>
                    <td>${item.price.toFixed(2)}</td>
                    <td>
                      <div className="input-group" style={{ width: '120px' }}>
                        <button 
                          className="btn btn-sm btn-outline-secondary" 
                          type="button"
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        >
                          -
                        </button>
                        <input 
                          type="number" 
                          className="form-control form-control-sm text-center" 
                          value={item.quantity}
                          onChange={(e) => updateQuantity(item.id, parseInt(e.target.value) || 1)}
                          min="1"
                        />
                        <button 
                          className="btn btn-sm btn-outline-secondary" 
                          type="button"
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        >
                          +
                        </button>
                      </div>
                    </td>
                    <td>${(item.price * item.quantity).toFixed(2)}</td>
                    <td>
                      <button 
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => removeFromCart(item.id)}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div className="row">
        <div className="col-md-6 offset-md-6">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Order Summary</h5>
              <div className="d-flex justify-content-between mb-2">
                <span>Items ({totalItems}):</span>
                <span>${totalPrice.toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Shipping:</span>
                <span>Free</span>
              </div>
              <hr />
              <div className="d-flex justify-content-between mb-3">
                <strong>Total:</strong>
                <strong>${totalPrice.toFixed(2)}</strong>
              </div>
              <div className="d-grid gap-2">
                <button 
                  className="btn btn-primary btn-lg"
                  onClick={handleCheckout}
                >
                  Proceed to Checkout
                </button>
                <div className="py-2">
                  <div className="d-flex align-items-center my-3">
                    <hr className="flex-grow-1" />
                    <div className="px-3 text-muted">OR</div>
                    <hr className="flex-grow-1" />
                  </div>
                  <div className="mb-2 text-center">Pay with PayPal:</div>
                  <PayPalButton 
                    amount={totalPrice.toFixed(2)} 
                    onSuccess={handlePayPalSuccess} 
                    onError={handlePayPalError} 
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4">
        <Link to="/" className="btn btn-outline-secondary">
          &larr; Continue Shopping
        </Link>
      </div>
    </div>
  );
};

export default Cart;
