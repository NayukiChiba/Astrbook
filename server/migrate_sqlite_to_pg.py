"""
SQLite 到 PostgreSQL 数据迁移脚本

使用方法:
1. 确保 PostgreSQL 已安装并运行
2. 创建目标数据库: createdb astrbook
3. 设置环境变量或修改下面的配置
4. 运行: python migrate_sqlite_to_pg.py
"""

import os
import sys
from datetime import datetime

# 配置
# SQLite 数据库在项目根目录 (server 的父目录)
SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///../astrbook.db")
PG_URL = os.getenv("PG_URL", "postgresql://astrbook:810210Gao@localhost:5432/astrbook")

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# 导入模型
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.models import Base, Admin, User, OAuthAccount, Thread, Reply, Notification, SystemSettings, ModerationLog


def get_sqlite_engine():
    """获取 SQLite 引擎"""
    return create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


def get_pg_engine():
    """获取 PostgreSQL 引擎"""
    return create_engine(PG_URL, pool_pre_ping=True)


def check_sqlite_exists():
    """检查 SQLite 数据库是否存在"""
    if SQLITE_URL.startswith("sqlite:///"):
        # 提取路径部分
        db_path = SQLITE_URL.replace("sqlite:///", "")
        # 处理相对路径
        if not os.path.isabs(db_path):
            # 相对于当前脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.normpath(os.path.join(script_dir, db_path))
        
        print(f"📂 SQLite 文件路径: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite 数据库不存在: {db_path}")
            print("请确保 SQLite 数据库文件路径正确")
            return False
    return True


def create_pg_tables(pg_engine):
    """在 PostgreSQL 中创建所有表"""
    print("📦 正在 PostgreSQL 中创建表结构...")
    Base.metadata.create_all(bind=pg_engine)
    print("✅ 表结构创建完成")


def migrate_table(sqlite_session, pg_session, model_class, table_name):
    """迁移单个表的数据"""
    print(f"  📥 正在迁移 {table_name}...")
    
    # 获取所有数据
    records = sqlite_session.query(model_class).all()
    count = len(records)
    
    if count == 0:
        print(f"    ⏭️  {table_name}: 无数据，跳过")
        return 0
    
    # 转换并插入数据
    for record in records:
        # 创建新对象，复制所有列值
        mapper = inspect(model_class)
        new_record = model_class()
        
        for column in mapper.columns:
            value = getattr(record, column.key)
            setattr(new_record, column.key, value)
        
        pg_session.merge(new_record)
    
    pg_session.commit()
    print(f"    ✅ {table_name}: 迁移 {count} 条记录")
    return count


def reset_sequences(pg_engine):
    """重置 PostgreSQL 序列（自增ID）"""
    print("🔄 正在重置序列...")
    
    tables_with_id = [
        ('admins', 'id'),
        ('users', 'id'),
        ('oauth_accounts', 'id'),
        ('threads', 'id'),
        ('replies', 'id'),
        ('notifications', 'id'),
        ('moderation_logs', 'id'),
    ]
    
    with pg_engine.connect() as conn:
        for table, column in tables_with_id:
            try:
                # 获取当前最大 ID
                result = conn.execute(text(f"SELECT MAX({column}) FROM {table}"))
                max_id = result.scalar()
                
                if max_id is not None:
                    # 重置序列
                    seq_name = f"{table}_{column}_seq"
                    conn.execute(text(f"SELECT setval('{seq_name}', {max_id})"))
                    print(f"    ✅ {table}: 序列重置为 {max_id}")
            except Exception as e:
                print(f"    ⚠️  {table}: 重置序列时出错 - {e}")
        
        conn.commit()
    
    print("✅ 序列重置完成")


def verify_migration(sqlite_session, pg_session):
    """验证迁移结果"""
    print("🔍 正在验证迁移结果...")
    
    models = [
        (Admin, "admins"),
        (User, "users"),
        (OAuthAccount, "oauth_accounts"),
        (Thread, "threads"),
        (Reply, "replies"),
        (Notification, "notifications"),
        (SystemSettings, "system_settings"),
        (ModerationLog, "moderation_logs"),
    ]
    
    all_match = True
    for model, name in models:
        sqlite_count = sqlite_session.query(model).count()
        pg_count = pg_session.query(model).count()
        
        if sqlite_count == pg_count:
            print(f"    ✅ {name}: {sqlite_count} == {pg_count}")
        else:
            print(f"    ❌ {name}: SQLite({sqlite_count}) != PostgreSQL({pg_count})")
            all_match = False
    
    return all_match


def main():
    print("=" * 60)
    print("🚀 SQLite 到 PostgreSQL 数据迁移工具")
    print("=" * 60)
    print(f"📂 源数据库 (SQLite): {SQLITE_URL}")
    print(f"📂 目标数据库 (PostgreSQL): {PG_URL}")
    print()
    
    # 检查 SQLite 数据库是否存在
    if not check_sqlite_exists():
        return
    
    # 创建引擎
    try:
        sqlite_engine = get_sqlite_engine()
        pg_engine = get_pg_engine()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 测试连接
    try:
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL 连接成功")
    except Exception as e:
        print(f"❌ PostgreSQL 连接失败: {e}")
        print("请确保 PostgreSQL 已启动且数据库已创建")
        print("创建数据库命令: createdb astrbook")
        return
    
    # 创建表结构
    create_pg_tables(pg_engine)
    
    # 创建会话
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PGSession = sessionmaker(bind=pg_engine)
    
    sqlite_session = SQLiteSession()
    pg_session = PGSession()
    
    try:
        print("\n📊 开始数据迁移...")
        
        # 按照外键依赖顺序迁移
        # 1. 先迁移没有外键依赖的表
        migrate_table(sqlite_session, pg_session, Admin, "admins")
        migrate_table(sqlite_session, pg_session, User, "users")
        migrate_table(sqlite_session, pg_session, SystemSettings, "system_settings")
        
        # 2. 迁移依赖 users 的表
        migrate_table(sqlite_session, pg_session, OAuthAccount, "oauth_accounts")
        migrate_table(sqlite_session, pg_session, Thread, "threads")
        
        # 3. 迁移依赖 threads 的表
        migrate_table(sqlite_session, pg_session, Reply, "replies")
        
        # 4. 迁移依赖 replies 的表
        migrate_table(sqlite_session, pg_session, Notification, "notifications")
        migrate_table(sqlite_session, pg_session, ModerationLog, "moderation_logs")
        
        print("\n✅ 数据迁移完成!")
        
        # 重置序列
        reset_sequences(pg_engine)
        
        # 验证
        print()
        if verify_migration(sqlite_session, pg_session):
            print("\n🎉 迁移验证通过！所有数据已成功迁移到 PostgreSQL")
        else:
            print("\n⚠️  迁移验证发现差异，请检查数据")
        
    except Exception as e:
        print(f"\n❌ 迁移过程中出错: {e}")
        import traceback
        traceback.print_exc()
        pg_session.rollback()
    finally:
        sqlite_session.close()
        pg_session.close()
    
    print("\n" + "=" * 60)
    print("📝 后续步骤:")
    print("1. 修改 .env 文件中的 DATABASE_URL 为 PostgreSQL 连接字符串")
    print("2. 重启应用服务器")
    print("3. 测试应用功能是否正常")
    print("=" * 60)


if __name__ == "__main__":
    main()
