from Sensor import WaterPump
from Camera import Camera


class Command:
    """
    一个指令类，用于定义指令。
    """

    @staticmethod
    def create_pump_command(sensor: WaterPump):
        """创建一个已绑定sensor的pump命令"""
        def pump_command(paras: dict):
            duration = paras.get("duration")
            print("pump", duration)
            sensor.pump(t=duration)
        return pump_command

    @staticmethod
    def create_camera_command(camera: Camera):
        """创建一个已绑定camera的camera命令"""
        def camera_command(paras: dict):
            file_name = camera.camera()
            return file_name
        return camera_command

    @staticmethod
    def create_led_command(led):
        """创建一个已绑定led的led命令"""
        def led_command(paras: dict):
            if led.value == 1:
                led.off()
            else:
                led.on()
        return led_command