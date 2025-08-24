#!/usr/bin/env python3
"""Create a sample SQLite database for testing."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def create_sample_database():
    """Create a sample SQLite database with test data."""
    
    # Create test_data directory if it doesn't exist
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(exist_ok=True)
    
    # Create resources directory if it doesn't exist
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)
    
    # Database path
    db_path = test_data_dir / "sample.db"
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Insert sample data
    sample_users = [
        ('john_doe', 'john@example.com', 'John Doe'),
        ('jane_smith', 'jane@example.com', 'Jane Smith'),
        ('bob_wilson', 'bob@example.com', 'Bob Wilson'),
        ('alice_johnson', 'alice@example.com', 'Alice Johnson'),
        ('charlie_brown', 'charlie@example.com', 'Charlie Brown')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO users (username, email, full_name) VALUES (?, ?, ?)",
        sample_users
    )
    
    sample_products = [
        ('Laptop', 'High-performance laptop with 16GB RAM', 1299.99, 50, 'Electronics'),
        ('Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 200, 'Electronics'),
        ('Office Chair', 'Comfortable ergonomic office chair', 399.99, 75, 'Furniture'),
        ('Standing Desk', 'Adjustable height standing desk', 599.99, 30, 'Furniture'),
        ('USB-C Hub', '7-in-1 USB-C hub adapter', 49.99, 150, 'Electronics'),
        ('Monitor 27"', '4K UHD 27-inch monitor', 449.99, 40, 'Electronics'),
        ('Desk Lamp', 'LED desk lamp with adjustable brightness', 39.99, 100, 'Furniture'),
        ('Keyboard', 'Mechanical gaming keyboard', 89.99, 80, 'Electronics'),
        ('Webcam', '1080p HD webcam with microphone', 69.99, 120, 'Electronics'),
        ('Notebook', 'A5 hardcover notebook', 12.99, 500, 'Stationery')
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO products (name, description, price, stock_quantity, category) VALUES (?, ?, ?, ?, ?)",
        sample_products
    )
    
    # Create some sample orders
    cursor.execute("INSERT OR IGNORE INTO orders (user_id, total_amount, status) VALUES (1, 1329.98, 'completed')")
    cursor.execute("INSERT OR IGNORE INTO orders (user_id, total_amount, status) VALUES (2, 449.99, 'completed')")
    cursor.execute("INSERT OR IGNORE INTO orders (user_id, total_amount, status) VALUES (3, 89.99, 'processing')")
    cursor.execute("INSERT OR IGNORE INTO orders (user_id, total_amount, status) VALUES (1, 649.98, 'pending')")
    
    # Add order items
    cursor.execute("INSERT OR IGNORE INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 1, 1, 1299.99)")
    cursor.execute("INSERT OR IGNORE INTO order_items (order_id, product_id, quantity, unit_price) VALUES (1, 2, 1, 29.99)")
    cursor.execute("INSERT OR IGNORE INTO order_items (order_id, product_id, quantity, unit_price) VALUES (2, 6, 1, 449.99)")
    cursor.execute("INSERT OR IGNORE INTO order_items (order_id, product_id, quantity, unit_price) VALUES (3, 8, 1, 89.99)")
    cursor.execute("INSERT OR IGNORE INTO order_items (order_id, product_id, quantity, unit_price) VALUES (4, 4, 1, 599.99)")
    cursor.execute("INSERT OR IGNORE INTO order_items (order_id, product_id, quantity, unit_price) VALUES (4, 5, 1, 49.99)")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ Sample database created at: {db_path}")
    
    # Create metadata file
    metadata = {
        "server_name": "talk-2-tables-mcp",
        "database_path": str(db_path),
        "description": "Sample e-commerce database for demonstration purposes",
        "business_use_cases": [
            "Customer order analysis",
            "Product inventory management",
            "Sales reporting and analytics",
            "User activity tracking",
            "Revenue analysis by product category"
        ],
        "tables": {
            "users": {
                "description": "Customer user accounts",
                "columns": ["id", "username", "email", "full_name", "created_at", "is_active"],
                "row_count": 5
            },
            "products": {
                "description": "Product catalog",
                "columns": ["id", "name", "description", "price", "stock_quantity", "category", "created_at"],
                "row_count": 10
            },
            "orders": {
                "description": "Customer orders",
                "columns": ["id", "user_id", "order_date", "total_amount", "status"],
                "row_count": 4
            },
            "order_items": {
                "description": "Individual items within orders",
                "columns": ["id", "order_id", "product_id", "quantity", "unit_price"],
                "row_count": 6
            }
        },
        "last_updated": datetime.now().isoformat()
    }
    
    metadata_path = resources_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Metadata file created at: {metadata_path}")
    
    return db_path, metadata_path

if __name__ == "__main__":
    create_sample_database()