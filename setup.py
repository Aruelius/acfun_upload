import setuptools
import acfun_upload

with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.readlines()

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setuptools.setup(
    name="acfun_upload",
    version=acfun_upload.__version__,
    packages=setuptools.find_packages(),
    url="https://github.com/Aruelius/acfun_upload",
    license="GNU General Public License v3.0",
    author=acfun_upload.__author__,
    author_email=acfun_upload.__email__,
    description="AcFun 命令行投稿工具。Upload video to AcFun with Python.",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=["acfun", "upload", "acfun投稿", "投稿脚本"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Internet :: WWW/HTTP"
    ],
    install_requires=install_requires,
    python_requires=">=3.6"
)