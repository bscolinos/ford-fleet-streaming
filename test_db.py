#!/usr/bin/env python3
"""
Test SingleStore database connection using singlestoredb package.

This script verifies that the database connection is working correctly
using the SINGLESTORE_* environment variables from .env file.

Usage:
    python test_db.py
"""

import os
import socket
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

import singlestoredb as s2


def resolve_hostname(hostname: str) -> str:
    """
    Resolve hostname to IP, using public DNS as fallback.

    Works around macOS DNS resolution issues where Python's socket
    library can't resolve hostnames that system tools (nslookup) can.
    """
    # First try normal resolution
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        pass

    # Fall back to using dnspython with public DNS
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']  # Google & Cloudflare DNS
        answers = resolver.resolve(hostname, 'A')
        return str(answers[0])
    except Exception as e:
        raise RuntimeError(f"Could not resolve hostname {hostname}: {e}")


def test_connection():
    """Test basic database connection."""
    host = os.getenv("SINGLESTORE_HOST", "localhost")
    port = int(os.getenv("SINGLESTORE_PORT", "3306"))
    user = os.getenv("SINGLESTORE_USER", "admin")
    password = os.getenv("SINGLESTORE_PASSWORD", "")
    database = os.getenv("SINGLESTORE_DATABASE", "ford_fleet")

    print("=" * 60)
    print("SingleStore Connection Test")
    print("=" * 60)
    print(f"Host:     {host}")
    print(f"Port:     {port}")
    print(f"User:     {user}")
    print(f"Database: {database}")
    print(f"Password: {'*' * len(password) if password else '(not set)'}")
    print()

    try:
        # Resolve hostname (with fallback to public DNS for macOS compatibility)
        print(f"Resolving hostname...")
        resolved_host = resolve_hostname(host)
        if resolved_host != host:
            print(f"Resolved to: {resolved_host}")
        print()

        print("Connecting to SingleStore...")
        conn = s2.connect(
            host=resolved_host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        print("Connected successfully!")
        print()

        # Test basic query
        print("Testing basic query (SELECT 1)...")
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"Result: {result[0]}")
            assert result[0] == 1, "Basic query failed"
        print("Basic query passed!")
        print()

        # Test database version
        print("Getting SingleStore version...")
        with conn.cursor() as cursor:
            cursor.execute("SELECT @@memsql_version as version")
            result = cursor.fetchone()
            print(f"SingleStore Version: {result[0]}")
        print()

        # Test if tables exist
        print("Checking for tables...")
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print(f"Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("No tables found. Run db/schema.sql to create tables.")
        print()

        # Test sample query on vehicles table if it exists
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'vehicles'")
            if cursor.fetchone():
                print("Testing query on vehicles table...")
                cursor.execute("SELECT COUNT(*) as count FROM vehicles")
                count = cursor.fetchone()[0]
                print(f"Vehicle count: {count}")
        print()

        conn.close()
        print("=" * 60)
        print("All tests passed! Database connection is working.")
        print("=" * 60)
        return True

    except s2.Error as e:
        print(f"Database error: {e}")
        print()
        print("Troubleshooting tips:")
        print("  1. Check that SINGLESTORE_HOST is correct")
        print("  2. Check that SINGLESTORE_USER and SINGLESTORE_PASSWORD are set in .env")
        print("  3. Verify the database exists")
        print("  4. Check network connectivity to the SingleStore server")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
