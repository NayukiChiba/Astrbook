#!/usr/bin/env python3
"""
迁移脚本: 修复 OAuth access_token 字段长度限制

问题: LinuxDo OAuth 返回的 access_token 超过 500 字符，导致数据库插入失败
解决: 将 access_token 从 VARCHAR(500) 改为 TEXT

使用方法:
    cd server
    python migrate_fix_access_token.py
"""

import sys
from sqlalchemy import text

# 添加当前目录到路径
sys.path.insert(0, ".")

from app.database import engine


def migrate():
    """执行迁移"""
    print("=" * 60)
    print("🔧 数据库迁移: 修复 OAuth access_token 字段长度")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 检查当前字段类型
        result = conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'oauth_accounts' 
            AND column_name = 'access_token'
        """))
        
        current_type = result.fetchone()
        if current_type:
            print(f"\n当前字段类型: {current_type[1]}", end="")
            if current_type[2]:
                print(f"({current_type[2]})")
            else:
                print()
        
        # 修改字段类型
        print("\n正在将 access_token 字段改为 TEXT 类型...")
        
        try:
            conn.execute(text("""
                ALTER TABLE oauth_accounts 
                ALTER COLUMN access_token TYPE TEXT
            """))
            conn.commit()
            print("✅ 字段类型修改成功！")
            
            # 验证修改结果
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'oauth_accounts' 
                AND column_name = 'access_token'
            """))
            
            new_type = result.fetchone()
            if new_type:
                print(f"\n新字段类型: {new_type[1]}")
            
            print("\n" + "=" * 60)
            print("✅ 迁移完成！现在 LinuxDo OAuth 应该可以正常工作了。")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
