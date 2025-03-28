import cv2
import urllib.request
import numpy as np
from ultralytics import YOLO

url = 'http://192.168.3.120/cam-hi.jpg'
width, height = 800, 600

cap = cv2.VideoCapture(0)
model = YOLO('./Output/yolo_model.pt')

yaw_start_angle = 90
pitch_start_angle = 145

def frame_to_degrees(x, y, frame_width, frame_height, fov_x=48, fov_y=36):    
    # Normalize x and y to be in range [-1, 1]
    norm_x = (2 * x / frame_width) - 1
    norm_y = (2 * y / frame_height) - 1
    
    # Convert normalized coordinates to angles
    yaw_angle = norm_x * (fov_x / 2)
    pitch_angle = -norm_y * (fov_y / 2)
    
    return yaw_angle, pitch_angle

while True:    
    # img_resp = urllib.request.urlopen(url)
    # imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    # frame = cv2.imdecode(imgnp, -1)

    ret,frame = cap.read()

    results = model(frame, stream=True, verbose=False)

    for result in results:
        boxes = result.boxes

        for box in boxes:
            confidence = box.conf[0].item()  # Ensure it's a number
            if confidence > 0.52:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box corners
                x_center, y_center, w, h = map(int, box.xywh[0])  # Centered bounding box

                # Shift the center to make (0,0) the middle of the frame
                x_shifted = x_center - width // 2
                y_shifted = (height // 2) - y_center  # Inverting Y-axis

                
                yaw, pitch = frame_to_degrees(x_shifted, y_shifted, width, height)
                print(f"YAW: {yaw + yaw_start_angle}\nPITCH: {pitch + pitch_start_angle}")

                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.circle(frame, (x_center, y_center), 3, (0, 0, 255), -1)

                # Display confidence and coordinates
                cv2.putText(frame, f"Conf: {confidence*100:.2f}%", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f"Coords: x: {x_shifted}, y: {y_shifted}", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Camera Frame", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
