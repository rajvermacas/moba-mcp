#!/usr/bin/env python3
"""Create a metadata-only SQLite database for multi-MCP server testing."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def create_sample_database():
    """Create a SQLite database with only metadata tables for multi-MCP testing."""
    
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
    
    # Create only metadata tables (original tables exist in a different MCP server)
    # Note: Foreign key constraints removed as referenced tables are in another database
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_behavior_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_count INTEGER DEFAULT 0,
            avg_session_duration_min DECIMAL(10,2),
            bounce_rate DECIMAL(5,2),
            device_type TEXT,
            browser TEXT,
            geo_location TEXT,
            referral_source TEXT,
            churn_risk_score DECIMAL(3,2),
            last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- user_id references users table in another MCP server
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_performance_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            views_last_30d INTEGER DEFAULT 0,
            conversion_rate DECIMAL(5,2),
            return_rate DECIMAL(5,2),
            avg_cart_abandonment DECIMAL(5,2),
            seasonal_demand_score DECIMAL(3,2),
            competitor_price DECIMAL(10,2),
            market_trend TEXT,
            last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- product_id references products table in another MCP server
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_logistics_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            warehouse_id TEXT,
            picker_id TEXT,
            packing_time_min INTEGER,
            shipping_carrier TEXT,
            tracking_url TEXT,
            delivery_attempts INTEGER DEFAULT 1,
            carbon_footprint DECIMAL(10,2),
            insurance_amount DECIMAL(10,2)
            -- order_id references orders table in another MCP server
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_channel TEXT DEFAULT 'email',
            language_preference TEXT DEFAULT 'en',
            currency_preference TEXT DEFAULT 'USD',
            newsletter_subscribed BOOLEAN DEFAULT 0,
            marketing_consent BOOLEAN DEFAULT 0,
            theme_preference TEXT DEFAULT 'light',
            accessibility_needs TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- user_id references users table in another MCP server
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_supplier_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            manufacturer_name TEXT,
            manufacturer_country TEXT,
            import_duty_rate DECIMAL(5,2),
            certification_type TEXT,
            sustainability_score INTEGER,
            lead_time_days INTEGER,
            minimum_order_qty INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- product_id references products table in another MCP server
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_financial_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            payment_processor TEXT,
            transaction_fee DECIMAL(10,2),
            currency_used TEXT DEFAULT 'USD',
            exchange_rate DECIMAL(10,4) DEFAULT 1.0000,
            tax_jurisdiction TEXT,
            invoice_number TEXT,
            accounting_period TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- order_id references orders table in another MCP server
        )
    """)
    
    # Insert sample data for user_behavior_metadata
    # user_id values correspond to users in another MCP server
    user_behavior_data = [
        (1, 45, 28.5, 0.12, 'Desktop', 'Chrome', 'New York, USA', 'Google Search', 0.15),
        (2, 23, 15.3, 0.28, 'Mobile', 'Safari', 'London, UK', 'Direct', 0.35),
        (3, 67, 42.1, 0.08, 'Desktop', 'Firefox', 'Berlin, Germany', 'Facebook Ads', 0.10),
        (4, 12, 8.7, 0.45, 'Tablet', 'Safari', 'Tokyo, Japan', 'Email Campaign', 0.65),
        (5, 89, 55.2, 0.05, 'Desktop', 'Edge', 'Sydney, Australia', 'Instagram', 0.08)
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO user_behavior_metadata 
        (user_id, session_count, avg_session_duration_min, bounce_rate, device_type, 
         browser, geo_location, referral_source, churn_risk_score) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        user_behavior_data
    )
    
    # Insert sample data for product_performance_metadata
    # product_id values correspond to products in another MCP server
    product_performance_data = [
        (1, 3456, 0.045, 0.02, 0.15, 0.85, 1199.99, 'Increasing'),
        (2, 8912, 0.082, 0.01, 0.08, 0.45, 24.99, 'Stable'),
        (3, 1234, 0.032, 0.05, 0.22, 0.60, 379.99, 'Decreasing'),
        (4, 2345, 0.028, 0.03, 0.18, 0.70, 549.99, 'Stable'),
        (5, 5678, 0.065, 0.02, 0.12, 0.55, 44.99, 'Increasing'),
        (6, 4321, 0.055, 0.04, 0.20, 0.80, 399.99, 'Increasing'),
        (7, 2109, 0.072, 0.01, 0.10, 0.40, 34.99, 'Stable'),
        (8, 6789, 0.068, 0.03, 0.14, 0.65, 79.99, 'Increasing'),
        (9, 3210, 0.051, 0.02, 0.16, 0.50, 59.99, 'Stable'),
        (10, 987, 0.095, 0.01, 0.05, 0.30, 10.99, 'Decreasing')
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO product_performance_metadata 
        (product_id, views_last_30d, conversion_rate, return_rate, avg_cart_abandonment, 
         seasonal_demand_score, competitor_price, market_trend) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        product_performance_data
    )
    
    # Insert sample data for order_logistics_metadata
    # order_id values correspond to orders in another MCP server
    order_logistics_data = [
        (1, 'WH-001', 'PICKER-042', 15, 'FedEx', 'https://fedex.com/track/123456', 1, 2.5, 50.00),
        (2, 'WH-002', 'PICKER-017', 12, 'UPS', 'https://ups.com/track/789012', 1, 1.8, 25.00),
        (3, 'WH-001', 'PICKER-023', 18, 'DHL', 'https://dhl.com/track/345678', 2, 2.2, 15.00),
        (4, 'WH-003', 'PICKER-009', 20, 'USPS', 'https://usps.com/track/901234', 1, 3.1, 35.00)
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO order_logistics_metadata 
        (order_id, warehouse_id, picker_id, packing_time_min, shipping_carrier, 
         tracking_url, delivery_attempts, carbon_footprint, insurance_amount) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        order_logistics_data
    )
    
    # Insert sample data for user_preferences_metadata
    # user_id values correspond to users in another MCP server
    user_preferences_data = [
        (1, 'email', 'en', 'USD', 1, 1, 'dark', None),
        (2, 'sms', 'en-GB', 'GBP', 1, 0, 'light', 'high-contrast'),
        (3, 'push', 'de', 'EUR', 0, 0, 'auto', None),
        (4, 'email', 'ja', 'JPY', 1, 1, 'light', 'large-text'),
        (5, 'email', 'en-AU', 'AUD', 0, 1, 'dark', None)
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO user_preferences_metadata 
        (user_id, notification_channel, language_preference, currency_preference, 
         newsletter_subscribed, marketing_consent, theme_preference, accessibility_needs) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        user_preferences_data
    )
    
    # Insert sample data for product_supplier_metadata
    # product_id values correspond to products in another MCP server
    product_supplier_data = [
        (1, 'TechCorp Manufacturing', 'China', 0.08, 'ISO-9001', 85, 30, 10),
        (2, 'Precision Electronics', 'Taiwan', 0.06, 'CE', 78, 14, 100),
        (3, 'Comfort Furniture Co', 'Vietnam', 0.12, 'FSC', 92, 45, 5),
        (4, 'ErgoDesign Industries', 'Malaysia', 0.10, 'GREENGUARD', 88, 60, 3),
        (5, 'ConnectTech Ltd', 'South Korea', 0.07, 'RoHS', 80, 21, 50),
        (6, 'DisplayPro Inc', 'Japan', 0.09, 'Energy Star', 95, 35, 8),
        (7, 'Lumina Lighting', 'Netherlands', 0.05, 'UL', 90, 28, 20),
        (8, 'KeyMaster Tech', 'Germany', 0.04, 'CE', 87, 25, 15),
        (9, 'VisionCam Solutions', 'Canada', 0.03, 'FCC', 82, 18, 25),
        (10, 'PaperCraft Studios', 'Italy', 0.02, 'FSC', 75, 10, 200)
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO product_supplier_metadata 
        (product_id, manufacturer_name, manufacturer_country, import_duty_rate, 
         certification_type, sustainability_score, lead_time_days, minimum_order_qty) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        product_supplier_data
    )
    
    # Insert sample data for order_financial_metadata
    # order_id values correspond to orders in another MCP server
    order_financial_data = [
        (1, 'Stripe', 38.70, 'USD', 1.0000, 'NY-US', 'INV-2024-001', '2024-Q1'),
        (2, 'PayPal', 13.05, 'USD', 1.0000, 'CA-US', 'INV-2024-002', '2024-Q1'),
        (3, 'Square', 2.61, 'USD', 1.0000, 'TX-US', 'INV-2024-003', '2024-Q1'),
        (4, 'Stripe', 18.85, 'USD', 1.0000, 'FL-US', 'INV-2024-004', '2024-Q1')
    ]
    
    cursor.executemany(
        """INSERT OR IGNORE INTO order_financial_metadata 
        (order_id, payment_processor, transaction_fee, currency_used, exchange_rate, 
         tax_jurisdiction, invoice_number, accounting_period) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        order_financial_data
    )
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ Metadata-only database created at: {db_path}")
    
    # Create metadata file
    metadata = {
        "server_name": "metadata-mcp-server",
        "database_path": str(db_path),
        "description": "Metadata-only database for multi-MCP server testing (disjoint from main data)",
        "business_use_cases": [
            "User behavior analytics",
            "Product performance monitoring",
            "Supply chain management",
            "Logistics tracking",
            "Financial reconciliation",
            "Customer preference analysis",
            "Cross-server data federation testing",
            "Multi-source JOIN operations"
        ],
        "tables": {
            "user_behavior_metadata": {
                "description": "User behavioral analytics and engagement metrics",
                "columns": ["id", "user_id", "session_count", "avg_session_duration_min", "bounce_rate", 
                          "device_type", "browser", "geo_location", "referral_source", "churn_risk_score", "last_analyzed"],
                "row_count": 5,
                "foreign_key_reference": "user_id -> users.id (in another MCP server)"
            },
            "product_performance_metadata": {
                "description": "Product performance metrics and market analysis",
                "columns": ["id", "product_id", "views_last_30d", "conversion_rate", "return_rate", 
                          "avg_cart_abandonment", "seasonal_demand_score", "competitor_price", "market_trend", "last_analyzed"],
                "row_count": 10,
                "foreign_key_reference": "product_id -> products.id (in another MCP server)"
            },
            "order_logistics_metadata": {
                "description": "Order shipping and logistics tracking",
                "columns": ["id", "order_id", "warehouse_id", "picker_id", "packing_time_min", 
                          "shipping_carrier", "tracking_url", "delivery_attempts", "carbon_footprint", "insurance_amount"],
                "row_count": 4,
                "foreign_key_reference": "order_id -> orders.id (in another MCP server)"
            },
            "user_preferences_metadata": {
                "description": "User preferences and communication settings",
                "columns": ["id", "user_id", "notification_channel", "language_preference", "currency_preference", 
                          "newsletter_subscribed", "marketing_consent", "theme_preference", "accessibility_needs", "updated_at"],
                "row_count": 5,
                "foreign_key_reference": "user_id -> users.id (in another MCP server)"
            },
            "product_supplier_metadata": {
                "description": "Product supply chain and manufacturer information",
                "columns": ["id", "product_id", "manufacturer_name", "manufacturer_country", "import_duty_rate", 
                          "certification_type", "sustainability_score", "lead_time_days", "minimum_order_qty", "last_updated"],
                "row_count": 10,
                "foreign_key_reference": "product_id -> products.id (in another MCP server)"
            },
            "order_financial_metadata": {
                "description": "Order financial and payment processing details",
                "columns": ["id", "order_id", "payment_processor", "transaction_fee", "currency_used", 
                          "exchange_rate", "tax_jurisdiction", "invoice_number", "accounting_period", "processed_at"],
                "row_count": 4,
                "foreign_key_reference": "order_id -> orders.id (in another MCP server)"
            }
        },
        "notes": {
            "data_separation": "This database contains ONLY metadata tables. Original tables (users, products, orders, order_items) exist in a separate MCP server.",
            "join_capability": "Tables use matching IDs to enable JOIN operations across MCP servers.",
            "testing_purpose": "Designed for testing multi-MCP server data federation and cross-server JOIN capabilities."
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