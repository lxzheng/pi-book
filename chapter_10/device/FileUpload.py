import os
import requests


class FileUpload:
    def __init__(
            self, 
            url: str = 'http://192.168.8.20:5000/upload-photo',
        ):
        self.url = url

    def upload(self, file_name: str):
        try:
            # 使用with语句确保文件正确关闭
            with open(file_name, 'rb') as f:
                files = {'photo': f}
                response = requests.post(self.url, files=files)
                result = response.json()
                print(result)
                return result
        finally:
            # 无论上传是否成功，都删除文件
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"文件 {file_name} 已删除")


if __name__ == "__main__":
    file_upload = FileUpload()
    file_upload.upload('flower.jpg')