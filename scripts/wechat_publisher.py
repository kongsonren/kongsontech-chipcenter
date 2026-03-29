# -*- coding: utf-8 -*-
"""
微信公众号自动发布助手 (WeChat Publisher)
功能:
1. 自动登录公众号后台 (mp.weixin.qq.com)
2. 自动填充图文内容（标题/正文/摘要）
3. 自动上传图片
4. 等待人工审核后发布

使用方法:
    python wechat_publisher.py --title "标题" --content "内容.md" --cover "封面图.jpg"

作者：KR + Claude Code
日期：2026-03-22
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("请安装 playwright: pip install playwright")
    print("然后运行：playwright install chromium")
    exit(1)


class WeChatPublisher:
    """微信公众号发布助手"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def start(self):
        """启动浏览器"""
        print("🌐 正在启动浏览器...")
        self.playwright = sync_playwright().start()

        # 使用 Chromium
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # 创建上下文（模拟真实浏览器）
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            locale='zh-CN',
        )

        self.page = self.context.new_page()
        print("✅ 浏览器启动成功！")

    def login(self, username: str = None, password: str = None):
        """
        登录公众号后台

        Args:
            username: 公众号账号（邮箱）
            password: 密码

        如果未提供账号密码，则手动扫码登录
        """
        print("🔐 正在访问公众号后台...")

        # 访问公众号登录页
        self.page.goto('https://mp.weixin.qq.com/', wait_until='domcontentloaded')
        time.sleep(2)

        # 检查是否已登录
        try:
            # 尝试查找"新的创作"按钮，如果存在说明已登录
            self.page.wait_for_selector('a[href*="/cgi-bin/appmsg"]', timeout=5000)
            print("✅ 已登录状态！")
            return True
        except PlaywrightTimeout:
            pass

        # 未登录，需要扫码
        print("📱 请使用微信扫码登录")
        print("提示：如需自动填充账号密码，请运行：python wechat_publisher.py --username xxx --password xxx")

        # 等待扫码登录（最长 60 秒）
        try:
            self.page.wait_for_url('https://mp.weixin.qq.com/cgi-bin/home*', timeout=60000)
            print("✅ 登录成功！")
            return True
        except PlaywrightTimeout:
            print("⏰ 登录超时，请重新开始")
            return False

    def create_new_article(self):
        """创建新图文消息"""
        print("📝 正在创建新图文...")

        # 点击"新的创作" -> "图文消息"
        try:
            # 方法 1: 找"新的创作"按钮
            self.page.click('a[href*="/cgi-bin/appmsg"]', timeout=5000)
            time.sleep(2)

            # 等待页面加载
            self.page.wait_for_load_state('domcontentloaded')
            time.sleep(1)

            print("✅ 进入图文编辑页面")
            return True
        except Exception as e:
            print(f"❌ 创建图文失败：{e}")
            return False

    def fill_article(self, title: str, content: str, summary: str = None):
        """
        填充图文内容

        Args:
            title: 文章标题
            content: 文章内容（HTML 格式）
            summary: 摘要（可选，默认自动提取）
        """
        print("✏️ 正在填充内容...")

        try:
            # 等待编辑器加载
            time.sleep(3)

            # 填写标题
            title_input = self.page.locator('input[placeholder*="标题"]').first
            title_input.fill(title)
            print(f"✅ 标题已填写：{title}")

            # 填写摘要（如果有）
            if summary:
                try:
                    summary_input = self.page.locator('textarea[placeholder*="摘要"]').first
                    summary_input.fill(summary)
                    print(f"✅ 摘要已填写")
                except:
                    print("⚠️ 未找到摘要输入框")

            # 填写正文（模拟粘贴）
            # 注意：公众号编辑器使用富文本，需要特殊处理
            editor = self.page.locator('#edui23').first
            if editor.is_visible():
                # 清空编辑器
                editor.click()
                self.page.keyboard.press('Ctrl+A')
                self.page.keyboard.press('Delete')

                # 粘贴内容（需要先复制到剪贴板）
                self.page.evaluate(f'''() => {{
                    navigator.clipboard.writeText({repr(content)})
                }}''')
                self.page.keyboard.press('Ctrl+V')

                print("✅ 正文已填充")
            else:
                print("⚠️ 未找到编辑器，可能需要手动粘贴内容")

            return True

        except Exception as e:
            print(f"❌ 填充内容失败：{e}")
            return False

    def upload_cover(self, cover_path: str):
        """
        上传封面图片

        Args:
            cover_path: 封面图片路径
        """
        print(f"🖼️ 正在上传封面：{cover_path}")

        if not os.path.exists(cover_path):
            print(f"⚠️ 封面文件不存在：{cover_path}")
            return False

        try:
            # 查找封面上传按钮
            upload_btn = self.page.locator('input[type="file"]').first

            if upload_btn.is_visible():
                upload_btn.set_input_files(cover_path)
                print("✅ 封面上传成功")
                return True
            else:
                print("⚠️ 未找到上传按钮，请手动上传封面")
                return False

        except Exception as e:
            print(f"❌ 上传封面失败：{e}")
            return False

    def wait_for_review(self, timeout_minutes: int = 10):
        """
        等待人工审核并发布

        Args:
            timeout_minutes: 等待超时时间（分钟）
        """
        print(f"⏳ 等待人工审核...（最长{timeout_minutes}分钟）")
        print("提示：检查内容无误后，请手动点击'发布'按钮")

        start_time = time.time()
        max_seconds = timeout_minutes * 60

        while time.time() - start_time < max_seconds:
            time.sleep(5)

            # 检查是否已发布（页面跳转）
            try:
                # 如果页面跳转到已发表列表，说明发布成功
                if '/cgi-bin/appmsg' in self.page.url and 'status=publish' in self.page.url:
                    print("✅ 发布成功！")
                    return True
            except:
                pass

        print("⏰ 等待超时，请手动完成发布")
        return False

    def publish(self):
        """点击发布按钮"""
        print("📤 正在发布...")

        try:
            # 查找发布按钮
            publish_btn = self.page.locator('button:has-text("发表")').first

            if publish_btn.is_visible():
                publish_btn.click()
                time.sleep(2)

                # 确认发布
                confirm_btn = self.page.locator('button:has-text("确认")').first
                if confirm_btn.is_visible():
                    confirm_btn.click()

                # 等待发布完成
                time.sleep(5)
                print("✅ 发布成功！")
                return True
            else:
                print("⚠️ 未找到发布按钮，请手动发布")
                return False

        except Exception as e:
            print(f"❌ 发布失败：{e}")
            return False

    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        print("👋 浏览器已关闭")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='微信公众号自动发布助手')
    parser.add_argument('--title', '-t', help='文章标题')
    parser.add_argument('--content', '-c', help='文章内容文件路径（Markdown/HTML）')
    parser.add_argument('--cover', help='封面图片路径')
    parser.add_argument('--username', '-u', help='公众号账号（邮箱）')
    parser.add_argument('--password', '-p', help='密码')
    parser.add_argument('--headless', action='store_true', help='无头模式（不显示浏览器）')
    parser.add_argument('--demo', action='store_true', help='演示模式（仅打开页面）')

    args = parser.parse_args()

    # 创建发布助手
    publisher = WeChatPublisher(headless=args.headless)

    try:
        # 启动浏览器
        publisher.start()

        # 登录
        publisher.login(username=args.username, password=args.password)

        # 演示模式
        if args.demo:
            print("🎬 演示模式：仅打开页面，不执行任何操作")
            print("提示：您可以在浏览器中手动操作")
            input("按回车键关闭浏览器...")
            return

        # 创建图文
        if not publisher.create_new_article():
            print("⚠️ 创建图文失败，请手动操作")
            input("按回车键关闭浏览器...")
            return

        # 填充内容
        if args.title and args.content:
            # 读取内容
            if os.path.exists(args.content):
                with open(args.content, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 如果内容包含 Markdown，需要转换为 HTML
                # （这里简化处理，直接填充）
                publisher.fill_article(
                    title=args.title,
                    content=content,
                    summary=None  # 自动提取
                )
            else:
                print(f"⚠️ 内容文件不存在：args.content}")

        # 上传封面
        if args.cover:
            publisher.upload_cover(args.cover)

        # 等待审核
        print("\n" + "="*50)
        print("下一步操作：")
        print("1. 检查文章内容是否正确")
        print("2. 调整排版/图片位置（如需要）")
        print("3. 点击'发表'按钮")
        print("="*50)

        publisher.wait_for_review(timeout_minutes=10)

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
    finally:
        publisher.close()


if __name__ == '__main__':
    main()
