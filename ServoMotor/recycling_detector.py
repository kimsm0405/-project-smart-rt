import torch
import cv2
import time

class RecyclingDetector:
    """main_controller와 연동되도록 수정된 YOLOv5 재활용 객체 탐지 클래스"""
    def __init__(self, conf_threshold=0.5, camera_id=0):
        self.conf_threshold = conf_threshold
        self.camera_id = camera_id
        
        # YOLOv5 모델 로드
        print("YOLOv5 모델을 로드하는 중...")
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
        self.model.conf = self.conf_threshold
        print("모델 로드 완료!")
        
        # 카메라 초기화
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise IOError(f"웹캠을 열 수 없습니다 (ID: {self.camera_id})")
        print("웹캠 탐지 시작. 'q'를 눌러 종료하세요.")

        # 색상 설정 (BGR)
        self.colors = {
            'plastic': (0, 255, 0), 'paper': (255, 0, 0), 'metal': (0, 0, 255),
            'glass': (255, 255, 0), 'organic': (0, 255, 255), 'other': (128, 128, 128)
        }

    def classify_recyclable(self, class_name):
        """객체를 재활용 카테고리로 분류"""
        plastic_items = ['bottle', 'cup', 'plastic bag']
        paper_items = ['book', 'newspaper']
        metal_items = ['fork', 'knife', 'spoon', 'can']
        glass_items = ['wine glass']
        organic_items = ['banana', 'apple', 'orange', 'broccoli', 'carrot']
        
        if class_name in plastic_items: return 'plastic'
        if class_name in paper_items: return 'paper'
        if class_name in metal_items: return 'metal'
        if class_name in glass_items: return 'glass'
        if class_name in organic_items: return 'organic'
        return 'other'

    def detect(self):
        """웹캠에서 프레임 하나를 읽고, 객체를 탐지하여 가장 유력한 객체의 분류명을 반환"""
        ret, frame = self.cap.read()
        if not ret:
            return None, None # 프레임 읽기 실패

        frame = cv2.resize(frame, (640, 480))
        
        # 추론 실행
        results = self.model(frame)
        detections = results.pandas().xyxy[0]
        
        detected_category = None

        # 가장 신뢰도 높은 객체 찾기
        if not detections.empty:
            best_detection = detections.loc[detections['confidence'].idxmax()]
            recycle_category = self.classify_recyclable(best_detection['name'])
            detected_category = recycle_category

        # 화면에 모든 탐지 결과 그리기
        for _, detection in detections.iterrows():
            x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            conf = detection['confidence']
            class_name = detection['name']
            
            recycle_category = self.classify_recyclable(class_name)
            color = self.colors.get(recycle_category, self.colors['other'])
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{class_name} ({recycle_category}): {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # 프레임 표시
        cv2.imshow('Recycling Detection', frame)
        
        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return 'quit', frame

        return detected_category, frame

    def cleanup(self):
        """리소스 정리"""
        print("카메라와 창을 닫습니다.")
        self.cap.release()
        cv2.destroyAllWindows()
