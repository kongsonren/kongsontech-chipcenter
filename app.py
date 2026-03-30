# -*- coding: utf-8 -*-
"""
芯片产品作战看板 - 简化版 (Streamlit Cloud 兼容)
Chip Product Dashboard - Simplified Version for Streamlit Cloud

作者：KR (Kongson Ren)
日期：2026-03-30
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 页面配置
st.set_page_config(
    page_title="KR 的芯片作战指挥中心",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #FF6A00;
    text-align: center;
    padding: 1rem 0;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown("### 🎯 导航菜单")
    page = st.radio(
        "选择页面",
        ["📊 作战指挥中心", "📦 产品管理", "📈 数据分析", "⚙️ 设置"],
        index=0
    )
    
    st.markdown("---")
    st.info("**作者**: KR (Kongson Ren)\n\n**版本**: 1.0.0\n\n**最后更新**: 2026-03-30")

# 主标题
st.markdown("<h1 class='main-header'>🚀 KR 的芯片作战指挥中心</h1>", unsafe_allow_html=True)
st.markdown("---")

# 根据选择显示不同页面
if page == "📊 作战指挥中心":
    st.header("📊 实时作战看板")
    
    # 示例数据
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("在线产品数", "156", "+12")
    
    with col2:
        st.metric("今日访问", "1,234", "+8.5%")
    
    with col3:
        st.metric("1688 上架", "89", "+5")
    
    with col4:
        st.metric("待处理任务", "23", "-3")
    
    # 示例图表
    st.markdown("### 📈 销售趋势")
    
    # 创建示例数据
    dates = pd.date_range(start="2026-01-01", periods=30, freq="D")
    sales_data = pd.DataFrame({
        "日期": dates,
        "销售额": [1000 + i * 50 + (i % 7) * 100 for i in range(30)],
        "订单数": [50 + i * 2 + (i % 5) * 10 for i in range(30)]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sales = px.line(sales_data, x="日期", y="销售额", 
                           title="30 天销售趋势",
                           markers=True)
        fig_sales.update_layout(height=400)
        st.plotly_chart(fig_sales, use_container_width=True)
    
    with col2:
        fig_orders = px.bar(sales_data, x="日期", y="订单数",
                           title="30 天订单趋势",
                           color="订单数")
        fig_orders.update_layout(height=400)
        st.plotly_chart(fig_orders, use_container_width=True)
    
    # 产品表格
    st.markdown("### 📦 热门产品")
    
    products_data = pd.DataFrame({
        "产品型号": ["LED-001", "LED-002", "RGB-001", "WS2812B", "SK6812"],
        "类别": ["室内照明", "氛围灯", "RGB 控制器", "LED 灯带", "LED 灯带"],
        "价格 (¥)": [15.99, 29.99, 45.00, 12.50, 18.00],
        "库存": [500, 300, 150, 800, 600],
        "状态": ["✓ 已上架", "✓ 已上架", "⏳ 准备中", "✓ 已上架", "✓ 已上架"]
    })
    
    st.dataframe(products_data, use_container_width=True, hide_index=True)

elif page == "📦 产品管理":
    st.header("📦 产品管理")
    st.info(" 此功能需要连接数据库。完整版将在本地部署后提供。")
    
    st.markdown("""
    ### 功能列表
    
    - ✅ PDF 规格书上传与解析
    - ✅ 1688 产品上架监控
    - ✅ 销售数据追踪
    - ✅ 库存管理
    - ✅ 自动定价
    
    **当前状态**: 简化演示版
    """)

elif page == "📈 数据分析":
    st.header("📈 数据分析")
    
    # 平台分布图
    st.markdown("### 平台销售分布")
    
    platform_data = pd.DataFrame({
        "平台": ["1688", "淘宝", "天猫", "京东", "拼多多"],
        "销售额": [45000, 28000, 35000, 22000, 18000],
        "占比": [45, 28, 35, 22, 18]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(platform_data, values="销售额", names="平台",
                        title="各平台销售占比")
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(platform_data, x="平台", y="销售额",
                        title="各平台销售额对比",
                        color="销售额")
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

elif page == "⚙️ 设置":
    st.header("⚙️ 系统设置")
    
    st.markdown("""
    ### 系统信息
    
    - **版本**: 1.0.0 (Simplified)
    - **部署平台**: Streamlit Cloud
    - **作者**: KR (Kongson Ren)
    - **公司**: 中山宜欧特灯饰商行
    
    ### 配置选项
    
    完整版将提供：
    - 数据库连接配置
    - API 密钥管理
    - 团队权限设置
    - 自动化规则配置
    """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>© 2026 中山宜欧特灯饰商行 | Powered by Streamlit</p>
    <p>联系人：任光成 (Kongson Ren) | Email: kongsonren@gmail.com</p>
</div>
""", unsafe_allow_html=True)
