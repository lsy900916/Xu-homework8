#!/usr/bin/env python
"""
依赖检查脚本 - 验证所有关键依赖是否安装成功
"""
import sys

print("=" * 60)
print("开始检查依赖...")
print("=" * 60)

# 要检查的依赖列表
dependencies = [
    ("Flask", "flask"),
    ("SQLAlchemy", "sqlalchemy"),
    ("PyTorch", "torch"),
    ("Sentence Transformers", "sentence_transformers"),
    ("FAISS", "faiss"),
    ("Pandas", "pandas"),
    ("BeautifulSoup", "bs4"),
    ("Jieba", "jieba"),
    ("Scikit-learn", "sklearn"),
    ("Bcrypt", "bcrypt"),
    ("Loguru", "loguru"),
    ("Pydantic", "pydantic"),
    ("Pytest", "pytest"),
]

all_ok = True
results = []

for name, module in dependencies:
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', '未知版本')
        results.append((name, "✅", version))
        print(f"✅ {name:25s} - 已安装 (v{version})")
    except ImportError:
        results.append((name, "❌", "未安装"))
        print(f"❌ {name:25s} - 未安装")
        all_ok = False

print("=" * 60)

if all_ok:
    print("🎉 所有依赖检查通过！可以启动应用了。")
    print("\n下一步:")
    print("  1. python scripts/init_db.py      # 初始化数据库")
    print("  2. python scripts/create_admin.py # 创建管理员")
    print("  3. python app.py                  # 启动服务")
    sys.exit(0)
else:
    print("⚠️  部分依赖缺失，请安装:")
    print("\n  pip install -r requirements.txt")
    print("\n或单独安装缺失的包:")
    for name, status, version in results:
        if status == "❌":
            module = [m for n, m in dependencies if n == name][0]
            print(f"  pip install {module}")
    sys.exit(1)

