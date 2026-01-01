#!/usr/bin/env python3
"""
查看数据库数据的脚本
"""
from app.models import init_db, get_db, User
from sqlalchemy.orm import Session
from datetime import datetime

def view_database():
    """查看数据库中的所有数据"""
    init_db()
    db = next(get_db())
    
    print("=" * 60)
    print("WriteLoop 数据库数据查看")
    print("=" * 60)
    print()
    
    # 查看用户数据
    users = db.query(User).all()
    print(f"📊 用户总数: {len(users)}")
    print()
    
    if users:
        print("👥 用户列表:")
        print("-" * 60)
        for user in users:
            print(f"  ID: {user.id}")
            print(f"  用户名: {user.username}")
            print(f"  创建时间: {user.created_at}")
            print(f"  密码哈希: {user.hashed_password[:30]}...")
            print("-" * 60)
    else:
        print("  暂无用户数据")
    
    print()
    print("=" * 60)
    
    db.close()

if __name__ == "__main__":
    view_database()

