import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import SavedCards from '../components/payment/SavedCards';
import AddCardForm from '../components/payment/AddCardForm';
import { getUserCards } from '../services/payment/cardService';

const PaymentMethods = () => {
  const { currentUser } = useContext(AuthContext);
  const [showAddCardForm, setShowAddCardForm] = useState(false);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (currentUser) {
      fetchUserCards();
    } else {
      setLoading(false);
    }
  }, [currentUser]);

  const fetchUserCards = async () => {
    setLoading(true);
    try {
      const response = await getUserCards(currentUser.id);
      if (response.success) {
        setCards(response.data);
      } else {
        setError(response.error || 'Failed to load your saved cards');
      }
    } catch (err) {
      setError('An error occurred while fetching your payment methods');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCardAdded = (newCard) => {
    setCards([...cards, newCard]);
    setShowAddCardForm(false);
  };

  if (!currentUser) {
    return (
      <div className="container mt-5">
        <div className="alert alert-warning">
          Please <Link to="/login">login</Link> to manage your payment methods.
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-md-8 offset-md-2">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h2 className="mb-0">Payment Methods</h2>
              {!showAddCardForm && (
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowAddCardForm(true)}
                >
                  Add New Card
                </button>
              )}
            </div>
            
            <div className="card-body">
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}
              
              {loading ? (
                <div className="text-center py-4">
                  <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <p className="mt-2">Loading your payment methods...</p>
                </div>
              ) : (
                <>
                  {showAddCardForm ? (
                    <div className="mb-4">
                      <h5 className="mb-3">Add New Card</h5>
                      <AddCardForm 
                        userId={currentUser.id}
                        onCardAdded={handleCardAdded}
                        onCancel={() => setShowAddCardForm(false)}
                      />
                    </div>
                  ) : (
                    <>
                      {cards.length === 0 ? (
                        <div className="text-center py-4">
                          <p>You don't have any saved payment methods yet.</p>
                          <button 
                            className="btn btn-primary"
                            onClick={() => setShowAddCardForm(true)}
                          >
                            Add Your First Card
                          </button>
                        </div>
                      ) : (
                        <div>
                          <h5 className="mb-3">Your Saved Cards</h5>
                          <SavedCards showManage={true} />
                          <div className="card-info mt-4">
                            <h6>About Your Saved Cards</h6>
                            <ul className="text-muted">
                              <li>Your card information is securely stored.</li>
                              <li>We never store your CVV code.</li>
                              <li>You can set a default card for faster checkout.</li>
                              <li>Any saved card can be removed at any time.</li>
                            </ul>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentMethods;