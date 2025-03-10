import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { CartContext } from '../contexts/CartContext';

const ProductCard = ({ product }) => {
  const { addToCart } = useContext(CartContext);
  
  const handleAddToCart = (e) => {
    e.preventDefault();
    addToCart(product);
    alert(`${product.name} added to cart!`);
  };
  
  return (
    <div className="card product-card h-100">
      <img 
        src={product.image} 
        className="card-img-top p-3 product-img" 
        alt={product.name} 
      />
      <div className="card-body d-flex flex-column">
        <h5 className="card-title">{product.name}</h5>
        <p className="card-text text-muted mb-1">{product.category}</p>
        <p className="card-text flex-grow-1">{product.description.substring(0, 80)}...</p>
        <div className="d-flex justify-content-between align-items-center mt-auto">
          <h5 className="mb-0">${product.price.toFixed(2)}</h5>
          <div>
            <button 
              className="btn btn-sm btn-primary me-2"
              onClick={handleAddToCart}
            >
              Add to Cart
            </button>
            <Link 
              to={`/product/${product.id}`} 
              className="btn btn-sm btn-outline-secondary"
            >
              Details
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
