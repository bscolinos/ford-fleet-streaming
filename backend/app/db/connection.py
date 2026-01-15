"""
Database connection management using singlestoredb package.
Supports both main admin connection and role-based connections for RLS.
"""

import socket
import singlestoredb as s2
from contextlib import contextmanager
from typing import Generator, Optional

from app.config import get_settings

settings = get_settings()

# Cache for resolved hostname
_resolved_host: Optional[str] = None


def _resolve_hostname(hostname: str) -> str:
    """
    Resolve hostname to IP, using public DNS as fallback.

    Works around macOS DNS resolution issues where Python's socket
    library can't resolve hostnames that system tools (nslookup) can.
    """
    global _resolved_host
    if _resolved_host:
        return _resolved_host

    # First try normal resolution
    try:
        _resolved_host = socket.gethostbyname(hostname)
        return _resolved_host
    except socket.gaierror:
        pass

    # Fall back to using dnspython with public DNS
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        answers = resolver.resolve(hostname, 'A')
        _resolved_host = str(answers[0])
        return _resolved_host
    except Exception:
        # Last resort: return original hostname and let connection fail with clear error
        return hostname


def get_db_credentials(role: Optional[str] = None) -> tuple[str, str]:
    """
    Get database credentials.

    Currently uses main SINGLESTORE_USER/SINGLESTORE_PASSWORD for all roles.
    Role-based RLS credentials can be enabled by uncommenting the role checks below
    after creating the corresponding users in SingleStore using db/security.sql.
    """
    # Always use main SingleStore credentials for now
    return settings.singlestore_user, settings.singlestore_password

    # Uncomment below for role-based RLS after running security.sql:
    # if role is None:
    #     return settings.singlestore_user, settings.singlestore_password
    # elif role == "admin":
    #     return settings.db_admin_user, settings.db_admin_password
    # elif role == "regional_manager":
    #     return settings.db_regional_manager_user, settings.db_regional_manager_password
    # elif role == "territory_manager":
    #     return settings.db_territory_manager_user, settings.db_territory_manager_password
    # else:
    #     return settings.singlestore_user, settings.singlestore_password


def create_connection(role: Optional[str] = None):
    """
    Create a database connection using singlestoredb package.

    Args:
        role: Optional role for RLS. If None, uses main SINGLESTORE credentials.

    Returns:
        SingleStore database connection
    """
    user, password = get_db_credentials(role)
    host = _resolve_hostname(settings.singlestore_host)

    return s2.connect(
        host=host,
        port=settings.singlestore_port,
        user=user,
        password=password,
        database=settings.singlestore_database
    )


@contextmanager
def get_connection(role: Optional[str] = None) -> Generator:
    """
    Context manager for database connections.

    Args:
        role: Optional role for RLS. If None, uses main SINGLESTORE credentials.
    """
    conn = create_connection(role)
    try:
        yield conn
    finally:
        conn.close()


def execute_query(sql: str, params: tuple = None, role: Optional[str] = None) -> list:
    """
    Execute a query and return results as list of dicts.

    Args:
        sql: SQL query string
        params: Query parameters
        role: Optional role for RLS credentials
    """
    with get_connection(role) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []


def execute_write(sql: str, params: tuple = None, role: Optional[str] = None) -> int:
    """
    Execute a write operation and return affected rows.

    Args:
        sql: SQL statement
        params: Statement parameters
        role: Optional role for RLS credentials
    """
    with get_connection(role) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.rowcount


def execute_many(sql: str, params_list: list[tuple], role: Optional[str] = None) -> int:
    """
    Execute a batch write operation.

    Args:
        sql: SQL statement
        params_list: List of parameter tuples
        role: Optional role for RLS credentials
    """
    with get_connection(role) as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, params_list)
            conn.commit()
            return cursor.rowcount


def test_connection() -> bool:
    """
    Test database connection using main SINGLESTORE credentials.

    Returns:
        True if connection successful, raises exception otherwise.
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1

