"""添加用户封禁功能 - is_banned + ban_reason 字段"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()


def upgrade():
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        # 检查 is_banned 字段是否已存在
        try:
            conn.execute(text("SELECT is_banned FROM users LIMIT 1"))
            print("is_banned 字段已存在，跳过")
        except Exception:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
            conn.commit()
            print("已添加 is_banned 字段")

        # 检查 ban_reason 字段是否已存在
        try:
            conn.execute(text("SELECT ban_reason FROM users LIMIT 1"))
            print("ban_reason 字段已存在，跳过")
        except Exception:
            conn.execute(text("ALTER TABLE users ADD COLUMN ban_reason VARCHAR(500)"))
            conn.commit()
            print("已添加 ban_reason 字段")


if __name__ == "__main__":
    upgrade()
