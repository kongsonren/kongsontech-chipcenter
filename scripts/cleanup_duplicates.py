# -*- coding: utf-8 -*-
"""
清理重复产品数据
保留每个型号中 ID 最小的记录，删除其他重复记录
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/chip_workflow.db")

def cleanup_duplicates():
    """清理重复产品"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 查找重复的型号
    cursor.execute('''
        SELECT model, COUNT(*) as cnt, MIN(id) as min_id
        FROM products
        WHERE status = "active"
        GROUP BY model
        HAVING cnt > 1
    ''')

    duplicates = cursor.fetchall()

    if not duplicates:
        print("✅ 没有发现重复数据")
        return

    print(f"🔍 找到 {len(duplicates)} 个重复的型号:")

    total_deleted = 0

    for dup in duplicates:
        model = dup['model']
        count = dup['cnt']
        keep_id = dup['min_id']

        print(f"\n  型号 {model}: 共 {count} 条，保留 ID={keep_id}")

        # 删除重复记录（保留 ID 最小的）
        cursor.execute('''
            DELETE FROM products
            WHERE model = ? AND status = "active" AND id != ?
        ''', (model, keep_id))

        deleted_count = cursor.rowcount
        total_deleted += deleted_count
        print(f"    已删除 {deleted_count} 条重复记录")

    conn.commit()

    # 验证清理结果
    cursor.execute('''
        SELECT COUNT(*) as cnt FROM products WHERE status = "active"
    ''')
    final_count = cursor.fetchone()['cnt']

    print(f"\n✅ 清理完成！")
    print(f"   共删除 {total_deleted} 条重复记录")
    print(f"   剩余产品总数：{final_count}")

    conn.close()

if __name__ == "__main__":
    cleanup_duplicates()
