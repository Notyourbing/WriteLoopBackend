#!/bin/bash
# 使用 MySQL 命令行查看数据库

# 从环境变量或默认值读取配置
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-appuser}
DB_PASSWORD=${DB_PASSWORD:-App@12345678}
DB_NAME=${DB_NAME:-appdb}

echo "连接到数据库: $DB_NAME@$DB_HOST:$DB_PORT"
echo ""

# 查看用户表数据
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD $DB_NAME <<EOF
SELECT 
    id,
    username,
    created_at,
    LEFT(hashed_password, 30) as password_hash_preview
FROM users
ORDER BY id;
EOF

