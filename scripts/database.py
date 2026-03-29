# -*- coding: utf-8 -*-
"""
本地数据库模块 - SQLite Database for Chip Automation Workflow
用于持久化存储产品数据、销售数据、任务队列等

作者：KR + Claude Code
日期：2026-03-22
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 数据库文件路径
DB_PATH = Path("data/chip_workflow.db")

def get_db_connection():
    """获取数据库连接"""
    # 确保数据库目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 支持字典访问
    return conn

def init_database():
    """初始化数据库表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 产品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model VARCHAR(100) NOT NULL,
            name VARCHAR(200),
            brand VARCHAR(100) DEFAULT '冠辰科技',
            category VARCHAR(100),
            input_voltage VARCHAR(50),
            output_voltage VARCHAR(50),
            output_current VARCHAR(50),
            efficiency VARCHAR(20),
            switch_frequency VARCHAR(50),
            current_accuracy VARCHAR(50),
            operating_temp VARCHAR(50),
            package VARCHAR(50),
            protection VARCHAR(200),
            cost DECIMAL(10,2),
            suggested_price DECIMAL(10,2),
            pdf_file_path VARCHAR(500),
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 1688 详情页生成记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            model VARCHAR(100) NOT NULL,
            html_path VARCHAR(500),
            md_path VARCHAR(500),
            content_type VARCHAR(20) DEFAULT '1688 详情页',
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # 上架队列表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upload_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            model VARCHAR(100) NOT NULL,
            platform VARCHAR(50) DEFAULT '1688',
            status VARCHAR(20) DEFAULT 'pending',
            scheduled_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # 销售数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            model VARCHAR(100),
            platform VARCHAR(50),
            sale_date DATE NOT NULL,
            revenue DECIMAL(10,2),
            orders INTEGER,
            views INTEGER,
            clicks INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # 团队任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            assignee VARCHAR(100),
            status VARCHAR(20) DEFAULT 'todo',
            priority VARCHAR(20) DEFAULT 'medium',
            due_date DATE,
            product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # 公众号文章表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wechat_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            model VARCHAR(100),
            title VARCHAR(300),
            content TEXT,
            article_type VARCHAR(50) DEFAULT '公众号推文',
            file_path VARCHAR(500),
            status VARCHAR(20) DEFAULT 'draft',
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # 产品系列表（品牌 - 系列管理）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand VARCHAR(100) NOT NULL,        -- 品牌：士兰微、晶丰明源、矹力杰
            series_name VARCHAR(100) NOT NULL,  -- 系列名：SM89 系列、BP 系列、SY 系列
            description TEXT,                   -- 系列描述
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(brand, series_name)          -- 防止重复
        )
    ''')

    # ==================== 冠辰科技方案开发服务管理系统 ====================

    # 方案库表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solution_name VARCHAR(200) NOT NULL,    -- 方案名称
            domain VARCHAR(50) NOT NULL,            -- 所属领域：智能照明/电源电池/传感感应/电机风扇
            sub_domain VARCHAR(100),                -- 子分类
            solution_type VARCHAR(50) DEFAULT '标准方案',  -- 方案类型：标准方案/定制方案
            application VARCHAR(100),               -- 应用领域：照明/家电/汽车/工业等
            core_chip VARCHAR(200),                 -- 核心芯片
            features TEXT,                          -- 方案特点
            description TEXT,                       -- 方案描述
            status VARCHAR(20) DEFAULT '开发中',    -- 状态：开发中/已发布/已停产
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 方案文档表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solution_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solution_id INTEGER NOT NULL,
            doc_name VARCHAR(200) NOT NULL,         -- 文档名称
            doc_type VARCHAR(50) NOT NULL,          -- 文档类型：PDF/原理图/PCB/CAD/生产文件
            file_path VARCHAR(500) NOT NULL,        -- 文件存储路径
            file_size INTEGER,                      -- 文件大小（字节）
            description TEXT,                       -- 文档描述
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (solution_id) REFERENCES solutions (id)
        )
    ''')

    # 客户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name VARCHAR(200) NOT NULL,     -- 公司名称
            contact_person VARCHAR(100),            -- 联系人
            contact_phone VARCHAR(50),              -- 联系电话
            contact_email VARCHAR(100),             -- 联系邮箱
            industry VARCHAR(100),                  -- 所属行业
            region VARCHAR(100),                    -- 地区
            customer_type VARCHAR(50) DEFAULT '潜在', -- 客户类型：潜在/意向/签约/VIP
            preferred_domains TEXT,                 -- 偏好领域（JSON 数组）
            notes TEXT,                             -- 备注
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 方案分发记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solution_distributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solution_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            distribution_type VARCHAR(50) DEFAULT '推荐',  -- 分发类型：推荐/主动询问/会议演示
            status VARCHAR(20) DEFAULT '已发送',    -- 状态：已发送/已查看/有意向/已成交
            feedback TEXT,                          -- 客户反馈
            follow_up_date DATE,                    -- 跟进日期
            distributed_by VARCHAR(100),            -- 分发人
            distributed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (solution_id) REFERENCES solutions (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')

    # ==================== 关联公司数据对接 ====================
    # 希懋/智慧世界/宜欧特/日银微电子 - 数据接口配置

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name VARCHAR(200) NOT NULL,     -- 公司名称：希懋/智慧世界/宜欧特/日银微电子
            company_code VARCHAR(50) UNIQUE,        -- 公司代码：XIMAO/SMARTWORLD/YOUTO/silver
            contact_person VARCHAR(100),            -- 联系人
            contact_phone VARCHAR(50),              -- 联系电话
            contact_email VARCHAR(100),             -- 联系邮箱
            api_endpoint VARCHAR(500),              -- API 接口地址
            api_key VARCHAR(500),                   -- API 密钥
            api_secret VARCHAR(500),                -- API 密钥
            data_sync_enabled BOOLEAN DEFAULT FALSE, -- 是否启用数据同步
            sync_frequency VARCHAR(50) DEFAULT 'daily', -- 同步频率：hourly/daily/weekly
            last_sync_at TIMESTAMP,                 -- 最后同步时间
            status VARCHAR(20) DEFAULT 'active',    -- 状态：active/inactive
            notes TEXT,                             -- 备注
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 合作公司产品数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,            -- 关联公司 ID
            product_id INTEGER,                     -- 关联本地产品 ID
            external_product_id VARCHAR(100),       -- 外部产品 ID
            product_name VARCHAR(200),              -- 产品名称
            product_category VARCHAR(100),          -- 产品分类
            price DECIMAL(10,2),                    -- 价格
            stock_quantity INTEGER,                 -- 库存数量
            sync_status VARCHAR(20) DEFAULT 'synced', -- 同步状态：synced/pending/failed
            last_synced_at TIMESTAMP,               -- 最后同步时间
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES partner_companies(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # 合作公司订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER NOT NULL,            -- 关联公司 ID
            order_number VARCHAR(100) UNIQUE,       -- 订单号
            customer_name VARCHAR(200),             -- 客户名称
            product_name VARCHAR(200),              -- 产品名称
            quantity INTEGER,                       -- 数量
            amount DECIMAL(10,2),                   -- 金额
            order_date DATE,                        -- 订单日期
            order_status VARCHAR(50),               -- 订单状态
            notes TEXT,                             -- 备注
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (partner_id) REFERENCES partner_companies(id)
        )
    ''')

    conn.commit()

    # 为 products 表添加 series_id 列（如果不存在）
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN series_id INTEGER REFERENCES product_series(id)')
        cursor.execute('ALTER TABLE products ADD COLUMN series_name VARCHAR(100)')
        conn.commit()
        print("✅ 已添加 series_id 和 series_name 字段到 products 表")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️ series_id 和 series_name 字段已存在，跳过添加")
        else:
            raise

    conn.close()
    print(f"✅ 数据库初始化完成：{DB_PATH.absolute()}")

# ==================== 产品系列管理 ====================
class SeriesManager:
    """产品系列管理器"""

    @staticmethod
    def add_series(brand: str, series_name: str, description: str = None) -> int:
        """添加产品系列"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO product_series (brand, series_name, description)
                VALUES (?, ?, ?)
            ''', (brand, series_name, description))
            series_id = cursor.lastrowid
            conn.commit()
            return series_id
        except sqlite3.IntegrityError:
            # 系列已存在，返回现有 ID
            cursor.execute(
                'SELECT id FROM product_series WHERE brand = ? AND series_name = ?',
                (brand, series_name)
            )
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else -1

    @staticmethod
    def get_all_series() -> List[Dict]:
        """获取所有系列"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM product_series ORDER BY brand, series_name')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_series_by_brand(brand: str) -> List[Dict]:
        """获取指定品牌的所有系列"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM product_series WHERE brand = ? ORDER BY series_name',
            (brand,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_series_by_id(series_id: int) -> Optional[Dict]:
        """根据 ID 获取系列"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM product_series WHERE id = ?', (series_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def delete_series(series_id: int) -> bool:
        """删除系列（不删除产品，仅解除关联）"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 解除该系列下所有产品的关联
        cursor.execute('UPDATE products SET series_id = NULL WHERE series_id = ?', (series_id,))
        cursor.execute('DELETE FROM product_series WHERE id = ?', (series_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_all_brands() -> List[str]:
        """获取所有品牌（去重列表）"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT DISTINCT brand FROM product_series ORDER BY brand')
        rows = cursor.fetchall()
        conn.close()

        return [row['brand'] for row in rows]


# ==================== 冠辰科技方案开发服务管理系统 ====================
class SolutionManager:
    """方案库管理器"""

    @staticmethod
    def add_solution(solution_data: Dict) -> int:
        """添加方案"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO solutions (
                solution_name, domain, sub_domain, solution_type,
                application, core_chip, features, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            solution_data.get('solution_name', ''),
            solution_data.get('domain', ''),
            solution_data.get('sub_domain', ''),
            solution_data.get('solution_type', '标准方案'),
            solution_data.get('application', ''),
            solution_data.get('core_chip', ''),
            solution_data.get('features', ''),
            solution_data.get('description', ''),
            solution_data.get('status', '开发中')
        ))

        solution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return solution_id

    @staticmethod
    def get_all_solutions(domain: str = None, status: str = None) -> List[Dict]:
        """获取所有方案（支持筛选）"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM solutions WHERE 1=1'
        params = []

        if domain:
            query += ' AND domain = ?'
            params.append(domain)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params if params else ())
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_solution_by_id(solution_id: int) -> Optional[Dict]:
        """根据 ID 获取方案"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM solutions WHERE id = ?', (solution_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def update_solution(solution_id: int, solution_data: Dict) -> bool:
        """更新方案"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE solutions SET
                solution_name = ?, domain = ?, sub_domain = ?,
                solution_type = ?, application = ?, core_chip = ?,
                features = ?, description = ?, status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            solution_data.get('solution_name', ''),
            solution_data.get('domain', ''),
            solution_data.get('sub_domain', ''),
            solution_data.get('solution_type', '标准方案'),
            solution_data.get('application', ''),
            solution_data.get('core_chip', ''),
            solution_data.get('features', ''),
            solution_data.get('description', ''),
            solution_data.get('status', '开发中'),
            solution_id
        ))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete_solution(solution_id: int) -> bool:
        """删除方案"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 先删除关联文档
        cursor.execute('DELETE FROM solution_documents WHERE solution_id = ?', (solution_id,))
        cursor.execute('DELETE FROM solution_distributions WHERE solution_id = ?', (solution_id,))
        cursor.execute('DELETE FROM solutions WHERE id = ?', (solution_id,))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def batch_delete_solutions(solution_ids: List[int]) -> int:
        """批量删除方案"""
        count = 0
        for sid in solution_ids:
            if SolutionManager.delete_solution(sid):
                count += 1
        return count

    @staticmethod
    def get_domains() -> List[str]:
        """获取所有领域（去重）"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT DISTINCT domain FROM solutions ORDER BY domain')
        rows = cursor.fetchall()
        conn.close()

        return [row['domain'] for row in rows]

    @staticmethod
    def get_statistics() -> Dict:
        """获取方案统计信息"""
        conn = get_db_connection()
        cursor = conn.cursor()

        stats = {}

        # 按领域统计
        cursor.execute('''
            SELECT domain, COUNT(*) as count
            FROM solutions
            GROUP BY domain
        ''')
        stats['by_domain'] = {row['domain']: row['count'] for row in cursor.fetchall()}

        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM solutions
            GROUP BY status
        ''')
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

        # 按类型统计
        cursor.execute('''
            SELECT solution_type, COUNT(*) as count
            FROM solutions
            GROUP BY solution_type
        ''')
        stats['by_type'] = {row['solution_type']: row['count'] for row in cursor.fetchall()}

        conn.close()
        return stats


class SolutionDocumentManager:
    """方案文档管理器"""

    @staticmethod
    def add_document(solution_id: int, doc_name: str, doc_type: str, file_path: str, file_size: int = None, description: str = None) -> int:
        """添加方案文档"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO solution_documents (solution_id, doc_name, doc_type, file_path, file_size, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (solution_id, doc_name, doc_type, file_path, file_size, description))

        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id

    @staticmethod
    def get_documents_by_solution(solution_id: int) -> List[Dict]:
        """获取方案的所有文档"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM solution_documents
            WHERE solution_id = ?
            ORDER BY uploaded_at DESC
        ''', (solution_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def delete_document(doc_id: int) -> bool:
        """删除文档"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM solution_documents WHERE id = ?', (doc_id,))
        conn.commit()
        conn.close()
        return True


class CustomerManager:
    """客户管理器"""

    @staticmethod
    def add_customer(customer_data: Dict) -> int:
        """添加客户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 将偏好领域转为 JSON
        preferred_domains = customer_data.get('preferred_domains', [])
        if isinstance(preferred_domains, list):
            preferred_domains = json.dumps(preferred_domains)

        cursor.execute('''
            INSERT INTO customers (
                company_name, contact_person, contact_phone, contact_email,
                industry, region, customer_type, preferred_domains, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_data.get('company_name', ''),
            customer_data.get('contact_person', ''),
            customer_data.get('contact_phone', ''),
            customer_data.get('contact_email', ''),
            customer_data.get('industry', ''),
            customer_data.get('region', ''),
            customer_data.get('customer_type', '潜在'),
            preferred_domains,
            customer_data.get('notes', '')
        ))

        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id

    @staticmethod
    def get_all_customers(customer_type: str = None) -> List[Dict]:
        """获取所有客户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM customers WHERE 1=1'
        params = []

        if customer_type:
            query += ' AND customer_type = ?'
            params.append(customer_type)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params if params else ())
        rows = cursor.fetchall()
        conn.close()

        customers = [dict(row) for row in rows]

        # 解析 JSON 字段
        for customer in customers:
            if customer.get('preferred_domains'):
                try:
                    customer['preferred_domains'] = json.loads(customer['preferred_domains'])
                except:
                    pass

        return customers

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Dict]:
        """根据 ID 获取客户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()

        if row:
            customer = dict(row)
            if customer.get('preferred_domains'):
                try:
                    customer['preferred_domains'] = json.loads(customer['preferred_domains'])
                except:
                    pass
            conn.close()
            return customer

        conn.close()
        return None

    @staticmethod
    def update_customer(customer_id: int, customer_data: Dict) -> bool:
        """更新客户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 将偏好领域转为 JSON
        preferred_domains = customer_data.get('preferred_domains', [])
        if isinstance(preferred_domains, list):
            preferred_domains = json.dumps(preferred_domains)

        cursor.execute('''
            UPDATE customers SET
                company_name = ?, contact_person = ?, contact_phone = ?,
                contact_email = ?, industry = ?, region = ?,
                customer_type = ?, preferred_domains = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            customer_data.get('company_name', ''),
            customer_data.get('contact_person', ''),
            customer_data.get('contact_phone', ''),
            customer_data.get('contact_email', ''),
            customer_data.get('industry', ''),
            customer_data.get('region', ''),
            customer_data.get('customer_type', '潜在'),
            preferred_domains,
            customer_data.get('notes', ''),
            customer_id
        ))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete_customer(customer_id: int) -> bool:
        """删除客户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM solution_distributions WHERE customer_id = ?', (customer_id,))
        cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))

        conn.commit()
        conn.close()
        return True


class DistributionManager:
    """方案分发管理器"""

    @staticmethod
    def add_distribution(solution_id: int, customer_id: int, distribution_type: str = '推荐',
                        distributed_by: str = None, follow_up_date: str = None) -> int:
        """添加分发记录"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO solution_distributions (solution_id, customer_id, distribution_type, distributed_by, follow_up_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (solution_id, customer_id, distribution_type, distributed_by, follow_up_date))

        dist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return dist_id

    @staticmethod
    def get_distributions_by_solution(solution_id: int) -> List[Dict]:
        """获取方案的所有分发记录"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT d.*, c.company_name, c.contact_person
            FROM solution_distributions d
            JOIN customers c ON d.customer_id = c.id
            WHERE d.solution_id = ?
            ORDER BY d.distributed_at DESC
        ''', (solution_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_distributions_by_customer(customer_id: int) -> List[Dict]:
        """获取客户的所有分发记录"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT d.*, s.solution_name, s.domain
            FROM solution_distributions d
            JOIN solutions s ON d.solution_id = s.id
            WHERE d.customer_id = ?
            ORDER BY d.distributed_at DESC
        ''', (customer_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def update_distribution_status(dist_id: int, status: str, feedback: str = None) -> bool:
        """更新分发状态"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE solution_distributions
            SET status = ?, feedback = ?
            WHERE id = ?
        ''', (status, feedback, dist_id))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_distribution_statistics() -> Dict:
        """获取分发统计"""
        conn = get_db_connection()
        cursor = conn.cursor()

        stats = {}

        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM solution_distributions
            GROUP BY status
        ''')
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}

        # 按分发类型统计
        cursor.execute('''
            SELECT distribution_type, COUNT(*) as count
            FROM solution_distributions
            GROUP BY distribution_type
        ''')
        stats['by_type'] = {row['distribution_type']: row['count'] for row in cursor.fetchall()}

        conn.close()
        return stats

# ==================== 产品管理 ====================
class ProductManager:
    """产品数据管理器"""

    @staticmethod
    def add_product(product_data: Dict) -> int:
        """添加产品（带查重功能）"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查重：检查是否已存在相同型号的产品
        model = product_data.get('型号', '')
        if model:
            cursor.execute('SELECT id FROM products WHERE model = ? AND status = "active"', (model,))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return -1  # 返回 -1 表示重复

        # 获取或自动创建系列
        series_id = None
        series_name = product_data.get('系列', None)
        brand = product_data.get('品牌', '冠辰科技')

        if series_name and brand:
            # 尝试获取现有系列
            cursor.execute('SELECT id FROM product_series WHERE brand = ? AND series_name = ?',
                          (brand, series_name))
            row = cursor.fetchone()
            if row:
                series_id = row['id']
            else:
                # 自动创建新系列
                cursor.execute('INSERT INTO product_series (brand, series_name) VALUES (?, ?)',
                              (brand, series_name))
                series_id = cursor.lastrowid

        cursor.execute('''
            INSERT INTO products (
                model, name, brand, category, input_voltage, output_voltage,
                output_current, efficiency, switch_frequency, current_accuracy,
                operating_temp, package, protection, cost, suggested_price,
                pdf_file_path, series_id, series_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_data.get('型号', ''),
            product_data.get('名称', ''),
            product_data.get('品牌', '冠辰科技'),
            product_data.get('分类', 'LED 驱动芯片'),
            product_data.get('输入电压', ''),
            product_data.get('输出电压', ''),
            product_data.get('输出电流', ''),
            product_data.get('效率', ''),
            product_data.get('开关频率', ''),
            product_data.get('电流精度', ''),
            product_data.get('工作温度', ''),
            product_data.get('封装形式', ''),
            product_data.get('保护功能', ''),
            product_data.get('成本', 0),
            product_data.get('建议售价', 0),
            product_data.get('pdf_path', ''),
            series_id,
            series_name
        ))

        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def get_all_products() -> List[Dict]:
        """获取所有产品"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM products WHERE status = "active" ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Dict]:
        """根据 ID 获取产品"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def get_product_by_model(model: str) -> Optional[Dict]:
        """根据型号获取产品（用于查重）"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM products WHERE model = ? AND status = "active"', (model,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def get_products_by_series(series_id: int = None, brand: str = None) -> List[Dict]:
        """根据系列或品牌获取产品"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM products WHERE status = "active"'
        params = []

        if series_id:
            query += ' AND series_id = ?'
            params.append(series_id)
        elif brand:
            query += ' AND brand = ?'
            params.append(brand)

        query += ' ORDER BY series_name, model'

        cursor.execute(query, params if params else ())
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def batch_delete_products(product_ids: List[int]) -> int:
        """批量删除产品"""
        conn = get_db_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(product_ids))
        cursor.execute(f'UPDATE products SET status = "deleted", updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders})', product_ids)
        deleted_count = cursor.rowcount

        conn.commit()
        conn.close()
        return deleted_count

    @staticmethod
    def batch_update_series(product_ids: List[int], series_id: int) -> int:
        """批量更新产品所属系列"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取系列名称
        cursor.execute('SELECT series_name FROM product_series WHERE id = ?', (series_id,))
        row = cursor.fetchone()
        series_name = row['series_name'] if row else ''

        placeholders = ','.join('?' * len(product_ids))
        cursor.execute(f'''
            UPDATE products
            SET series_id = ?, series_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id IN ({placeholders})
        ''', [series_id, series_name] + product_ids)

        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        return updated_count

    @staticmethod
    def update_product(product_id: int, product_data: Dict) -> bool:
        """更新产品"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE products SET
                model = ?, name = ?, brand = ?, category = ?,
                input_voltage = ?, output_voltage = ?, output_current = ?,
                efficiency = ?, switch_frequency = ?, current_accuracy = ?,
                operating_temp = ?, package = ?, protection = ?,
                cost = ?, suggested_price = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            product_data.get('型号', ''),
            product_data.get('名称', ''),
            product_data.get('品牌', '冠辰科技'),
            product_data.get('分类', 'LED 驱动芯片'),
            product_data.get('输入电压', ''),
            product_data.get('输出电压', ''),
            product_data.get('输出电流', ''),
            product_data.get('效率', ''),
            product_data.get('开关频率', ''),
            product_data.get('电流精度', ''),
            product_data.get('工作温度', ''),
            product_data.get('封装形式', ''),
            product_data.get('保护功能', ''),
            product_data.get('成本', 0),
            product_data.get('建议售价', 0),
            product_id
        ))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def delete_product(product_id: int) -> bool:
        """删除产品（软删除）"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('UPDATE products SET status = "deleted", updated_at = CURRENT_TIMESTAMP WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        return True

# ==================== 详情页记录管理 ====================
class DetailPageManager:
    """详情页生成记录管理器"""

    @staticmethod
    def add_record(product_id: int, model: str, html_path: str = None, md_path: str = None):
        """添加生成记录"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO detail_pages (product_id, model, html_path, md_path)
            VALUES (?, ?, ?, ?)
        ''', (product_id, model, html_path, md_path))

        conn.commit()
        conn.close()

    @staticmethod
    def get_latest_page(product_id: int) -> Optional[Dict]:
        """获取产品最新生成的详情页"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM detail_pages
            WHERE product_id = ?
            ORDER BY generated_at DESC
            LIMIT 1
        ''', (product_id,))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def get_all_pages(product_id: int = None) -> List[Dict]:
        """获取所有详情页记录"""
        conn = get_db_connection()
        cursor = conn.cursor()

        if product_id:
            cursor.execute('SELECT * FROM detail_pages WHERE product_id = ? ORDER BY generated_at DESC', (product_id,))
        else:
            cursor.execute('SELECT * FROM detail_pages ORDER BY generated_at DESC')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

# ==================== 上架队列管理 ====================
class UploadQueueManager:
    """上架队列管理器"""

    @staticmethod
    def add_to_queue(product_id: int, model: str, platform: str = '1688'):
        """添加到上架队列"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO upload_queue (product_id, model, platform)
            VALUES (?, ?, ?)
        ''', (product_id, model, platform))

        conn.commit()
        conn.close()

    @staticmethod
    def get_pending_items() -> List[Dict]:
        """获取待上架项目"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM upload_queue
            WHERE status = "pending"
            ORDER BY created_at ASC
        ''')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def mark_completed(queue_id: int):
        """标记为已完成"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE upload_queue
            SET status = "completed", completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (queue_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def get_all_items() -> List[Dict]:
        """获取所有队列项目"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM upload_queue ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

# ==================== 初始化检查 ====================
def ensure_database_initialized():
    """确保数据库已初始化"""
    if not DB_PATH.exists():
        init_database()
    return True


# ==================== 关联公司数据管理 ====================
class PartnerCompanyManager:
    """关联公司数据管理器 - 希懋/智慧世界/宜欧特/日银微电子"""

    @staticmethod
    def add_company(company_data: Dict) -> int:
        """添加关联公司"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO partner_companies (
                company_name, company_code, contact_person, contact_phone,
                contact_email, api_endpoint, api_key, api_secret,
                data_sync_enabled, sync_frequency, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_data.get('company_name', ''),
            company_data.get('company_code', ''),
            company_data.get('contact_person', ''),
            company_data.get('contact_phone', ''),
            company_data.get('contact_email', ''),
            company_data.get('api_endpoint', ''),
            company_data.get('api_key', ''),
            company_data.get('api_secret', ''),
            company_data.get('data_sync_enabled', False),
            company_data.get('sync_frequency', 'daily'),
            company_data.get('notes', '')
        ))

        company_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return company_id

    @staticmethod
    def get_all_companies(status: str = None) -> List[Dict]:
        """获取所有关联公司"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM partner_companies WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params if params else ())
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_company_by_id(company_id: int) -> Optional[Dict]:
        """根据 ID 获取公司"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM partner_companies WHERE id = ?', (company_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def get_company_by_code(company_code: str) -> Optional[Dict]:
        """根据公司代码获取公司"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM partner_companies WHERE company_code = ?', (company_code,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def update_company(company_id: int, company_data: Dict) -> bool:
        """更新公司信息"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE partner_companies SET
                company_name = ?, company_code = ?, contact_person = ?,
                contact_phone = ?, contact_email = ?, api_endpoint = ?,
                api_key = ?, api_secret = ?, data_sync_enabled = ?,
                sync_frequency = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            company_data.get('company_name', ''),
            company_data.get('company_code', ''),
            company_data.get('contact_person', ''),
            company_data.get('contact_phone', ''),
            company_data.get('contact_email', ''),
            company_data.get('api_endpoint', ''),
            company_data.get('api_key', ''),
            company_data.get('api_secret', ''),
            company_data.get('data_sync_enabled', False),
            company_data.get('sync_frequency', 'daily'),
            company_data.get('notes', ''),
            company_id
        ))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def update_sync_status(company_id: int, last_sync_at: datetime = None) -> bool:
        """更新同步状态"""
        conn = get_db_connection()
        cursor = conn.cursor()

        if last_sync_at is None:
            last_sync_at = datetime.now()

        cursor.execute('''
            UPDATE partner_companies SET
                last_sync_at = ?
            WHERE id = ?
        ''', (last_sync_at, company_id))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def add_partner_product(product_data: Dict) -> int:
        """添加合作公司产品"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO partner_products (
                partner_id, product_id, external_product_id, product_name,
                product_category, price, stock_quantity, sync_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_data.get('partner_id'),
            product_data.get('product_id'),
            product_data.get('external_product_id', ''),
            product_data.get('product_name', ''),
            product_data.get('product_category', ''),
            product_data.get('price', 0),
            product_data.get('stock_quantity', 0),
            product_data.get('sync_status', 'pending')
        ))

        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return product_id

    @staticmethod
    def get_partner_products(partner_id: int = None, sync_status: str = None) -> List[Dict]:
        """获取合作公司产品"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT pp.*, pc.company_name
            FROM partner_products pp
            JOIN partner_companies pc ON pp.partner_id = pc.id
            WHERE 1=1
        '''
        params = []

        if partner_id:
            query += ' AND pp.partner_id = ?'
            params.append(partner_id)
        if sync_status:
            query += ' AND pp.sync_status = ?'
            params.append(sync_status)

        query += ' ORDER BY pp.updated_at DESC'

        cursor.execute(query, params if params else ())
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def add_partner_order(order_data: Dict) -> int:
        """添加合作公司订单"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO partner_orders (
                partner_id, order_number, customer_name, product_name,
                quantity, amount, order_date, order_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data.get('partner_id'),
            order_data.get('order_number', ''),
            order_data.get('customer_name', ''),
            order_data.get('product_name', ''),
            order_data.get('quantity', 0),
            order_data.get('amount', 0),
            order_data.get('order_date'),
            order_data.get('order_status', ''),
            order_data.get('notes', '')
        ))

        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id

    @staticmethod
    def get_partner_orders(partner_id: int = None, start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取合作公司订单"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT po.*, pc.company_name
            FROM partner_orders po
            JOIN partner_companies pc ON po.partner_id = pc.id
            WHERE 1=1
        '''
        params = []

        if partner_id:
            query += ' AND po.partner_id = ?'
            params.append(partner_id)
        if start_date:
            query += ' AND po.order_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND po.order_date <= ?'
            params.append(end_date)

        query += ' ORDER BY po.order_date DESC'

        cursor.execute(query, params if params else ())
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_partner_statistics() -> Dict:
        """获取合作公司统计"""
        conn = get_db_connection()
        cursor = conn.cursor()

        stats = {}

        # 公司统计
        cursor.execute('SELECT COUNT(*) as count FROM partner_companies WHERE status = "active"')
        stats['company_count'] = cursor.fetchone()['count']

        # 产品统计
        cursor.execute('SELECT COUNT(*) as count FROM partner_products')
        stats['product_count'] = cursor.fetchone()['count']

        # 订单统计（本月）
        cursor.execute('''
            SELECT COUNT(*) as count, SUM(amount) as total
            FROM partner_orders
            WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')
        ''')
        row = cursor.fetchone()
        stats['orders_this_month'] = row['count'] if row['count'] else 0
        stats['revenue_this_month'] = row['total'] if row['total'] else 0

        # 按公司统计订单
        cursor.execute('''
            SELECT pc.company_name, COUNT(po.id) as order_count, SUM(po.amount) as total_amount
            FROM partner_companies pc
            LEFT JOIN partner_orders po ON pc.id = po.partner_id
            GROUP BY pc.id
        ''')
        stats['by_company'] = {row['company_name']: {'orders': row['order_count'], 'revenue': row['total_amount'] or 0} for row in cursor.fetchall()}

        conn.close()
        return stats
