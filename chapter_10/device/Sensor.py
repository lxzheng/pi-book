from gpiozero import LineSensor, DigitalOutputDevice, PolledInternalDevice, led
import gpiozero
import time


# class SoilHumiditySensor(LineSensor):
#     def __init__(self, pin: int, max_value: int = 1, min_value: int = 0):
#         # 对应干燥时最大的ADC数值。
#         self.max_value = max_value
#         # 对应湿润时最小的ADC数值。
#         self.min_value = min_value
#         # 初始化引脚，设置采样频率为10Hz
#         super().__init__(pin=pin, sample_rate=10)

#     @property
#     def value(self):
#         current = super().value
#         # 将读取的ADC数值换算成湿度百分比。
#         return (self.max_value - current) / (self.max_value - self.min_value) * 100


class TimeoutTask(PolledInternalDevice):
    def __init__(self, timeout: float, event_delay=1.0, pin_factory=None):
        """
        timeout: second. 默认启动时间。
        """
        self._timeout = timeout
        self._start_time = time.time() - self._timeout - 1.0
        super().__init__(event_delay=event_delay, pin_factory=pin_factory)
        # False 为默认状态。当默认状态为False时，状态改变为True时，触发when_activated。
        self._fire_events(self.pin_factory.ticks(), False)

    def start(self, timeout=None):
        """
        更新开始时间，从而实现重新触发。
        """
        self._start_time = time.time()
        if timeout is not None:
            self._timeout = timeout
        # 当状态可能发生变化的时候调用
        self._fire_events(self.pin_factory.ticks(), True)

    @property
    def value(self):
        """
        根据时间判断当前事件的状态。
        """
        current = time.time()
        if current - self._start_time <= self._timeout:
            return 1
        else:
            return 0

    # 当value的数值为1时触发。
    when_activated = gpiozero.internal_devices.event()
    # 当value的数值为0时触发。
    when_deactivated = gpiozero.internal_devices.event()


class WaterPump(DigitalOutputDevice):
    def __init__(self, pin: int):
        # 初始化引脚
        super().__init__(pin=pin)
        self._timeout_task = TimeoutTask(timeout=3.0)
        # 定时控制水泵的通断，不会阻塞主线程。
        self._timeout_task.when_activated = self._start_pump
        self._timeout_task.when_deactivated = self._stop_pump

    def _start_pump(self):
        """
        启动浇水。
        """
        print("start pump water")  # 测试使用
        super().on()

    def _stop_pump(self):
        """
        关闭浇水。
        """
        print("stop pump water")  # 测试使用
        super().off()

    def pump(self, t=None):
        """
        开启水泵t秒。
        """
        if t is not None:
            # 改变默认的浇水时间。
            self._timeout_task.start(timeout=t)
        self._timeout_task.start()

    @property
    def value(self):
        current = super().value
        # 将读取到的GPIO状态转换为布尔值。
        return bool(current)

class SoilHumiditySensor:
    def __init__(self, pin: int):
        self.spi = spidev.SpiDev() # Created an object
        self.spi.open(0,0)

    def read(self):
        adc = self.spi.xfer2([1, (8+self.channel)<<4, 0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data

    @property
    def value(self):
        return self.read() / 1023.0 * 100

class Led(led):
    def __init__(self, pin: int):
        super().__init__(pin=pin)
    
    @property
    def value(self):
        return bool(super().value)


if __name__ == "__main__":
    import time

    t = TimeoutTask(1)

    t.when_activated = lambda: print("when_activated")
    t.when_deactivated = lambda: print("when_deactivated")

    t.start()

    time.sleep(3)
    t.close()