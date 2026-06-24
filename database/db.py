import aiomysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


class Database:
    """
    Async MySQL database wrapper using a connection pool.

    All SQL queries go through the single execute() method.
    Call create_pool() on startup and close() on shutdown.
    """

    def __init__(self, host: str, port: int, user: str, password: str, db_name: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.pool: aiomysql.Pool | None = None

    async def create_pool(self):
        """Open the connection pool. Must be called before any queries."""
        # autocommit=True so we don't need explicit commit() after every write
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db_name,
            charset="utf8mb4",
            autocommit=True,
            minsize=1,
            maxsize=5,
        )

    async def close(self):
        """Gracefully close all connections in the pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def execute(
        self,
        sql: str,
        params: tuple = (),
        fetchone: bool = False,
        fetchall: bool = False,
    ) -> dict | list | int | None:
        """
        Run any SQL query and return the appropriate result.

        Args:
            sql:      Raw SQL string with %s placeholders.
            params:   Values to substitute into the placeholders.
            fetchone: Return a single row as a dict.
            fetchall: Return all matching rows as a list of dicts.

        Returns:
            dict if fetchone, list[dict] if fetchall,
            lastrowid (int) for INSERT, None otherwise.
        """
        # DictCursor returns rows as dicts instead of tuples
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql, params)
                if fetchone:
                    return await cur.fetchone()
                if fetchall:
                    return await cur.fetchall()
                return cur.lastrowid

    async def init_tables(self):
        """Create all required tables if they don't exist yet."""
        await self.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id             INT PRIMARY KEY AUTO_INCREMENT,
                user_id        BIGINT NOT NULL,
                username       VARCHAR(255),
                section        VARCHAR(50) NOT NULL,
                content        TEXT NOT NULL,
                status         VARCHAR(20) NOT NULL DEFAULT 'pending',
                admin_id       BIGINT,
                admin_username VARCHAR(255),
                admin_comment  TEXT,
                created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                resolved_at    DATETIME
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)
        # Add admin_username for existing tables created before this column existed
        await self.execute(
            "ALTER TABLE submissions ADD COLUMN IF NOT EXISTS admin_username VARCHAR(255)"
        )

    async def add_submission(self, user_id: int, username: str | None, section: str, content: str) -> int:
        """
        Save a new user submission and return its auto-generated ID.

        Args:
            user_id:  Telegram user ID of the sender.
            username: Telegram @username (may be None if not set).
            section:  Section key — 'complaint', 'deputy', 'senior', or 'misc'.
            content:  Raw message text submitted by the user.

        Returns:
            The new submission's ID in the database.
        """
        return await self.execute(
            "INSERT INTO submissions (user_id, username, section, content) VALUES (%s, %s, %s, %s)",
            (user_id, username, section, content),
        )

    async def get_submission(self, sub_id: int) -> dict | None:
        """
        Fetch a single submission by its ID.

        Returns:
            A dict with all submission fields, or None if not found.
        """
        return await self.execute(
            "SELECT * FROM submissions WHERE id = %s",
            (sub_id,),
            fetchone=True,
        )

    async def update_status(
        self,
        sub_id: int,
        status: str,
        admin_id: int,
        admin_comment: str | None = None,
        admin_username: str | None = None,
    ):
        """
        Update the status of a submission after an admin decision.

        Args:
            sub_id:         ID of the submission to update.
            status:         New status — 'approved' or 'rejected'.
            admin_id:       Telegram ID of the admin who made the decision.
            admin_comment:  Optional comment or rejection reason to store.
            admin_username: Telegram @username of the admin (may be None).
        """
        await self.execute(
            """UPDATE submissions
               SET status = %s, admin_id = %s, admin_username = %s,
                   admin_comment = %s, resolved_at = NOW()
               WHERE id = %s""",
            (status, admin_id, admin_username, admin_comment, sub_id),
        )

    async def list_by_status(self, status: str) -> list[dict]:
        """
        Return all submissions with the given status, newest first.

        Args:
            status: 'approved', 'rejected', or 'pending'.

        Returns:
            List of submission dicts (empty list if none found).
        """
        result = await self.execute(
            "SELECT * FROM submissions WHERE status = %s ORDER BY created_at DESC",
            (status,),
            fetchall=True,
        )
        return result or []


# Single shared instance used across the entire project
db = Database(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    db_name=DB_NAME,
)
