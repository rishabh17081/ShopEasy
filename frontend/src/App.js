import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import ProductDetails from './pages/ProductDetails';
import Login from './pages/Login';
import Register from './pages/Register';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import OrderConfirmation from './pages/OrderConfirmation';
import PaymentMethods from './pages/PaymentMethods';
import ChatbotPage from './pages/ChatbotPage';
import { CartProvider } from './contexts/CartContext';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import { setupGlobalErrorSuppression, setupConsoleErrorSuppression } from './utils/errorHandling';

function App() {
  // Set up global error handlers
  useEffect(() => {
    // Set up global error suppression
    const cleanupGlobalErrors = setupGlobalErrorSuppression();
    
    // Set up console.error suppression
    const cleanupConsoleErrors = setupConsoleErrorSuppression();
    
    // Cleanup function
    return () => {
      cleanupGlobalErrors();
      cleanupConsoleErrors();
    };
  }, []);

  return (
    <ErrorBoundary pathsToSuppress={['/cart']}>
      <AuthProvider>
        <CartProvider>
          <Router>
            <Header />
            <div className="container mt-4">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/product/:id" element={<ProductDetails />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/cart" element={
                  <ErrorBoundary suppressErrors={true}>
                    <Cart />
                  </ErrorBoundary>
                } />
                <Route path="/checkout" element={<Checkout />} />
                <Route path="/order-confirmation" element={<OrderConfirmation />} />
                <Route path="/payment-methods" element={<PaymentMethods />} />
                <Route path="/chatbot" element={<ChatbotPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </Router>
        </CartProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
