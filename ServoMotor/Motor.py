import RPi.GPIO as GPIO
import time

class MotorController:
    """
    RPi.GPIO를 사용하여 실제 서보 모터를 제어하는 클래스
    """
    def __init__(self, pin):
        self.pin = pin
        
        # GPIO 설정
        GPIO.setmode(GPIO.BCM)  # BCM 핀 번호 모드 사용
        GPIO.setup(self.pin, GPIO.OUT)
        
        # PWM 설정 (주파수: 50Hz)
        self.pwm = GPIO.PWM(self.pin, 50)
        self.pwm.start(0)  # 초기 듀티 사이클 0으로 시작
        print(f"MotorController 초기화 완료 (GPIO 핀: {self.pin}, 실제 모터 제어)")

    def set_angle(self, angle):
        """
        지정된 각도로 서보 모터를 이동시킵니다.
        서보 모터는 보통 0~180도의 각도를 가집니다.
        PWM 듀티 사이클은 보통 2(0도)에서 12(180도) 사이의 값을 가집니다.
        """
        # 각도를 듀티 사이클로 변환
        duty = angle / 18 + 2
        
        GPIO.output(self.pin, True)
        self.pwm.ChangeDutyCycle(duty)
        print(f"모터를 {angle}도로 이동합니다. (듀티: {duty:.2f})")
        
        # 모터가 해당 각도로 이동할 시간을 줍니다.
        time.sleep(1)
        
        # 이동 후 신호를 보내지 않아 모터가 떨리는 것을 방지합니다.
        GPIO.output(self.pin, False)
        self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        """
        GPIO 리소스를 정리합니다.
        """
        print("GPIO 리소스를 정리하고 모터를 정지합니다.")
        self.pwm.stop()
        GPIO.cleanup()
