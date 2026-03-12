from setuptools import setup, find_packages

setup(
    name="wuwa-planner",
    version="1.0.0",
    description="鸣潮账号规划文档编辑器",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="鬼神莫能窥",
    url="https://github.com/yourusername/wuwa-planner",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "wuwa-planner=web_editor:main",
        ],
    },
)
