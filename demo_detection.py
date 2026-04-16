import cv2
from ultralytics import YOLO

# Load model
model = YOLO('best.pt')

# Point this at any of your test images
IMAGE_PATH = 'abrams-1800x1200.jpg'

# Run detection
img = cv2.imread(IMAGE_PATH)
results = model(img, verbose=False)

# Draw boxes
for box in results[0].boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    confidence = float(box.conf[0])
    label = f'{class_name} {confidence:.2f}'
    
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.rectangle(img, (x1, y1 - 20), (x1 + len(label) * 8, y1), (0, 255, 0), -1)
    cv2.putText(img, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

# Display
cv2.imshow('TrueSight — Military Detection', img)
cv2.waitKey(0)
cv2.destroyAllWindows()