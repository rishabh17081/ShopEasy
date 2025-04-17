import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Chatbot from '../components/Chatbot';
import Header from '../components/Header';

const ChatbotPage = () => {
  return (
    <>
      <Header />
      <Container className="mt-4 mb-5">
        <Row>
          <Col>
            <h2 className="mb-4">E-commerce Assistant</h2>
            <p className="mb-4">
              Ask our AI assistant about products, orders, payment options, or any other questions you have about our e-commerce platform.
              The assistant can help you with various tasks including creating invoices, listing products, and more.
            </p>
          </Col>
        </Row>
        <Row>
          <Col>
            <Chatbot />
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default ChatbotPage;
