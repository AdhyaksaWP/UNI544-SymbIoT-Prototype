import cv2
import serial
import urllib.request
import numpy as np
from ultralytics import YOLO

class Fire_Inference():
    def __init__(self):
        self.__url = 'http://192.168.252.180/cam-hi.jpg'
        self.__width = 600
        self.__height = 800
        # self.__serial = serial.Serial('/dev/ttyUSB0', baudrate=115200)
        self.__model = YOLO('Output/yolo_model.pt')
        self.__yaw_start_angle = 90 
        self.__pitch_start_angle = 145

        self.frame = None
        self.running = True

    def camera(self):
        while self.running:
            try:
                img_resp = urllib.request.urlopen(self.__url)
                imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
                self.frame = cv2.imdecode(imgnp, -1)

                self.inference()  # Run inference every frame
                cv2.imshow("Camera Frame", self.frame)

                if cv2.waitKey(1) == ord('q'):
                    break
            except Exception as e:
                print(f"Camera error: {e}")

        cv2.destroyAllWindows()
    
    def inference(self):
        if self.frame is None:
            print("No frame available for inference")
            return None, None

        results = self.__model(self.frame, stream=True, verbose=False)
        for result in results:
            boxes = result.boxes

            for box in boxes:
                confidence = box.conf[0].item()
                if confidence > 0.52:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    x_center, y_center, w, h = map(int, box.xywh[0])

                    # Shift the center to make (0,0) the middle of the frame
                    x_shifted = x_center - self.__width // 2
                    y_shifted = y_center - (self.__height // 2)  # Inverting Y-axis

                    yaw, pitch = self.__frame_to_servo_angles(x_shifted, y_shifted, self.__width, self.__height)
                    print(f"Target Angles - YAW: {yaw:.1f}°, PITCH: {pitch:.1f}°")

                    # Draw rectangle
                    cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.circle(self.frame, (x_center, y_center), 3, (0, 0, 255), -1)

                    # Display confidence and coordinates
                    cv2.putText(self.frame, f"Conf: {confidence*100:.2f}%", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.putText(self.frame, f"Coords: x: {x_shifted}, y: {y_shifted}", (x1, y2 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                        
                    # Send yaw and pitch over serial
                    # self.__serial.write(f"{yaw:.1f},{pitch:.1f}\n".encode())

    def __frame_to_servo_angles(self, x_pixel, y_pixel, frame_width, frame_height, fov_x=60, fov_y=45):
        degrees_per_pixel_x = fov_x / frame_width
        degrees_per_pixel_y = fov_y / frame_height

        yaw_offset = x_pixel * degrees_per_pixel_x
        pitch_offset = y_pixel * degrees_per_pixel_y

        yaw_angle = self.__yaw_start_angle + yaw_offset
        pitch_angle = self.__pitch_start_angle + pitch_offset

        yaw_angle = max(0, min(180, yaw_angle))
        pitch_angle = max(0, min(180, pitch_angle))

        return yaw_angle, pitch_angle

detector = Fire_Inference()
detector.camera()
