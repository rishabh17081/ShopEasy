import React, { createContext, useState, useEffect } from 'react';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPrice, setTotalPrice] = useState(0);

  useEffect(() => {
    try {
      // Load cart from localStorage on mount
      const savedCart = localStorage.getItem('cart');
      if (savedCart) {
        try {
          const parsedCart = JSON.parse(savedCart);
          
          // Validate the parsed cart data
          if (!Array.isArray(parsedCart)) {
            console.error("Saved cart is not an array:", parsedCart);
            return;
          }
          
          // Filter out any invalid items
          const validCart = parsedCart.filter(item => {
            if (!item || !item.id || typeof item.price !== 'number' || typeof item.quantity !== 'number') {
              console.error("Invalid item in saved cart:", item);
              return false;
            }
            return true;
          });
          
          setCartItems(validCart);
        } catch (parseError) {
          console.error("Error parsing saved cart:", parseError);
          // If there's an error parsing, reset the cart
          localStorage.removeItem('cart');
          setCartItems([]);
        }
      }
    } catch (error) {
      console.error("Error loading cart from localStorage:", error);
      setCartItems([]);
    }
  }, []);

  useEffect(() => {
    try {
      // Update totals when cart items change
      let items = 0;
      let price = 0;
      
      if (!Array.isArray(cartItems)) {
        console.error("Cart items is not an array:", cartItems);
        return;
      }
      
      cartItems.forEach(item => {
        try {
          if (!item || typeof item.quantity !== 'number' || typeof item.price !== 'number') {
            console.error("Invalid item in cart:", item);
            return;
          }
          items += item.quantity;
          price += item.price * item.quantity;
        } catch (itemError) {
          console.error("Error processing cart item:", itemError, item);
        }
      });
      
      setTotalItems(items);
      setTotalPrice(price);
      
      // Save to localStorage
      try {
        localStorage.setItem('cart', JSON.stringify(cartItems));
      } catch (storageError) {
        console.error("Error saving cart to localStorage:", storageError);
      }
    } catch (error) {
      console.error("Error updating cart totals:", error);
    }
  }, [cartItems]);

  const addToCart = (product, quantity = 1) => {
    try {
      // Handle null or undefined product gracefully
      if (!product) {
        console.error("Product is null or undefined");
        return;
      }
      
      // Ensure product has an id, even if it's a generated one
      const safeProduct = {
        ...product,
        id: product.id || Date.now(), // Use timestamp as fallback id
        price: typeof product.price === 'number' ? product.price : 0,
        name: product.name || 'Unknown Product',
        image: product.image || 'https://via.placeholder.com/150',
        category: product.category || 'Uncategorized'
      };
      
      // Validate quantity
      const validQuantity = Math.max(1, parseInt(quantity) || 1);
      
      setCartItems(prevItems => {
        try {
          // Ensure prevItems is an array
          const safeItems = Array.isArray(prevItems) ? prevItems : [];
          
          // Check if the product is already in cart
          const existingItemIndex = safeItems.findIndex(item => 
            item && item.id && item.id === safeProduct.id
          );
          
          if (existingItemIndex >= 0) {
            // If product exists, update quantity
            const updatedItems = [...safeItems];
            updatedItems[existingItemIndex] = {
              ...updatedItems[existingItemIndex],
              quantity: (updatedItems[existingItemIndex].quantity || 0) + validQuantity
            };
            return updatedItems;
          } else {
            // If product doesn't exist, add new item
            return [...safeItems, { ...safeProduct, quantity: validQuantity }];
          }
        } catch (innerError) {
          console.error("Error updating cart items:", innerError);
          return Array.isArray(prevItems) ? prevItems : []; // Return unchanged cart on error
        }
      });
    } catch (error) {
      console.error("Error in addToCart:", error);
    }
  };

  const removeFromCart = (productId) => {
    try {
      // Validate product ID
      if (!productId) {
        console.error("Invalid product ID for removal:", productId);
        return;
      }
      
      setCartItems(prevItems => {
        try {
          if (!Array.isArray(prevItems)) {
            console.error("Cart items is not an array:", prevItems);
            return prevItems;
          }
          
          return prevItems.filter(item => {
            if (!item) {
              console.error("Invalid item in cart:", item);
              return false; // Remove invalid items
            }
            return item.id !== productId;
          });
        } catch (innerError) {
          console.error("Error filtering cart items:", innerError);
          return prevItems; // Return unchanged cart on error
        }
      });
    } catch (error) {
      console.error("Error in removeFromCart:", error);
    }
  };

  const updateQuantity = (productId, quantity) => {
    try {
      // Validate inputs
      if (!productId) {
        console.error("Invalid product ID for quantity update:", productId);
        return;
      }
      
      // Parse quantity to ensure it's a number
      const validQuantity = parseInt(quantity);
      if (isNaN(validQuantity)) {
        console.error("Invalid quantity value:", quantity);
        return;
      }
      
      // Remove item if quantity is zero or negative
      if (validQuantity <= 0) {
        removeFromCart(productId);
        return;
      }
      
      setCartItems(prevItems => {
        try {
          if (!Array.isArray(prevItems)) {
            console.error("Cart items is not an array:", prevItems);
            return prevItems;
          }
          
          return prevItems.map(item => {
            if (!item) {
              console.error("Invalid item in cart:", item);
              return item;
            }
            return item.id === productId ? { ...item, quantity: validQuantity } : item;
          });
        } catch (innerError) {
          console.error("Error updating cart items:", innerError);
          return prevItems; // Return unchanged cart on error
        }
      });
    } catch (error) {
      console.error("Error in updateQuantity:", error);
    }
  };

  const clearCart = () => {
    try {
      setCartItems([]);
      
      // Also clear localStorage
      try {
        localStorage.removeItem('cart');
      } catch (storageError) {
        console.error("Error clearing cart from localStorage:", storageError);
      }
    } catch (error) {
      console.error("Error clearing cart:", error);
    }
  };

  const value = {
    cartItems,
    totalItems,
    totalPrice,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};
