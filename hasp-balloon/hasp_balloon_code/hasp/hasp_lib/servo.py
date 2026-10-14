from adafruit_servokit import ServoKit
import time

class ContinuousServo:
    def __init__(self):
        self.kit = ServoKit(channels=16)
        # self.kit.servo[0].set_pulse_width_range(500, 2500)
        self.kit.continuous_servo[1].set_pulse_width_range(750,2250)

    def start(self):
        print("Servo object created")

    def close(self):
        print("Servo object deleted")
        self.kit.continuous_servo[1].throttle=0

    def continuous_rotate(self,speed,t):
        # rotate a continuous servo at a throttle for fixed time
        if speed >=0:
            self.kit.continuous_servo[1].throttle=speed
            time.sleep(t)
            self.kit.continuous_servo[1].throttle=0
        else:
            self.kit.continuous_servo[1].throttle=speed*0.715
            time.sleep(t)
            self.kit.continuous_servo[1].throttle=0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

# while True:
#     kit.servo[0].angle = 0
#     time.sleep(4)
#     kit.servo[0].angle = 180
#     time.sleep(4)


if __name__ == "__main__":
    with ContinuousServo() as servo:
        servo.continuous_rotate(-0.5,5)
        print("Spinning servo")
