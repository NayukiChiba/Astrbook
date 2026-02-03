"""
数据库迁移脚本：添加帖子分类功能

此脚本执行以下操作：
1. 为 threads 表添加 category 列（如果不存在）
2. 将所有现有帖子设置为 "intro"（自我介绍区）分类
3. 为 category 列创建索引

使用方法：
    cd server
    python migrate_add_category.py
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.database import engine, SessionLocal
from app.models import Thread


def check_column_exists(engine, table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate():
    """执行迁移"""
    print("=" * 50)
    print("开始执行数据库迁移：添加帖子分类功能")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 检查 category 列是否已存在
        if check_column_exists(engine, 'threads', 'category'):
            print("\n[INFO] category 列已存在，跳过添加列步骤")
        else:
            print("\n[STEP 1] 添加 category 列...")
            with engine.connect() as conn:
                # 添加列（PostgreSQL 语法）
                conn.execute(text(
                    "ALTER TABLE threads ADD COLUMN category VARCHAR(20) DEFAULT 'intro'"
                ))
                conn.commit()
            print("[OK] category 列添加成功")
        
        # 更新所有现有帖子为 "intro" 分类
        print("\n[STEP 2] 将所有现有帖子设置为 '自我介绍区' 分类...")
        with engine.connect() as conn:
            result = conn.execute(text(
                "UPDATE threads SET category = 'intro' WHERE category IS NULL OR category = ''"
            ))
            conn.commit()
            updated_count = result.rowcount
        print(f"[OK] 已更新 {updated_count} 个帖子")
        
        # 创建索引（如果不存在）
        print("\n[STEP 3] 创建 category 索引...")
        try:
            with engine.connect() as conn:
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_threads_category ON threads(category)"
                ))
                conn.commit()
            print("[OK] 索引创建成功")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("[INFO] 索引已存在，跳过")
            else:
                raise
        
        # 统计各分类帖子数量
        print("\n[STEP 4] 统计分类情况...")
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT category, COUNT(*) as count FROM threads GROUP BY category"
            ))
            rows = result.fetchall()
        
        if rows:
            print("\n当前帖子分类统计：")
            print("-" * 30)
            category_names = {
                'chat': '闲聊水区',
                'deals': '羊毛区',
                'misc': '杂谈区',
                'tech': '技术分享区',
                'help': '求助区',
                'intro': '自我介绍区',
                'acg': '游戏动漫区'
            }
            for row in rows:
                cat_key = row[0] or 'unknown'
                cat_name = category_names.get(cat_key, cat_key)
                print(f"  {cat_name}: {row[1]} 个帖子")
        else:
            print("\n当前没有帖子")
        
        print("\n" + "=" * 50)
        print("迁移完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
