"""
迁移脚本：添加审核相关的表
- system_settings: 系统设置（键值对）
- moderation_logs: 审核日志

运行方式：
cd server
python migrate_add_moderation.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

# 创建 system_settings 表
create_system_settings = """
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 创建 moderation_logs 表
create_moderation_logs = """
CREATE TABLE IF NOT EXISTS moderation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type VARCHAR(20) NOT NULL,
    content_id INTEGER,
    user_id INTEGER NOT NULL,
    content_preview VARCHAR(500),
    passed BOOLEAN NOT NULL,
    flagged_category VARCHAR(50),
    reason VARCHAR(500),
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

# PostgreSQL 版本（如果使用 PostgreSQL）
create_moderation_logs_pg = """
CREATE TABLE IF NOT EXISTS moderation_logs (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(20) NOT NULL,
    content_id INTEGER,
    user_id INTEGER NOT NULL REFERENCES users(id),
    content_preview VARCHAR(500),
    passed BOOLEAN NOT NULL,
    flagged_category VARCHAR(50),
    reason VARCHAR(500),
    model_used VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

def migrate():
    with engine.connect() as conn:
        print("正在创建 system_settings 表...")
        conn.execute(text(create_system_settings))
        
        print("正在创建 moderation_logs 表...")
        if 'postgresql' in settings.DATABASE_URL:
            conn.execute(text(create_moderation_logs_pg))
        else:
            conn.execute(text(create_moderation_logs))
        
        conn.commit()
        print("✅ 迁移完成！")

if __name__ == "__main__":
    migrate()
