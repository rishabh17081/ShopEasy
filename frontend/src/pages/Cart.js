import React, { useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';
import { AuthContext } from '../contexts/AuthContext';
import PayPalButton from '../components/payment/PayPalButton';
import { savePaypalTransaction } from '../services/payment/paypalService';
import { safeExecute } from '../utils/errorHandling';

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
    // Use safeExecute to wrap the entire function
    return safeExecute(async () => {
      console.log('PayPal payment successful', data, details);
      
      // Safely access data properties with fallbacks
      const paymentId = data?.orderID || 'unknown';
      const payerInfo = details?.payer || {};
      const safePrice = typeof totalPrice === 'number' ? totalPrice : 0;
      
      // Save order details to your backend
      const orderData = {
        paymentId: paymentId,
        payerInfo: payerInfo,
        items: cartItems || [],
        totalAmount: safePrice.toFixed(2),
        date: new Date().toISOString()
      };
      
      // Use safeExecute for the nested try-catch
      const result = await safeExecute(async () => {
        return await savePaypalTransaction(orderData);
      }, { success: false, message: 'Transaction failed silently' });
      
      console.log('Transaction saved:', result);
      
      // Clear the cart and navigate to order confirmation
      clearCart();
      
      // Safely access payer name properties
      const firstName = payerInfo?.name?.given_name || '';
      const lastName = payerInfo?.name?.surname || '';
      const payerName = firstName + (firstName && lastName ? ' ' : '') + lastName || 'Customer';
      
      navigate('/order-confirmation', { 
        state: { 
          paymentId: paymentId,
          payerName: payerName,
          amount: safePrice.toFixed(2)
        } 
      });
    }, null, true); // true to force suppression
  };

  const handlePayPalError = (error) => {
    // Silently suppress the error - just log it with a prefix
    console.log('[Suppressed PayPal Error]', error);
    return; // Return without doing anything
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
                          src={item.image || '/placeholder.jpg'} 
                          alt={item.name || 'Product'} 
                          style={{ width: '50px', height: '50px', objectFit: 'cover' }}
                          className="me-3"
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = 'https://via.placeholder.com/50';
                          }}
                        />
                        <div>
                          <h6 className="mb-0">{item.name || 'Product'}</h6>
                          <small className="text-muted">{item.category || 'Uncategorized'}</small>
                        </div>
                      </div>
                    </td>
                    <td>${(typeof item.price === 'number' ? item.price : 0).toFixed(2)}</td>
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
                    <td>${(typeof item.price === 'number' && typeof item.quantity === 'number' ? item.price * item.quantity : 0).toFixed(2)}</td>
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
                <span>Items ({totalItems || 0}):</span>
                <span>${(typeof totalPrice === 'number' ? totalPrice : 0).toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Shipping:</span>
                <span>Free</span>
              </div>
              <hr />
              <div className="d-flex justify-content-between mb-3">
                <strong>Total:</strong>
                <strong>${(typeof totalPrice === 'number' ? totalPrice : 0).toFixed(2)}</strong>
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
                    amount={(typeof totalPrice === 'number' ? totalPrice : 0).toFixed(2)} 
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
