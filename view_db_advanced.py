#!/usr/bin/env python3
"""
高级数据库查看脚本 - 可以查看更详细的信息
"""
from app.models import init_db, get_db, User
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys

def view_users():
    """查看所有用户"""
    init_db()
    db = next(get_db())
    
    users = db.query(User).all()
    print(f"\n📊 用户总数: {len(users)}\n")
    
    if users:
        print(f"{'ID':<5} {'用户名':<20} {'创建时间':<20}")
        print("-" * 50)
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {str(user.created_at):<20}")
    else:
        print("  暂无用户数据")
    
    db.close()

def view_user_detail(username=None):
    """查看特定用户的详细信息"""
    init_db()
    db = next(get_db())
    
    if username:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"\n👤 用户详情: {username}")
            print("-" * 50)
            print(f"  ID: {user.id}")
            print(f"  用户名: {user.username}")
            print(f"  创建时间: {user.created_at}")
            print(f"  密码哈希: {user.hashed_password}")
        else:
            print(f"❌ 未找到用户: {username}")
    else:
        print("请提供用户名，例如: python3 view_db_advanced.py detail Jialu")
    
    db.close()

def view_table_info():
    """查看表结构信息"""
    init_db()
    db = next(get_db())
    
    result = db.execute(text("SHOW TABLES"))
    tables = result.fetchall()
    
    print("\n📋 数据库表列表:")
    print("-" * 50)
    for table in tables:
        print(f"  - {table[0]}")
    
    # 查看 users 表结构
    print("\n📋 users 表结构:")
    print("-" * 50)
    result = db.execute(text("DESCRIBE users"))
    columns = result.fetchall()
    for col in columns:
        print(f"  {col[0]:<20} {col[1]:<20} {col[2]}")
    
    db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "detail" and len(sys.argv) > 2:
            view_user_detail(sys.argv[2])
        elif command == "tables":
            view_table_info()
        else:
            print("用法:")
            print("  python3 view_db_advanced.py          # 查看所有用户")
            print("  python3 view_db_advanced.py detail <用户名>  # 查看特定用户详情")
            print("  python3 view_db_advanced.py tables    # 查看表结构")
    else:
        view_users()

