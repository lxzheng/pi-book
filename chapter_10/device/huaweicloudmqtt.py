from iot_device_sdk_python.client.connect_auth_info import ConnectAuthInfo
from iot_device_sdk_python.client.client_conf import ClientConf
from iot_device_sdk_python.client.request.command_response import CommandRsp
from iot_device_sdk_python.iot_device import IotDevice
from iot_device_sdk_python.client.listener.command_listener import CommandListener
from iot_device_sdk_python.transport.connect_listener import ConnectListener
from iot_device_sdk_python.client.request.service_property import ServiceProperty
from gpiozero import GPIODevice
from FileUpload import FileUpload


# 自定义华为云MQTT
class PiMqttApi:
    def __init__(
        self,
        server_uri = "*********.st1.iotda-device.cn-north-4.myhuaweicloud.com",
        port = 8883,
        device_id = "67667*****f1872637c94378_test",
        secret = "***************",
        iot_ca_cert_path = "./root.pem", # ./huaweicloud-iot-device-sdk-python/iot_device_demo/resources/root.pem
    ):
        # 连接参数
        self.server_uri = server_uri
        self.port = port
        self.device_id = device_id
        self.secret = secret
        self.iot_ca_cert_path = iot_ca_cert_path

        # 需要采集的传感器列表，可以通过register_sensor进行注册。
        self._sensors: dict[str, GPIODevice] = {}
        # 指令注册字典
        self._commands: dict[str, function] = {}

        self.file_upload = FileUpload()  # 初始化时创建一次

    def connect(self):
        '''连接设备至华为云平台'''
        # 配置连接参数
        self.connect_auth_info = ConnectAuthInfo()
        self.connect_auth_info.server_uri = self.server_uri
        self.connect_auth_info.port = self.port
        self.connect_auth_info.id = self.device_id
        self.connect_auth_info.secret = self.secret
        self.connect_auth_info.iot_cert_path = self.iot_ca_cert_path
        self.connect_auth_info.reconnect_on_failure = True
        self.client_conf = ClientConf(self.connect_auth_info)
        self.device = IotDevice(self.client_conf)
        self.client = self.device.get_client()

        # 设置命令监听器
        self.client.set_command_listener(CustomCommandListener(self.device, self))

        # 连接云平台
        if self.device.connect() != 0:
            print("connect failed")
            exit()

    def register_sensor(self, name, device):
        """注册需要获取状态的传感器"""
        self._sensors[name] = device

    def unregister_sensor(self, name):
        """取消注册需要获取状态的传感器"""
        return self._sensors.pop(name, None)

    @property
    def values(self):
        """获取所有注册传感器的状态，并生成一个状态字典"""
        states = {}
        for k, v in self._sensors.items():
            # 所有GPIODevice对象都具有value属性。
            states[k] = v.value
        return states

    def upload(self):
        """上传当前所有注册传感器的状态"""
        print("< ", self.values)
        self.client.report_properties(
            [
                ServiceProperty(
                    service_id="basic", properties=self.values
                ),
            ]
        )

    def register_command(self, name, function):
        """注册自定义指令"""
        self._commands[name] = function

    def unregister_command(self, name):
        """取消注册自定义指令"""
        return self._commands.pop(name, None)


# 自定义命令监听器
class CustomCommandListener(CommandListener):
    def __init__(self, iot_device: IotDevice, pi_mqtt_api):
        """ 传入一个IotDevice实例和PiMqttApi实例 """
        self.device = iot_device
        self.pi_mqtt_api = pi_mqtt_api

    def on_command(self, request_id, service_id, command_name, paras):
        print("on_command", request_id, service_id, command_name, paras)

        # 如果_commands字典中存在command_name，则执行相应的操作
        print('begin to handle command')
        commands = self.pi_mqtt_api._commands
        if command_name in commands:
            # 如果命令是camera，则需要特殊处理
            if command_name == "camera":
                file_name = commands[command_name](paras)
                print('file_name:', file_name)
                # 上传文件
                self.pi_mqtt_api.file_upload.upload(file_name)
            else:
                commands[command_name](paras)
        else:
            print(f"Command {command_name} not found")

        # 命令响应
        command_rsp = CommandRsp()
        command_rsp.result_code = 0
        command_rsp.response_name = command_name
        command_rsp.paras = {"result": True}
        self.device.get_client().respond_command(request_id, command_rsp)
