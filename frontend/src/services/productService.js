// This is a temporary service that provides mock product data
// In a real application, this would fetch data from an API

const dummyProducts = [
  {
    id: 1,
    name: 'Wireless Bluetooth Headphones',
    description: 'High-quality wireless headphones with noise cancellation technology, providing crystal clear sound and comfort for extended use.',
    price: 89.99,
    image: 'https://via.placeholder.com/300x300?text=Headphones',
    category: 'Electronics',
    inventory: 25
  },
  {
    id: 2,
    name: 'Organic Cotton T-Shirt',
    description: 'Soft, comfortable t-shirt made from 100% organic cotton. Available in various colors and sizes.',
    price: 24.99,
    image: 'https://via.placeholder.com/300x300?text=T-Shirt',
    category: 'Clothing',
    inventory: 50
  },
  {
    id: 3,
    name: 'Stainless Steel Water Bottle',
    description: 'Eco-friendly, double-walled insulated water bottle that keeps your drinks cold for 24 hours or hot for 12 hours.',
    price: 29.99,
    image: 'https://via.placeholder.com/300x300?text=Water+Bottle',
    category: 'Home',
    inventory: 35
  },
  {
    id: 4,
    name: 'Smartphone Gimbal Stabilizer',
    description: 'Create smooth, professional-looking videos with this 3-axis smartphone gimbal. Compatible with most smartphones.',
    price: 119.99,
    image: 'https://via.placeholder.com/300x300?text=Gimbal',
    category: 'Electronics',
    inventory: 15
  },
  {
    id: 5,
    name: 'Yoga Mat',
    description: 'Non-slip, eco-friendly yoga mat with perfect cushioning for comfort during your practice.',
    price: 39.99,
    image: 'https://via.placeholder.com/300x300?text=Yoga+Mat',
    category: 'Fitness',
    inventory: 40
  },
  {
    id: 6,
    name: 'Wooden Cutting Board',
    description: 'Handcrafted, sustainable wooden cutting board, perfect for food preparation and serving.',
    price: 49.99,
    image: 'https://via.placeholder.com/300x300?text=Cutting+Board',
    category: 'Home',
    inventory: 20
  },
  {
    id: 7,
    name: 'Smartwatch',
    description: 'Track your fitness, sleep, and notifications with this sleek, feature-packed smartwatch.',
    price: 199.99,
    image: 'https://via.placeholder.com/300x300?text=Smartwatch',
    category: 'Electronics',
    inventory: 18
  },
  {
    id: 8,
    name: 'Plant-Based Protein Powder',
    description: 'Complete, plant-based protein with all essential amino acids. 25g of protein per serving.',
    price: 34.99,
    image: 'https://via.placeholder.com/300x300?text=Protein',
    category: 'Fitness',
    inventory: 30
  },
  {
    id: 9,
    name: 'Mac book pro 14 inches ',
    description: 'Mac book pro',
    price: 34.99,
    image: 'https://via.placeholder.com/300x300?text=Protein',
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
