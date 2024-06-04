from deepface import DeepFace
import cv2
from ultralytics import YOLO

def detect_someone():
    try:
        recognition = DeepFace.find(img_path="frames/face.jpg", db_path="db", enforce_detection=False, silent=True)
        if recognition[0].empty:
            return None
        else:
            print("Лицо обнаружено:")
            print(recognition)
            return recognition
    except Exception as e:
        print(f"Произошла ошибка при выполнении поиска: {e}")
        return None

def process_video_with_tracking(model, input_video_path):
    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        raise Exception("Error: Could not open video file.")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    faces_count = 0
    frame_count = 0  # Переменная для отслеживания количества кадров

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % 25 == 0:
            results = model.track(frame, iou=0.4, conf=0.5, persist=True, imgsz=608, verbose=False)

            if results[0].boxes.id is not None:  # Проверка наличия треков
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                ids = results[0].boxes.id.cpu().numpy().astype(int)
                class_ids = results[0].boxes.cls.cpu().numpy().astype(int)

                for box, id, cls in zip(boxes, ids, class_ids):
                    color = (0, 0, 255)
                    text = "head"

                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
                    cv2.putText(
                        frame,
                        f"{text}",
                        (box[0], box[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

                    # Обрезка кадра по рамке
                    faces_count+=1
                    cropped_frame = frame[box[1]:box[3], box[0]:box[2]]
                    cv2.imwrite(f"frames/face.jpg", cropped_frame)
                    detect_someone()

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    # Close all OpenCV windows
    cv2.destroyAllWindows()

# Example usage:
model = YOLO('model.pt')
model.fuse()
process_video_with_tracking(model, "test2.mp4")