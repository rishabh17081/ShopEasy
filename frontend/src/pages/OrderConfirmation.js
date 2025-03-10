import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const OrderConfirmation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const paymentId = location.state?.paymentId;
  const payerName = location.state?.payerName;
  const amount = location.state?.amount;
  const orderNumber = Math.floor(Math.random() * 1000000); // Generate fake order number
  
  return (
    <div className="container text-center mt-5">
      <div className="card p-5">
        <div className="mb-4">
          <i className="fa fa-check-circle text-success" style={{ fontSize: '4rem' }}></i>
        </div>
        <h2 className="mb-3">Order Confirmed!</h2>
        <p className="mb-3">Thank you for your purchase. Your order has been received and is now being processed.</p>
        <h5 className="mb-4">Order Number: #{orderNumber}</h5>
        {paymentId && (
          <div className="alert alert-info">
            <p><strong>PayPal Payment ID:</strong> {paymentId}</p>
            {payerName && <p><strong>Payer Name:</strong> {payerName}</p>}
            {amount && <p><strong>Amount Paid:</strong> ${amount}</p>}
            <p>Your PayPal payment has been processed successfully.</p>
          </div>
        )}
        <p>You will receive an email confirmation shortly at the email address you provided.</p>
        <div className="mt-4">
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;