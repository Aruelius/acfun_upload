# -*- coding: utf-8 -*-

import json
import os
import time
from base64 import b64decode
from hashlib import sha1
from math import ceil
from mimetypes import guess_type

import requests


class AcFun(object):
    def __init__(self):
        self.session = requests.session()
        self.LOGIN_URL    = "https://id.app.acfun.cn/rest/web/login/signin"
        self.TOKEN_URL    = "https://member.acfun.cn/video/api/getKSCloudToken"
        self.FRAGMENT_URL = "https://mediacloud.kuaishou.com/api/upload/fragment"
        self.COMPLETE_URL = "https://mediacloud.kuaishou.com/api/upload/complete"
        self.FINISH_URL   = "https://member.acfun.cn/video/api/uploadFinish"
        self.C_VIDEO_URL  = "https://member.acfun.cn/video/api/createVideo"
        self.C_DOUGA_URL  = "https://member.acfun.cn/video/api/createDouga"
        self.QINIU_URL    = "https://member.acfun.cn/common/api/getQiniuToken"
        self.QINIU_UP_URL = "https://upload.qiniup.com/"
        self.IMAGE_URL    = "https://imgs.aixifan.com/"

    @staticmethod
    def log(*msg: object):
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]', *msg)

    def calc_sha1(self, data: bytes) -> str:
        sha1_obj = sha1()
        sha1_obj.update(data)
        return sha1_obj.hexdigest()

    def login(self, username: str, password: str):
        r = self.session.post(
            url = self.LOGIN_URL,
            data = {
                'username': username,
                'password': password,
                'key': '',
                'captcha': ''
            }
        )
        if r.json()['result'] == 0:
            self.log('登陆成功')
        else:
            self.log("账号密码错误")
            os._exit(0)

    def get_token(self, filename: str, filesize: int) -> tuple:
        r = self.session.post(
            url=self.TOKEN_URL,
            data={
                "fileName": filename,
                "size": filesize,
                "template": "1"
            }
        )
        response = r.json()
        return response["taskId"], response["token"], response["uploadConfig"]["partSize"]

    def upload_chunk(self, block: bytes, fragment_id: int, upload_token: str):
        for _ in range(3):
            r = requests.post(
                url=self.FRAGMENT_URL,
                params={
                    "fragment_id": fragment_id,
                    "upload_token": upload_token
                },
                data=block
            )
            if r.json()["result"] == 1:
                self.log(f"分块{fragment_id+1}上传成功")
                return
            else:
                self.log(f"分块{fragment_id+1}上传失败，重试第{_+1}次", r.text)

    def complete(self, fragment_count: int, upload_token: str):
        r = requests.post(
            url=self.COMPLETE_URL,
            params={
                "fragment_count": fragment_count,
                "upload_token": upload_token
            }
        )
        if r.json()["result"] != 1:
            self.log(r.text)
    
    def upload_finish(self, taskId: int):
        r = self.session.post(
            url=self.FINISH_URL,
            data={
                "taskId": taskId
            }
        )
        if r.json()["result"] != 0:
            self.log(r.text)

    def create_video(self, video_key: int, filename: str) -> int:
        r = self.session.post(
            url=self.C_VIDEO_URL,
            data={
                "videoKey": video_key,
                "fileName": filename,
                "vodType": "ksCloud"
            }
        )
        response = r.json()
        if response["result"] != 0: #  or not response["videoId"]
            self.log(r.text)
        self.upload_finish(video_key)
        return response["videoId"]

    def create_douga(
        self,
        file_path: str, # 视频文件路径，建议绝对路径
        title: str, # 稿件标题
        channel_id: int, # 频道ID，查看：https://gist.github.com/Aruelius/69b60a141d38ce1e1bfcfe1104b98d62
        cover: str, # 视频封面图片路径，建议绝对路径
        desc: str = "", # 稿件简介
        tags: list = [], # 稿件标签
        creation_type: int = 1, # 1,转载 3,原创
        originalLinkUrl: str = "" # 转载来源
        ):

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        task_id, token, part_size = self.get_token(file_name, file_size)
        fragment_count = ceil(file_size / part_size)
        self.log(f"{file_name} 开始上传, 一共{fragment_count}个分块")
        with open(file_path, "rb") as f:
            for fragment_id in range(fragment_count):
                chunk_data = f.read(part_size)
                if not chunk_data:
                    break
                self.upload_chunk(chunk_data, fragment_id, token)
            f.close()

        def add():
            video_id = self.create_video(task_id, file_name)
            data = {
                "title": title,
                "description": desc,
                "tagNames": json.dumps(tags),
                "creationType": creation_type,
                "channelId": channel_id,
                "coverUrl": self.cover(cover),
                "videoInfos": json.dumps([{"videoId": video_id,"title": title}]),
                "isJoinUpCollege": "0"
            }
            if creation_type == 1:
                data["originalLinkUrl"] = originalLinkUrl
                data["originalDeclare"] = "0"
            else:
                data["originalDeclare"] = "1"
            r = self.session.post(
                url=self.C_DOUGA_URL,
                data=data
            )
            response = r.json()
            if response["result"] == 0:
                self.log(f"视频投稿成功！AC号：{response['dougaId']}")
            else:
                self.log(r.text)
        
        self.complete(fragment_count, token)
        add()

    def cover(self, image_path: str):
        """
        封面上传方法，可单独调用，需登录
        """
        image_type = guess_type(image_path)[0]
        suffix = image_type.split("/")[-1] if image_type else "jpeg"
        def get_qiniu_token():
            r = self.session.post(
                url=self.QINIU_URL,
                json={"headers":{"devicetype":7}}
            )
            return b64decode(
                r.json()["info"]["upToken"]
            ).decode("utf-8").replace("null:", "")
        f = open(image_path, "rb")
        file_data = f.read()
        f.close()
        file_sha1 = self.calc_sha1(file_data)
        
        r = requests.post(
            url=self.QINIU_UP_URL,
            data={
               "key": f"afs/cover/{file_sha1}.{suffix}",
               "token": get_qiniu_token()
            },
            files={
                "file": file_data,
            }
        )
        response = r.json()
        return self.IMAGE_URL + response.get("key")
