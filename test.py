import cv2
import numpy as np
from ultralytics import YOLO

# Initialize camera
cap = cv2.VideoCapture(0)
width, height = 800, 600  # Frame dimensions
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Load YOLO model
model = YOLO('./Output/yolo_model.pt')

# Servo initial positions (in degrees)
yaw_start_angle = 90    # Typically middle position for yaw (0-180 range)
pitch_start_angle = 145 # Your calibrated starting position

# Field of view (FOV) angles - you'll need to adjust these based on your camera
# These represent how many degrees the camera sees horizontally/vertically
FOV_X = 60  # degrees horizontal FOV
FOV_Y = 45  # degrees vertical FOV

def frame_to_servo_angles(x_pixel, y_pixel, frame_width, frame_height):
    """
    Convert pixel coordinates to servo angles.
    Args:
        x_pixel, y_pixel: Object center coordinates relative to image center (0,0)
        frame_width, frame_height: Frame dimensions
    Returns:
        yaw_angle, pitch_angle: Servo angles in degrees
    """
    # Calculate how many degrees per pixel
    degrees_per_pixel_x = FOV_X / frame_width
    degrees_per_pixel_y = FOV_Y / frame_height
    
    # Convert pixel offset to angle offset
    yaw_offset = x_pixel * degrees_per_pixel_x
    pitch_offset = y_pixel * degrees_per_pixel_y
    
    # Calculate absolute servo angles
    yaw_angle = yaw_start_angle + yaw_offset
    pitch_angle = pitch_start_angle + pitch_offset
    
    # Constrain angles to valid servo range (typically 0-180)
    yaw_angle = max(0, min(180, yaw_angle))
    pitch_angle = max(0, min(180, pitch_angle))
    
    return yaw_angle, pitch_angle

while True:    
    ret, frame = cap.read()
    if not ret:
        break
    
    # Resize frame if needed
    frame = cv2.resize(frame, (width, height))
    
    # Object detection
    results = model(frame, stream=True, verbose=False)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            confidence = box.conf[0].item()
            if confidence > 0.52:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x_center, y_center = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Shift coordinates to make (0,0) the center
                x_shifted = x_center - width // 2
                y_shifted = (height // 2) - y_center  # Negative because in images, Y increases downward
                
                # Calculate servo angles
                yaw, pitch = frame_to_servo_angles(x_shifted, y_shifted, width, height)
                print(f"Target Angles - YAW: {yaw:.1f}°, PITCH: {pitch:.1f}°")
                
                # Here you would send these angles to your servos
                # servo_yaw.write(yaw)
                # servo_pitch.write(pitch)
                
                # Visualization
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (x_center, y_center), 5, (0, 0, 255), -1)
                cv2.putText(frame, f"YAW: {yaw:.1f}°", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"PITCH: {pitch:.1f}°", (x1, y1 - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show crosshair at center
    cv2.line(frame, (width//2, 0), (width//2, height), (255, 0, 0), 1)
    cv2.line(frame, (0, height//2), (width, height//2), (255, 0, 0), 1)
    
    cv2.imshow("Object Tracking", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()