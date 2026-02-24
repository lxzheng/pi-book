from flask import Flask, jsonify, render_template, request
import os
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.auth.credentials import DerivedCredentials
from huaweicloudsdkcore.region.region import Region as coreRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkiotda.v5 import *
import requests
from datetime import datetime
import json
from typing import Optional
# from werkzeug.utils import secure_filename



app = Flask(__name__, static_url_path='/static', static_folder='static')
app.json.ensure_ascii = False  # 添加这行来全局设置 JSON 编码

# 添加允许的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_iotda_client():
    ak = "***************"
    sk = "***************"
    endpoint = "https://**********.st1.iotda-app.cn-north-4.myhuaweicloud.com"

    credentials = BasicCredentials(ak, sk).with_derived_predicate(
        DerivedCredentials.get_default_derived_predicate()
    )

    return IoTDAClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(coreRegion(id="cn-north-4", endpoint=endpoint)) \
        .build()

# 添加 Coze API 的配置
COZE_API_ENDPOINT = "https://api.coze.cn/v3/chat"
COZE_ACCESS_TOKEN = "your_access_token_here"  # 请替换为实际的访问令牌

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-device-shadow')
def get_device_shadow():
    try:
        client = get_iotda_client()
        request = ShowDeviceShadowRequest()
        device_id = "6766746e2ff1872637c94378_test"

        request.device_id = device_id
        response = client.show_device_shadow(request)
        response_dict = response.to_dict()
        print(f"API响应: {response_dict}")  # 添加日志

        return jsonify({
            "success": True,
            "data": response_dict
        })
    except exceptions.ClientRequestException as e:
        print(f"华为云API错误: {e.error_msg}")  # 添加日志
        return jsonify({
            "success": False,
            "error": {
                "status_code": e.status_code,
                "request_id": e.request_id,
                "error_code": e.error_code,
                "error_msg": e.error_msg
            }
        }), 400
    except Exception as e:
        print(f"未知错误: {str(e)}")  # 添加日志
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/take-photo')
def take_photo():
    try:
        client = get_iotda_client()
        request = CreateCommandRequest()
        request.device_id = os.environ.get("DEVICE_ID")
        request.body = DeviceCommandRequest(
            paras={},
            command_name="camera"
        )

        response = client.create_command(request)
        print(f"拍照命令响应: {response}")

        return jsonify({
            "success": True,
            "data": response.to_dict()
        })
    except exceptions.ClientRequestException as e:
        print(f"华为云API错误: {e.error_msg}")
        return jsonify({
            "success": False,
            "error": {
                "status_code": e.status_code,
                "request_id": e.request_id,
                "error_code": e.error_code,
                "error_msg": e.error_msg
            }
        }), 400
    except Exception as e:
        print(f"拍照错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/control-pump', methods=['POST'])
def control_pump():
    try:
        client = get_iotda_client()

        # 从 flask.request 获取 JSON 数据
        duration = request.json.get('duration', 1)  # 修改这里
        if not isinstance(duration, int) or duration < 1 or duration > 10:
            return jsonify({
                "success": False,
                "error": "浇水时间必须在1-10秒之间"
            }), 400

        command_request = CreateCommandRequest()  # 重命名变量避免混淆
        command_request.device_id = os.environ.get("DEVICE_ID")
        command_request.body = DeviceCommandRequest(
            paras={"duration": duration},
            command_name="pump"
        )

        response = client.create_command(command_request)
        print(f"浇水命令响应: {response}")

        return jsonify({
            "success": True,
            "data": response.to_dict()
        })
    except exceptions.ClientRequestException as e:
        print(f"华为云API错误: {e.error_msg}")
        return jsonify({
            "success": False,
            "error": {
                "status_code": e.status_code,
                "request_id": e.request_id,
                "error_code": e.error_code,
                "error_msg": e.error_msg
            }
        }), 400
    except Exception as e:
        print(f"浇水错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    try:
        # 检查是否有文件
        if 'photo' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有找到图片文件'
            }), 400

        file = request.files['photo']

        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400

        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '不支持的文件类型'
            }), 400

        # 保存文件
        filename = 'flower.jpg'  # 固定文件名
        file_path = os.path.join(app.static_folder, filename)
        file.save(file_path)

        return jsonify({
            'success': True,
            'message': '图片上传成功',
            'path': f'/static/{filename}'
        })

    except Exception as e:
        print(f"上传图片错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/upload-to-coze', methods=['POST'])
def upload_to_coze():
    try:
        # 检查是否有文件
        if 'photo' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有找到图片文件'
            }), 400

        file = request.files['photo']

        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400

        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '不支持的文件类型'
            }), 400

        # 准备发送到 Coze API 的文件
        files = {
            'file': (file.filename, file.stream, file.content_type)
        }

        # 发送请求到 Coze API
        response = requests.post(
            'https://your-coze-api-endpoint/upload',  # 请替换为实际的 Coze API 端点
            files=files
        )

        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return jsonify({
                    'success': True,
                    'file_id': result['data']['id'],
                    'message': '文件上传成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f"Coze API 错误: {result.get('msg', '未知错误')}"
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f"API 请求失败，状态码: {response.status_code}"
            }), response.status_code

    except Exception as e:
        print(f"上传到 Coze 时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chat-with-coze', methods=['POST'])
def chat_with_coze():
    try:
        # 获取请求参数
        data = request.json
        file_id = data.get('file_id')  # 图片文件ID
        conversation_id = data.get('conversation_id')  # 可选的会话ID

        # 构建消息内容
        message_content = []
        if file_id:
            # 如果有图片，添加图片信息
            message_content.append({
                "type": "image",
                "file_id": file_id
            })

        # 构建请求头
        headers = {
            "Authorization": f"Bearer {COZE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # 构建请求体
        payload = {
            "messages": [{
                "role": "user",
                "content": json.dumps(message_content),
                "content_type": "object_string"
            }]
        }

        # 如果有会话ID，添加到请求参数中
        params = {}
        if conversation_id:
            params['conversation_id'] = conversation_id

        # 发送请求到 Coze API
        response = requests.post(
            COZE_API_ENDPOINT,
            headers=headers,
            params=params,
            json=payload
        )

        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return jsonify({
                    'success': True,
                    'data': result.get('data'),
                    'message': '对话成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f"Coze API 错误: {result.get('msg', '未知错误')}"
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f"API 请求失败，状态码: {response.status_code}"
            }), response.status_code

    except Exception as e:
        print(f"与 Coze 对话时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/check-chat-status', methods=['GET'])
def check_chat_status():
    try:
        # 从查询参数中获取必要的ID
        conversation_id = request.args.get('conversation_id')
        chat_id = request.args.get('chat_id')

        # 验证必要参数
        if not conversation_id or not chat_id:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：conversation_id 或 chat_id'
            }), 400

        # 构建请求头
        headers = {
            "Authorization": f"Bearer {COZE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # 构建查询参数
        params = {
            'conversation_id': conversation_id,
            'chat_id': chat_id
        }

        # 发送请求到 Coze API
        response = requests.get(
            'https://api.coze.cn/v3/chat/retrieve',
            headers=headers,
            params=params
        )

        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                chat_data = result.get('data', {})
                return jsonify({
                    'success': True,
                    'data': {
                        'status': chat_data.get('status'),
                        'conversation_id': chat_data.get('conversation_id'),
                        'chat_id': chat_data.get('id'),
                        'bot_id': chat_data.get('bot_id')
                    },
                    'is_completed': chat_data.get('status') == 'completed'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f"Coze API 错误: {result.get('msg', '未知错误')}"
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f"API 请求失败，状态码: {response.status_code}"
            }), response.status_code

    except Exception as e:
        print(f"检查对话状态时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/get-chat-messages', methods=['GET'])
def get_chat_messages():
    try:
        # 从查询参数中获取必要的ID
        conversation_id = request.args.get('conversation_id')
        chat_id = request.args.get('chat_id')

        # 验证必要参数
        if not conversation_id or not chat_id:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：conversation_id 或 chat_id'
            }), 400

        # 构建请求头
        headers = {
            "Authorization": f"Bearer {COZE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # 构建查询参数
        params = {
            'conversation_id': conversation_id,
            'chat_id': chat_id
        }

        # 发送请求到 Coze API
        response = requests.get(
            'https://api.coze.cn/v3/chat/message/list',
            headers=headers,
            params=params
        )

        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                messages = result.get('data', [])

                # 处理消息列表，添加更多有用的信息
                processed_messages = []
                for msg in messages:
                    processed_msg = {
                        'id': msg.get('id'),
                        'role': msg.get('role'),
                        'content': msg.get('content'),
                        'content_type': msg.get('content_type'),
                        'type': msg.get('type'),
                        'created_at': msg.get('created_at'),
                        'is_assistant': msg.get('role') == 'assistant',
                        'is_answer': msg.get('type') == 'answer'
                    }

                    # 如果是多模态内容，尝试解析
                    if msg.get('content_type') == 'object_string':
                        try:
                            processed_msg['parsed_content'] = json.loads(msg.get('content', '[]'))
                        except json.JSONDecodeError:
                            processed_msg['parsed_content'] = None

                    processed_messages.append(processed_msg)

                return jsonify({
                    'success': True,
                    'data': {
                        'messages': processed_messages,
                        'total_count': len(processed_messages),
                        'has_assistant_reply': any(m.get('role') == 'assistant' for m in messages)
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f"Coze API 错误: {result.get('msg', '未知错误')}"
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': f"API 请求失败，状态码: {response.status_code}"
            }), response.status_code

    except Exception as e:
        print(f"获取对话消息时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # 将 host 设置为 '0.0.0.0' 使其监听所有网络接口
    # 注意：这样局域网内的其他设备就可以通过你的 IP 地址访问了
    app.run(host='0.0.0.0', port=5000, debug=True)
