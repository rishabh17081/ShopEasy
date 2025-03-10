import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';
import { getProductById } from '../services/productService';

const ProductDetails = () => {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const { addToCart } = useContext(CartContext);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const data = await getProductById(parseInt(id));
        setProduct(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching product:', error);
        setLoading(false);
      }
    };
    
    fetchProduct();
  }, [id]);

  const handleAddToCart = () => {
    addToCart(product, quantity);
    alert(`${quantity} ${product.name} added to cart!`);
  };

  if (loading) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="alert alert-danger" role="alert">
        Product not found.
      </div>
    );
  }

  return (
    <div className="container">
      <div className="row mb-4">
        <div className="col-12">
          <Link to="/" className="btn btn-outline-secondary mb-3">
            &larr; Back to Products
          </Link>
        </div>
      </div>
      
      <div className="row">
        <div className="col-md-6 mb-4">
          <img 
            src={product.image} 
            alt={product.name} 
            className="img-fluid rounded" 
          />
        </div>
        
        <div className="col-md-6">
          <h1 className="mb-3">{product.name}</h1>
          <p className="text-muted mb-3">Category: {product.category}</p>
          <h4 className="text-primary mb-4">${product.price.toFixed(2)}</h4>
          
          <p className="mb-4">{product.description}</p>
          
          <div className="mb-4">
            <div className="input-group mb-3" style={{ maxWidth: '200px' }}>
              <button 
                className="btn btn-outline-secondary" 
                type="button"
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
              >
                -
              </button>
              <input 
                type="number" 
                className="form-control text-center" 
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                min="1"
              />
              <button 
                className="btn btn-outline-secondary" 
                type="button"
                onClick={() => setQuantity(quantity + 1)}
              >
                +
              </button>
            </div>
          </div>
          
          <button 
            className="btn btn-primary btn-lg me-3"
            onClick={handleAddToCart}
          >
            Add to Cart
          </button>
          
          <Link to="/cart" className="btn btn-success btn-lg">
            Go to Cart
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ProductDetails;
