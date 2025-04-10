import React, { useContext, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';
import { AuthContext } from '../contexts/AuthContext';
import { safeExecute } from '../utils/errorHandling';
import { PayPalScriptProvider, PayPalButtons } from '@paypal/react-paypal-js';

const Cart = () => {
  const { cartItems, totalItems, totalPrice, updateQuantity, removeFromCart, clearCart } = useContext(CartContext);
  const { currentUser } = useContext(AuthContext);
  const navigate = useNavigate();
  const [paypalLoaded, setPaypalLoaded] = useState(false);
  
  // PayPal initial options
  const initialOptions = {
    clientId: "AdlchHuRCMtJU8TEV1808gahBAlgSLZJULcVEl5-sOgIwLNbIGqK6L4PvBW3v-eE8zLn9LYaLtWsIZP3", // Replace with your PayPal client ID in production
    currency: "USD",
    intent: "capture",
  };

  const handleCheckout = () => {
    // Bypass login requirement for testing
    navigate('/checkout');
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
                
                <div className="mt-3">
                  <hr className="my-3" />
                  <h6 className="text-center mb-2">Or pay with PayPal</h6>
                  <PayPalScriptProvider options={initialOptions}>
                    <PayPalButtons 
                      style={{ layout: "vertical" }}
                      createOrder={(data, actions) => {
                        return actions.order.create({
                          purchase_units: [
                            {
                              amount: {
                                value: (typeof totalPrice === 'number' ? totalPrice : 0).toFixed(2),
                              },
                              description: `Order with ${totalItems} items`,
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
