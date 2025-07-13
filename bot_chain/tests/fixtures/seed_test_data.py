#!/usr/bin/env python3
"""
Seed test database with consistent test data from fixtures.
This ensures all tests run against the same dataset.
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tests.fixtures.test_data import MOCK_DECISIONS

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5433),
    "database": os.getenv("DB_NAME", "ceci_bot_chain"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

def create_connection():
    """Create database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def clear_test_data(cursor):
    """Clear existing test data."""
    print("Clearing existing test data...")
    
    # Delete test decisions (1000-9999 range)
    cursor.execute("""
        DELETE FROM government_decisions 
        WHERE CAST(decision_number AS INTEGER) BETWEEN 1000 AND 9999
    """)
    
    print(f"Deleted {cursor.rowcount} test decisions")

def insert_decision(cursor, decision: Dict[str, Any]):
    """Insert a single decision."""
    query = """
        INSERT INTO government_decisions (
            id,
            decision_number,
            government_number,
            title,
            summary,
            decision_date,
            decision_url,
            topics,
            ministries,
            budget,
            is_operational,
            operative_clauses,
            created_at,
            updated_at
        ) VALUES (
            gen_random_uuid()::text,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            NOW(), NOW()
        )
        ON CONFLICT (decision_number, government_number) DO UPDATE SET
            title = EXCLUDED.title,
            summary = EXCLUDED.summary,
            decision_date = EXCLUDED.decision_date,
            decision_url = EXCLUDED.decision_url,
            topics = EXCLUDED.topics,
            ministries = EXCLUDED.ministries,
            budget = EXCLUDED.budget,
            is_operational = EXCLUDED.is_operational,
            operative_clauses = EXCLUDED.operative_clauses,
            updated_at = NOW()
    """
    
    cursor.execute(query, (
        decision["decision_number"],
        decision["government_number"],
        decision["title"],
        decision["summary"],
        decision["decision_date"],
        decision["decision_url"],
        decision["topics"],
        decision["ministries"],
        decision.get("budget", 0),
        decision.get("is_operational", False),
        decision.get("operative_clauses", [])
    ))

def seed_decisions(cursor):
    """Seed all test decisions."""
    print("\nSeeding test decisions...")
    
    for decision_num, decision_data in MOCK_DECISIONS.items():
        try:
            insert_decision(cursor, decision_data)
            print(f"✅ Inserted decision {decision_num}")
        except Exception as e:
            print(f"❌ Error inserting decision {decision_num}: {e}")

def verify_data(cursor):
    """Verify seeded data."""
    print("\nVerifying seeded data...")
    
    # Count total test decisions
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM government_decisions 
        WHERE CAST(decision_number AS INTEGER) BETWEEN 1000 AND 9999
    """)
    total = cursor.fetchone()["count"]
    print(f"Total test decisions: {total}")
    
    # Verify each government
    for gov in [36, 37, 38]:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM government_decisions 
            WHERE government_number = %s
            AND CAST(decision_number AS INTEGER) BETWEEN 1000 AND 9999
        """, (gov,))
        count = cursor.fetchone()["count"]
        print(f"Government {gov}: {count} decisions")
    
    # Verify topics
    topics = ["חינוך", "בריאות", "תחבורה", "ביטחון"]
    for topic in topics:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM government_decisions 
            WHERE %s = ANY(topics)
            AND CAST(decision_number AS INTEGER) BETWEEN 1000 AND 9999
        """, (topic,))
        count = cursor.fetchone()["count"]
        print(f"Topic '{topic}': {count} decisions")

def main():
    """Main seeding function."""
    print("Starting test data seeding...")
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    conn = create_connection()
    if not conn:
        print("Failed to connect to database")
        return 1
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Clear existing test data
            if input("\nClear existing test data? (y/N): ").lower() == 'y':
                clear_test_data(cursor)
                conn.commit()
            
            # Seed new data
            seed_decisions(cursor)
            conn.commit()
            
            # Verify
            verify_data(cursor)
        
        print("\n✅ Test data seeding completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())