"""
多平台分发管理脚本
支持产品分发到多个电商平台：1688、淘宝、京东、拼多多、抖音、小红书、闲鱼、亚马逊、独立站
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chip_products.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_platform_tables():
    """初始化平台相关表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 电商平台配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_name TEXT NOT NULL UNIQUE,
            platform_type TEXT NOT NULL,
            api_key TEXT,
            api_secret TEXT,
            store_id TEXT,
            store_name TEXT,
            is_enabled INTEGER DEFAULT 1,
            auto_pricing INTEGER DEFAULT 0,
            pricing_strategy TEXT DEFAULT 'manual',
            commission_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 平台产品映射表（同一产品在不同平台的 ID）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            platform_name TEXT NOT NULL,
            platform_product_id TEXT,
            platform_product_url TEXT,
            platform_status TEXT DEFAULT 'pending',
            platform_price REAL,
            platform_stock INTEGER,
            platform_sales INTEGER DEFAULT 0,
            platform_views INTEGER DEFAULT 0,
            last_sync_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE(product_id, platform_name)
        )
    ''')

    # 平台分发任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS distribution_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            task_type TEXT NOT NULL,
            platform_list TEXT NOT NULL,
            product_ids TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            scheduled_time TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            success_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 平台订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT NOT NULL UNIQUE,
            platform_name TEXT NOT NULL,
            platform_order_id TEXT NOT NULL,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            order_amount REAL,
            order_status TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            shipping_address TEXT,
            tracking_no TEXT,
            order_time TIMESTAMP,
            paid_time TIMESTAMP,
            shipped_time TIMESTAMP,
            completed_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 插入默认平台配置
    platforms = [
        ('1688', 'domestic_wholesale', None, None, None, '宜欧特旗舰店', 1, 0, 'manual', 0),
        ('淘宝', 'domestic_retail', None, None, None, '宜欧特淘宝店', 0, 0, 'manual', 5),
        ('天猫', 'domestic_retail', None, None, None, '宜欧特天猫店', 0, 0, 'manual', 5),
        ('京东', 'domestic_retail', None, None, None, '宜欧特京东店', 0, 0, 'manual', 5),
        ('拼多多', 'domestic_retail', None, None, None, '宜欧特拼多多店', 0, 0, 'manual', 6),
        ('抖音电商', 'content_commerce', None, None, None, '宜欧特抖音店', 0, 0, 'manual', 10),
        ('小红书', 'content_commerce', None, None, None, '宜欧特小红书店', 0, 0, 'manual', 10),
        ('闲鱼', 'secondhand', None, None, None, '宜欧特闲鱼店', 0, 0, 'manual', 0),
        ('亚马逊', 'cross_border', None, None, None, 'KONGSON Store', 0, 0, 'manual', 15),
        ('独立站', 'self_operated', None, None, None, 'KONGSON Official', 0, 0, 'manual', 0),
    ]

    for platform in platforms:
        cursor.execute('''
            INSERT OR IGNORE INTO platform_configs
            (platform_name, platform_type, api_key, api_secret, store_id, store_name,
             is_enabled, auto_pricing, pricing_strategy, commission_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', platform)

    conn.commit()
    conn.close()


class PlatformManager:
    """平台管理器"""

    @staticmethod
    def get_all_platforms() -> List[Dict]:
        """获取所有平台配置"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM platform_configs ORDER BY id')
        platforms = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return platforms

    @staticmethod
    def get_enabled_platforms() -> List[Dict]:
        """获取已启用的平台"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM platform_configs WHERE is_enabled = 1 ORDER BY id')
        platforms = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return platforms

    @staticmethod
    def update_platform_config(platform_name: str, **kwargs):
        """更新平台配置"""
        conn = get_db_connection()
        cursor = conn.cursor()

        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [platform_name]

        cursor.execute(f'''
            UPDATE platform_configs
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE platform_name = ?
        ''', values)

        conn.commit()
        conn.close()

    @staticmethod
    def create_platform_product(product_id: int, platform_name: str,
                                platform_product_id: str = None) -> int:
        """创建平台产品映射"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO platform_products
            (product_id, platform_name, platform_product_id, platform_status, created_at)
            VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        ''', (product_id, platform_name, platform_product_id))

        platform_product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return platform_product_id

    @staticmethod
    def get_platform_products(product_id: int = None, platform_name: str = None) -> List[Dict]:
        """获取平台产品列表"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM platform_products WHERE 1=1'
        params = []

        if product_id:
            query += ' AND product_id = ?'
            params.append(product_id)
        if platform_name:
            query += ' AND platform_name = ?'
            params.append(platform_name)

        cursor.execute(query, params)
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products

    @staticmethod
    def update_platform_status(platform_product_id: int, status: str,
                               platform_product_id_ext: str = None):
        """更新平台产品状态"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE platform_products
            SET platform_status = ?,
                platform_product_id = COALESCE(?, platform_product_id),
                last_sync_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, platform_product_id_ext, platform_product_id))

        conn.commit()
        conn.close()

    @staticmethod
    def create_distribution_task(task_name: str, task_type: str,
                                 platform_list: List[str],
                                 product_ids: List[int],
                                 scheduled_time: datetime = None) -> int:
        """创建分发任务"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO distribution_tasks
            (task_name, task_type, platform_list, product_ids, status, scheduled_time)
            VALUES (?, ?, ?, ?, 'pending', ?)
        ''', (
            task_name,
            task_type,
            ','.join(platform_list),
            ','.join(map(str, product_ids)),
            scheduled_time
        ))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    @staticmethod
    def get_distribution_tasks(status: str = None) -> List[Dict]:
        """获取分发任务列表"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM distribution_tasks'
        if status:
            query += f' WHERE status = ?'
            cursor.execute(query, [status])
        else:
            cursor.execute(query)

        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    @staticmethod
    def update_task_status(task_id: int, status: str, **kwargs):
        """更新任务状态"""
        conn = get_db_connection()
        cursor = conn.cursor()

        set_fields = ['status = ?']
        values = [status]

        for key, value in kwargs.items():
            set_fields.append(f'{key} = ?')
            values.append(value)

        values.append(task_id)

        cursor.execute(f'''
            UPDATE distribution_tasks
            SET {', '.join(set_fields)}
            WHERE id = ?
        ''', values)

        conn.commit()
        conn.close()

    @staticmethod
    def get_platform_statistics() -> Dict:
        """获取平台统计"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 各平台产品数量
        cursor.execute('''
            SELECT platform_name,
                   COUNT(*) as total,
                   SUM(CASE WHEN platform_status = 'online' THEN 1 ELSE 0 END) as online,
                   SUM(CASE WHEN platform_status = 'pending' THEN 1 ELSE 0 END) as pending,
                   SUM(platform_sales) as total_sales
            FROM platform_products
            GROUP BY platform_name
        ''')
        platform_stats = [dict(row) for row in cursor.fetchall()]

        # 各平台订单数量
        cursor.execute('''
            SELECT platform_name,
                   COUNT(*) as order_count,
                   SUM(order_amount) as total_amount
            FROM platform_orders
            GROUP BY platform_name
        ''')
        order_stats = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            'platform_stats': platform_stats,
            'order_stats': order_stats
        }


# 初始化
init_platform_tables()

if __name__ == '__main__':
    # 测试
    print("平台配置表初始化完成！")
    platforms = PlatformManager.get_all_platforms()
    print(f"共配置 {len(platforms)} 个平台:")
    for p in platforms:
        status = "✅ 启用" if p['is_enabled'] else "❌ 禁用"
        print(f"  - {p['platform_name']} ({p['store_name']}) - {status}")
