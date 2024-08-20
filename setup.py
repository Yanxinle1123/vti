from setuptools import setup, find_packages

setup(
    name="vti",
    version="0.3.2",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "psutil",
    ],
    author="YanXinle",
    author_email="1020121123@qq.com",
    description="视频转图片的工具",
    url="https://github.com/Yanxinle1123/vti",
)
