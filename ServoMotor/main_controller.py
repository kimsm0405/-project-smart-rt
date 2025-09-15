from Motor import MotorController
from recycling_detector import RecyclingDetector
import time

# --- 설정 ---
SERVO_PIN = 18
ANGLE_MAP = {
    "plastic": 45,
    "paper": 90,
    "metal": 135,
    "glass": 180,
    "organic": 225, # 유기농 항목 추가
    # 'other'는 처리하지 않음
}

def main():
    """메인 제어 로직"""
    detector = None
    motor = None
    try:
        # confidence threshold를 0.5로 설정하여 탐지기 객체 생성
        detector = RecyclingDetector(conf_threshold=0.5)
        motor = MotorController(SERVO_PIN)

        print("--- 재활용품 분류 시스템 시작 ---")

        while True:
            # 1. 재활용품 탐지 (탐지된 객체 이름과 영상 프레임을 받아옴)
            detected_item, frame = detector.detect()

            # 'q'가 눌렸거나 프레임이 없으면 종료
            if detected_item == 'quit' or frame is None:
                break

            # 2. 탐지된 종류에 따라 모터 제어
            if detected_item and detected_item in ANGLE_MAP:
                target_angle = ANGLE_MAP[detected_item]
                print(f"탐지: [{detected_item}], 목표 각도: {target_angle}")
                motor.set_angle(target_angle)

                # 5초 대기
                print("분류 완료. 5초 후 원위치로 복귀합니다.")
                time.sleep(5)

                # 원위치(0도)로 복귀
                print("원위치로 복귀 중...")
                motor.set_angle(0)
                
                # 원위치 복귀 후 다음 탐지를 위해 잠시 대기
                time.sleep(1)

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 프로그램 종료 시 항상 모든 리소스를 정리
        if motor:
            motor.cleanup()
        if detector:
            detector.cleanup()
        print("시스템이 종료되었습니다.")

if __name__ == "__main__":
    main()
