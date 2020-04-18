# AcFun 投稿工具
![](https://img.shields.io/badge/pypi-v0.0.1-red) ![](https://img.shields.io/badge/license-GPL%20v3-ff69b4) ![](https://img.shields.io/badge/build-success-brightgreen) ![](https://img.shields.io/badge/Python-3.7-39c5bb)  
基于 Python 的命令行投稿工具

## 安装
```shell
pip install acfun_upload
```
## 使用
```python
from acfun_upload import AcFun
acfun = AcFun()
acfun.login(username="", password="")
acfun.create_douga(...)
```
create_douga 参数  
| 参数 | 注释 | 是否必须 | 类型 |
| :-----| :---- | :----: | :----: |
| file_path | 视频文件路径，建议绝对路径 | 是 | str |
| title | 稿件标题 | 是 | str |
| channel_id | 频道 ID，查看：[频道 ID 汇总](https://gist.github.com/Aruelius/69b60a141d38ce1e1bfcfe1104b98d62) | 是 | int |
| cover | 视频封面图片路径，建议绝对路径 | 是 | str |
| desc | 稿件简介 | 否 | str |
| tags | 稿件标签 | 否 | list |
| creation_type | 创作类型 1:转载 3:原创，默认1 | 是 | int |
| originalLinkUrl | 转载来源 | 否 | str |
## License
[GNU General Public License v3.0](https://github.com/Aruelius/acfun_upload/blob/master/LICENSE)  