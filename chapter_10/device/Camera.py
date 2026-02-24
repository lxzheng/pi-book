import cv2
from datetime import datetime


class Camera:
    def camera(self):
        cap=cv2.VideoCapture(0)
        ret ,frame = cap.read()
        timestamp = datetime.now().isoformat()
        print('take a photo at ',timestamp)
        cv2.imwrite('%s.jpg' % timestamp,frame)
        # cv2.imwrite('flower.jpg',frame)
        return '%s.jpg' % timestamp
    
    def run(self):
        self.camera()

if __name__ == "__main__":
    camera = Camera()
    camera.run()