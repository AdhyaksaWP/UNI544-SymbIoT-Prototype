import cv2
import serial
import time
import urllib.request
import numpy as np
from ultralytics import YOLO

class Fire_Inference():
    def __init__(self):
        self.__url = 'http://192.168.133.180/cam-hi.jpg'
        self.__width = 800
        self.__height = 600
        # self.__serial = serial.Serial('/dev/ttyUSB0', baudrate=115200)
        self.__model = YOLO('../AI/output/yolo_model.pt')
        self.__yaw_start_angle = 90 
        self.__pitch_start_angle = 150
        self.__cur_yaw = self.__yaw_start_angle
        self.__cur_pitch = self.__pitch_start_angle

        img = cv2.imread('../AI/vision_test/Large_bonfire.jpg')
        self.sample_image = cv2.resize(img, (100, 100))
        self.sample_image_height, self.sample_image_width, _ = self.sample_image.shape

        self.frame = None
        self.running = True
        self.start_time = time.time()

    def camera(self):
        while self.running:
            try:
                img_resp = urllib.request.urlopen(self.__url)
                imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
                self.frame = cv2.imdecode(imgnp, -1)

                self.time = (time.time() - self.start_time)

                # if (self.time >= 0 and self.time <= 4):
                #     self.test_images("Top_Left")
                # elif (self.time >= 5 and self.time <= 9):
                #     self.test_images("Top_Right")
                # elif (self.time >= 10 and self.time <= 14):
                #     self.test_images("Bot_Left")
                # elif (self.time >= 16 and self.time <= 19):
                #     self.test_images("Bot_Right")
                
                # if (self.time >=20):
                #     self.start_time = time.time()

                # self.inference()  # Run inference every frame

                cv2.line(self.frame, (self.__width//2, 0), (self.__width//2, self.__height), (0, 0, 255), 5)
                cv2.line(self.frame, (0, self.__height//2), (self.__width, self.__height//2), (0, 0, 255), 5)

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
                    x_shifted = x_center - (self.__width // 2)
                    y_shifted = y_center - (self.__height // 2)  # Adjust Y-axis properly

                    THRESHOLD_X = 50  # Pixels
                    THRESHOLD_Y = 50  # Pixels

                    # Adjust angles only if deviation exceeds the threshold
                    if abs(x_shifted) > THRESHOLD_X or abs(y_shifted) > THRESHOLD_Y:
                        yaw, pitch = self.__frame_to_servo_angles(x_shifted, y_shifted, self.__width, self.__height)
                        print(f"Target Angles - YAW: {yaw}°, PITCH: {pitch}°")

                        self.__cur_yaw = yaw
                        self.__cur_pitch = pitch

                        # self.__serial.write(f"{yaw:.1f},{pitch:.1f}\n".encode())
                    else:
                        print("Object is already centered, no adjustment needed")

                    return self.__cur_yaw, self.__cur_pitch
                
        print("No fire detected, returning last known angles")
        return self.__cur_yaw, self.__cur_pitch
        
    def __frame_to_servo_angles(self, x_pixel, y_pixel, frame_width, frame_height, fov_x=60, fov_y=45):
        degrees_per_pixel_x = fov_x / frame_width
        degrees_per_pixel_y = fov_y / frame_height

        yaw_offset = x_pixel * degrees_per_pixel_x
        pitch_offset = y_pixel * degrees_per_pixel_y

        yaw_angle = self.__yaw_start_angle + yaw_offset
        pitch_angle = self.__pitch_start_angle + pitch_offset

        yaw_angle = max(0, min(180, yaw_angle))
        pitch_angle = max(0, min(180, pitch_angle))

        return int(yaw_angle), int(pitch_angle)
    
    def test_images(self, term):
        match term:
            case "Top_Left":
                self.frame[100:100+self.sample_image_height, 100: 100+self.sample_image_width] = self.sample_image
            case "Top_Right":
                self.frame[100:100+self.sample_image_height, 600: 600+self.sample_image_width] = self.sample_image
            case "Bot_Left":
                self.frame[400:400+self.sample_image_height, 100: 100+self.sample_image_width] = self.sample_image
            case "Bot_Right":
                self.frame[400:400+self.sample_image_height, 600: 600+self.sample_image_width] = self.sample_image

# detector = Fire_Inference()
# detector.camera()
