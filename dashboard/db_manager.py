# -*- coding: utf-8 -*-
"""
数据库管理工具 - Database Management Tool
用于查看和管理芯片自动化工作流的数据库

作者：KR + Claude Code
日期：2026-03-22
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from database import (
    ProductManager,
    DetailPageManager,
    UploadQueueManager,
    DB_PATH
)

st.set_page_config(page_title="数据库管理", page_icon="🗄️", layout="wide")

st.title("🗄️ 数据库管理工具")
st.markdown("**芯片自动化工作流 - 数据持久化管理后台**")

# 数据库信息
st.subheader("📊 数据库状态")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("数据库文件", "✅ 存在" if DB_PATH.exists() else "❌ 不存在")

with col2:
    if DB_PATH.exists():
        size_kb = DB_PATH.stat().st_size / 1024
        st.metric("文件大小", f"{size_kb:.2f} KB")
    else:
        st.metric("文件大小", "N/A")

with col3:
    st.metric("数据库路径", str(DB_PATH.absolute()))

st.divider()

# 菜单
menu = st.segmented_control(
    "管理模块",
    ["📦 产品管理", "📄 详情页记录", "🚀 上架队列"]
)

# ==================== 产品管理 ====================
if menu == "📦 产品管理":
    st.header("📦 产品数据管理")

    # 获取所有产品
    products = ProductManager.get_all_products()

    if products:
        st.success(f"共有 {len(products)} 个产品")

        # 搜索框
        search = st.text_input("🔍 搜索产品型号或名称", placeholder="输入型号或名称搜索...")

        if search:
            filtered = [p for p in products if search.lower() in p.get('model', '').lower() or search.lower() in p.get('name', '').lower()]
        else:
            filtered = products

        if filtered:
            st.dataframe(
                filtered,
                use_container_width=True,
                column_config={
                    "id": "ID",
                    "model": "型号",
                    "name": "产品名称",
                    "brand": "品牌",
                    "category": "分类",
                    "input_voltage": "输入电压",
                    "output_voltage": "输出电压",
                    "output_current": "输出电流",
                    "efficiency": "效率",
                    "cost": st.column_config.NumberColumn("成本", format="¥%.2f"),
                    "suggested_price": st.column_config.NumberColumn("建议售价", format="¥%.2f"),
                    "status": "状态",
                    "created_at": "创建时间",
                    "updated_at": "更新时间"
                }
            )
        else:
            st.warning("没有找到匹配的产品")
    else:
        st.info("暂无产品数据")

# ==================== 详情页记录 ====================
elif menu == "📄 详情页记录":
    st.header("📄 1688 详情页生成记录")

    # 获取所有记录
    pages = DetailPageManager.get_all_pages()

    if pages:
        st.success(f"共有 {len(pages)} 条详情页生成记录")

        for page in pages:
            with st.expander(f"**{page['model']}** - 生成于 {page['generated_at']}"):
                col1, col2 = st.columns(2)

                html_path = Path(page.get('html_path', ''))
                md_path = Path(page.get('md_path', ''))

                with col1:
                    st.markdown("**📄 HTML 文件**")
                    if html_path.exists():
                        st.success(f"✅ 存在")
                        st.link_button("🌐 打开 HTML", f"file://{html_path.absolute().as_posix()}")
                    else:
                        st.error("❌ 文件不存在")
                    st.code(str(html_path))

                with col2:
                    st.markdown("**📝 Markdown 文件**")
                    if md_path.exists():
                        st.success(f"✅ 存在")
                        st.link_button("�� 打开 MD", f"file://{md_path.absolute().as_posix()}")
                    else:
                        st.error("❌ 文件不存在")
                    st.code(str(md_path))
    else:
        st.info("暂无详情页生成记录")

# ==================== 上架队列 ====================
elif menu == "🚀 上架队列":
    st.header("🚀 上架队列管理")

    # 获取所有队列项目
    all_items = UploadQueueManager.get_all_items()
    pending_items = UploadQueueManager.get_pending_items()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("待上架", len(pending_items))
    with col2:
        st.metric("总计", len(all_items))

    st.divider()

    if pending_items:
        st.subheader("🔄 待上架产品")
        for item in pending_items:
            with st.expander(f"**{item['model']}** - {item['platform']}"):
                st.write(f"**队列 ID:** {item['id']}")
                st.write(f"**产品 ID:** {item['product_id']}")
                st.write(f"**创建时间:** {item['created_at']}")

                if st.button("✅ 标记为已完成", key=f"complete_{item['id']}"):
                    UploadQueueManager.mark_completed(item['id'])
                    st.success("已标记为完成")
                    st.rerun()
    else:
        st.success("✅ 没有待上架的产品")

    st.divider()

    if all_items:
        st.subheader("📋 全部历史记录")
        for item in all_items[:20]:
            status_icon = "✅" if item['status'] == 'completed' else "⏳"
            st.write(f"{status_icon} **{item['model']}** ({item['platform']}) - {item['status']} - {item['created_at']}")
