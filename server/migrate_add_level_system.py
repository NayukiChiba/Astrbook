"""
数据库迁移脚本：添加等级系统

新增表：
- user_levels: 用户等级表
- likes: 点赞记录表

修改表：
- threads: 添加 like_count 字段
- replies: 添加 like_count 字段
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine, SessionLocal


def migrate():
    """执行迁移"""
    db = SessionLocal()
    
    try:
        # 检测数据库类型
        dialect = engine.dialect.name
        print(f"数据库类型: {dialect}")
        
        with engine.connect() as conn:
            # 1. 创建 user_levels 表
            print("检查 user_levels 表...")
            if dialect == "postgresql":
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_levels')"
                ))
                exists = result.scalar()
            else:  # SQLite
                result = conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='user_levels'"
                ))
                exists = result.fetchone() is not None
            
            if not exists:
                print("创建 user_levels 表...")
                conn.execute(text("""
                    CREATE TABLE user_levels (
                        user_id INTEGER PRIMARY KEY,
                        exp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        today_post_exp INTEGER DEFAULT 0,
                        today_reply_exp INTEGER DEFAULT 0,
                        last_exp_date DATE,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """))
                conn.commit()
                print("✓ user_levels 表创建成功")
            else:
                print("✓ user_levels 表已存在")
            
            # 2. 创建 likes 表
            print("检查 likes 表...")
            if dialect == "postgresql":
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'likes')"
                ))
                exists = result.scalar()
            else:  # SQLite
                result = conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='likes'"
                ))
                exists = result.fetchone() is not None
            
            if not exists:
                print("创建 likes 表...")
                conn.execute(text("""
                    CREATE TABLE likes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        target_type VARCHAR(10) NOT NULL,
                        target_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """) if dialect == "sqlite" else text("""
                    CREATE TABLE likes (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        target_type VARCHAR(10) NOT NULL,
                        target_id INTEGER NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """))
                conn.commit()
                
                # 创建唯一索引
                print("创建 likes 唯一索引...")
                conn.execute(text(
                    "CREATE UNIQUE INDEX ix_like_unique ON likes (user_id, target_type, target_id)"
                ))
                conn.commit()
                print("✓ likes 表创建成功")
            else:
                print("✓ likes 表已存在")
            
            # 3. 为 threads 表添加 like_count 字段
            print("检查 threads.like_count 字段...")
            if dialect == "postgresql":
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'threads' AND column_name = 'like_count'"
                ))
                exists = result.fetchone() is not None
            else:  # SQLite
                result = conn.execute(text("PRAGMA table_info(threads)"))
                columns = [row[1] for row in result.fetchall()]
                exists = "like_count" in columns
            
            if not exists:
                print("添加 threads.like_count 字段...")
                conn.execute(text(
                    "ALTER TABLE threads ADD COLUMN like_count INTEGER DEFAULT 0"
                ))
                conn.commit()
                print("✓ threads.like_count 字段添加成功")
            else:
                print("✓ threads.like_count 字段已存在")
            
            # 4. 为 replies 表添加 like_count 字段
            print("检查 replies.like_count 字段...")
            if dialect == "postgresql":
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'replies' AND column_name = 'like_count'"
                ))
                exists = result.fetchone() is not None
            else:  # SQLite
                result = conn.execute(text("PRAGMA table_info(replies)"))
                columns = [row[1] for row in result.fetchall()]
                exists = "like_count" in columns
            
            if not exists:
                print("添加 replies.like_count 字段...")
                conn.execute(text(
                    "ALTER TABLE replies ADD COLUMN like_count INTEGER DEFAULT 0"
                ))
                conn.commit()
                print("✓ replies.like_count 字段添加成功")
            else:
                print("✓ replies.like_count 字段已存在")
        
        # 5. 为现有用户初始化等级信息
        print("为现有用户初始化等级信息...")
        # 使用原生 SQL 查询用户并插入等级信息
        with engine.connect() as conn:
            # 获取所有用户 ID
            result = conn.execute(text("SELECT id FROM users"))
            user_ids = [row[0] for row in result.fetchall()]
            
            initialized_count = 0
            for user_id in user_ids:
                # 检查是否已有等级信息
                check_result = conn.execute(text(
                    f"SELECT user_id FROM user_levels WHERE user_id = {user_id}"
                ))
                if check_result.fetchone() is None:
                    # 插入初始等级信息
                    conn.execute(text(
                        f"INSERT INTO user_levels (user_id, exp, level, today_post_exp, today_reply_exp) "
                        f"VALUES ({user_id}, 0, 1, 0, 0)"
                    ))
                    initialized_count += 1
            
            conn.commit()
        
        if initialized_count > 0:
            print(f"✓ 为 {initialized_count} 个用户初始化了等级信息")
        else:
            print("✓ 所有用户都已有等级信息")
        
        print("\n✅ 迁移完成！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
