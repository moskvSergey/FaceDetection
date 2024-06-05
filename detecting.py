from deepface import DeepFace
import cv2
from ultralytics import YOLO

model = YOLO('model.pt')
model.fuse()


def detect_someone():
    try:
        recognition = DeepFace.find(img_path="frames/face.jpg", db_path="db", enforce_detection=False, silent=True)
        if recognition[0].empty:
            return None
        else:
            print("Лицо обнаружено:")
            print(recognition[0]['identity'])
            return recognition
    except Exception as e:
        print(f"Произошла ошибка при выполнении поиска: {e}")
        return None

def detect_head(frame):
    results = model.track(frame, iou=0.4, conf=0.5, persist=True, imgsz=608, verbose=False)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        ids = results[0].boxes.id.cpu().numpy().astype(int)
        class_ids = results[0].boxes.cls.cpu().numpy().astype(int)

        for box, id, cls in zip(boxes, ids, class_ids):
            cropped_frame = frame[box[1]:box[3], box[0]:box[2]]
            cv2.imwrite(f"frames/face.jpg", cropped_frame)
            detect_someone()


def cut_video(input_video_path):
    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        raise Exception("Error: Could not open video file.")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % 25 == 0:
            detect_head(frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            detect_head(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')