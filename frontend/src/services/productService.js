// This is a temporary service that provides mock product data
// In a real application, this would fetch data from an API

const dummyProducts = [
  {
    id: 1,
    name: 'Wireless Bluetooth Headphones',
    description: 'High-quality wireless headphones with noise cancellation technology, providing crystal clear sound and comfort for extended use.',
    price: 89.99,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&q=80',
    category: 'Electronics',
    inventory: 25
  },
  {
    id: 2,
    name: 'Organic Cotton T-Shirt',
    description: 'Soft, comfortable t-shirt made from 100% organic cotton. Available in various colors and sizes.',
    price: 24.99,
    image: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop&q=80',
    category: 'Clothing',
    inventory: 50
  },
  {
    id: 3,
    name: 'Stainless Steel Water Bottle',
    description: 'Eco-friendly, double-walled insulated water bottle that keeps your drinks cold for 24 hours or hot for 12 hours.',
    price: 29.99,
    image: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=300&h=300&fit=crop&q=80',
    category: 'Home',
    inventory: 35
  },
  {
    id: 4,
    name: 'Smartphone Gimbal Stabilizer',
    description: 'Create smooth, professional-looking videos with this 3-axis smartphone gimbal. Compatible with most smartphones.',
    price: 119.99,
    image: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=300&h=300&fit=crop&q=80',
    category: 'Electronics',
    inventory: 15
  },
  {
    id: 5,
    name: 'Yoga Mat',
    description: 'Non-slip, eco-friendly yoga mat with perfect cushioning for comfort during your practice.',
    price: 39.99,
    image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=300&h=300&fit=crop&q=80',
    category: 'Fitness',
    inventory: 40
  },
  {
    id: 6,
    name: 'Smartwatch',
    description: 'Track your fitness, sleep, and notifications with this sleek, feature-packed smartwatch.',
    price: 199.99,
    image: 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=300&h=300&fit=crop&q=80',
    category: 'Electronics',
    inventory: 18
  },
  {
    id: 7,
    name: 'Plant-Based Protein Powder',
    description: 'Complete, plant-based protein with all essential amino acids. 25g of protein per serving.',
    price: 34.99,
    image: 'https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=300&h=300&fit=crop&q=80',
    category: 'Fitness',
    inventory: 30
  },
  {
    id: 8,
    name: 'Mac book pro 14 inches',
    description: 'Mac book pro',
    price: 34.99,
    image: 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=300&h=300&fit=crop&q=80',
    category: 'Fitness',
    inventory: 30
  }
];

// Simulate API delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Get all products
export const getDummyProducts = async () => {
  await delay(800); // Simulate network delay
  return [...dummyProducts];
};

// Get product by ID
export const getProductById = async (id) => {
  await delay(500); // Simulate network delay
  const product = dummyProducts.find(p => p.id === id);
  if (!product) {
    throw new Error('Product not found');
  }
  return {...product};
};

// Search products
export const searchProducts = async (query) => {
  await delay(600); // Simulate network delay
  const lowerQuery = query.toLowerCase();
  return dummyProducts.filter(product => 
    product.name.toLowerCase().includes(lowerQuery) || 
    product.description.toLowerCase().includes(lowerQuery) ||
    product.category.toLowerCase().includes(lowerQuery)
  );
};

// Get products by category
export const getProductsByCategory = async (category) => {
  await delay(500); // Simulate network delay
  if (category.toLowerCase() === 'all') {
    return [...dummyProducts];
  }
  return dummyProducts.filter(product => 
    product.category.toLowerCase() === category.toLowerCase()
  );
};