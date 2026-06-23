import aiomysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


class Database:
    def __init__(self, host: str, port: int, user: str, password: str, db_name: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.pool: aiomysql.Pool | None = None

    async def create_pool(self):
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
        # DictCursor returns rows as dicts instead of tuples
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql, params)
                if fetchone:
                    return await cur.fetchone()
                if fetchall:
                    return await cur.fetchall()
                return cur.lastrowid  # used after INSERT to get the new row id

    async def init_tables(self):
        await self.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id            INT PRIMARY KEY AUTO_INCREMENT,
                user_id       BIGINT NOT NULL,
                username      VARCHAR(255),
                section       VARCHAR(50) NOT NULL,
                content       TEXT NOT NULL,
                status        VARCHAR(20) NOT NULL DEFAULT 'pending',
                admin_id      BIGINT,
                admin_comment TEXT,
                created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                resolved_at   DATETIME
            ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """)

    async def add_submission(self, user_id: int, username: str | None, section: str, content: str) -> int:
        return await self.execute(
            "INSERT INTO submissions (user_id, username, section, content) VALUES (%s, %s, %s, %s)",
            (user_id, username, section, content),
        )

    async def get_submission(self, sub_id: int) -> dict | None:
        return await self.execute(
            "SELECT * FROM submissions WHERE id = %s",
            (sub_id,),
            fetchone=True,
        )

    async def update_status(self, sub_id: int, status: str, admin_id: int, admin_comment: str | None = None):
        await self.execute(
            """UPDATE submissions
               SET status = %s, admin_id = %s, admin_comment = %s, resolved_at = NOW()
               WHERE id = %s""",
            (status, admin_id, admin_comment, sub_id),
        )

    async def list_by_status(self, status: str) -> list[dict]:
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
