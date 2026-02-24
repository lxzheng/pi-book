import huaweicloudmqtt
import Sensor
from Command import Command
import time, threading, signal
from Camera import Camera

def upload_task():
    """每隔五秒上传传感器状态"""
    while True:
        api.upload()
        time.sleep(1)

# 连接华为云平台
api = huaweicloudmqtt.PiMqttApi()
api.connect()
# 新建硬件对象
soil_sensor = Sensor.SoilHumiditySensor(pin=18)
pump_sensor = Sensor.WaterPump(pin=17)
camera = Camera()
led = Sensor.Led(pin=27)
# 注册硬件对象，方便获取各个硬件的状态。
api.register_sensor("soil", soil_sensor)
api.register_sensor("pump", pump_sensor)
# 注册硬件的控制指令
api.register_command("pump", Command.create_pump_command(pump_sensor))
api.register_command("camera", Command.create_camera_command(camera))
api.register_command("led", Command.create_led_command(led))
# 启动上传任务
threading.Thread(target=upload_task, daemon=True).start()

# 等待所有事件完成调用（不会自动退出）
signal.pause()
