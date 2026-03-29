@echo off
chcp 65001 >nul
echo ========================================
echo 内容生成器测试
echo ========================================
echo.

cd /d %~dp0

echo 正在测试公众号推文生成...
python -c "from scripts.content_generator import ContentGenerator; g = ContentGenerator('LM2596', {'efficiency': '87%', 'temp_rise': '35°C', 'ripple': '80mVpp', 'chip_type': 'DC-DC 芯片'}); print(g.generate_wechat_article()[:500])"

echo.
echo ========================================
echo 测试完成!
echo ========================================
pause
