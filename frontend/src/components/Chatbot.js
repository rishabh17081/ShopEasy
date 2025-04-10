import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, Button, Form, Spinner, Alert } from 'react-bootstrap';
import '../styles/Chatbot.css';
import { FaComments, FaTimes, FaExpand, FaCompress } from 'react-icons/fa';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const messagesEndRef = useRef(null);
  const chatbotRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Handle clicking outside the chatbot to close it
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (chatbotRef.current && !chatbotRef.current.contains(event.target) && isOpen) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Format tool calls for display
  const formatToolCalls = (toolCalls) => {
    if (!toolCalls || toolCalls.length === 0) return null;
    
    return (
      <div className="tool-calls">
        <h6>Tool Calls:</h6>
        {toolCalls.map((toolCall, index) => (
          <div key={index} className="tool-call">
            <div className="tool-name">{toolCall.name}</div>
            <pre className="tool-input">{JSON.stringify(toolCall.input, null, 2)}</pre>
          </div>
        ))}
      </div>
    );
  };

  // Format tool results for display
  const formatToolResults = (toolResults) => {
    if (!toolResults || toolResults.length === 0) return null;
    
    return (
      <div className="tool-results">
        <h6>Tool Results:</h6>
        {toolResults.map((result, index) => {
          // Check if this is a chart result
          if (result && result.chart && result.chart_type === 'pie') {
            return (
              <div key={index} className="tool-result chart-result">
                <h5>{result.chart_title || 'Chart'}</h5>
                <div className="chart-container">
                  <img 
                    src={`data:image/png;base64,${result.chart}`} 
                    alt={result.chart_title || 'Chart'} 
                    className="result-chart"
                  />
                </div>
                {result.insights && (
                  <div className="chart-insights">
                    <h6>Insights:</h6>
                    {result.insights.summary && (
                      <p className="insight-summary">{result.insights.summary}</p>
                    )}
                    {result.insights.financial && (
                      <div className="financial-insights">
                        <p><strong>Total Amount:</strong> {result.insights.financial.total_amount.toFixed(2)} {result.insights.financial.currency}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          }
          
          // Default display for non-chart results
          return (
            <div key={index} className="tool-result">
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          );
        })}
      </div>
    );
  };

  // Handle sending a message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Send request to backend
      console.log('Sending request to backend:', {
        query: input,
        chat_history: chatHistory,
        execute_tools: true
      });
      
      const response = await axios.post('http://localhost:5001/api/chatbot/query', {
        query: input,
        chat_history: chatHistory,
        execute_tools: true
      });

      console.log('Received response from backend:', response.data);

      // Update chat history for context
      setChatHistory([...chatHistory, userMessage]);

      // Add assistant response to chat
      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        toolCalls: response.data.tool_calls,
        toolResults: response.data.tool_results,
        followUpResponse: response.data.follow_up_response
      };
      
      setMessages([...messages, userMessage, assistantMessage]);
      
      // Add assistant message to chat history
      setChatHistory([...chatHistory, userMessage, { role: 'assistant', content: response.data.response }]);
      
    } catch (err) {
      console.error('Error sending message:', err);
      console.error('Error details:', {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data
      });
      setError(`Failed to send message: ${err.message}. Status: ${err.response?.status || 'unknown'}`);
    } finally {
      setLoading(false);
    }
  };

  // Toggle chatbot visibility
  const toggleChatbot = () => {
    setIsOpen(!isOpen);
  };
  
  // Toggle maximize/minimize
  const toggleMaximize = (e) => {
    e.stopPropagation();
    setIsMaximized(!isMaximized);
  };

  return (
    <div className="chatbot-wrapper">
      {!isOpen && (
        <Button 
          className="chatbot-toggle-btn" 
          onClick={toggleChatbot}
          aria-label="Open chat assistant"
        >
          <FaComments /> Chat
        </Button>
      )}
      
      {isOpen && (
        <Card className={`chatbot-container ${isMaximized ? 'maximized' : ''}`} ref={chatbotRef}>
          <Card.Header className="chatbot-header">
            <h5>E-commerce Assistant</h5>
            <div className="chatbot-controls">
              <Button 
                variant="link" 
                className="maximize-btn" 
                onClick={toggleMaximize}
                aria-label={isMaximized ? "Minimize chat assistant" : "Maximize chat assistant"}
              >
                {isMaximized ? <FaCompress /> : <FaExpand />}
              </Button>
              <Button 
                variant="link" 
                className="close-btn" 
                onClick={toggleChatbot}
                aria-label="Close chat assistant"
              >
                <FaTimes />
              </Button>
            </div>
          </Card.Header>
          <Card.Body className="chatbot-messages">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <p>Ask me anything about our products, orders, or payment options!</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                {message.content}
              </div>
              {message.toolCalls && formatToolCalls(message.toolCalls)}
              {message.toolResults && formatToolResults(message.toolResults)}
              {message.followUpResponse && (
                <div className="follow-up-response">
                  <h6>Follow-up:</h6>
                  <div>{message.followUpResponse}</div>
                </div>
              )}
            </div>
          ))
        )}
        {loading && (
          <div className="message assistant">
            <Spinner animation="border" size="sm" /> Thinking...
          </div>
        )}
        {error && <Alert variant="danger">{error}</Alert>}
        <div ref={messagesEndRef} />
          </Card.Body>
          <Card.Footer>
            <Form onSubmit={handleSendMessage}>
              <div className="input-container">
                <Form.Control
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message..."
                  disabled={loading}
                />
                <Button 
                  variant="primary" 
                  type="submit" 
                  disabled={loading || !input.trim()}
                >
                  Send
                </Button>
              </div>
            </Form>
          </Card.Footer>
        </Card>
      )}
    </div>
  );
};

export default Chatbot;
