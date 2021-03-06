from flask import Flask, render_template, Response
import cv2
import torch
import numpy as np
import matplotlib

try:
    from PIL import Image, ImageDraw
except ImportError:
    import Image

# for internal storing of the object classes
import sys
import io

app = Flask(__name__)

# webcam camera
# camera = cv2.VideoCapture(0)
camera = cv2.VideoCapture("rtsp://admin:admin@172.24.28.36/11")

# pretrained small yolo model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# how many frames to wait before classifying objects
yolo_refresh_rate = 10

# output raw camera feed to frontend
def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        

        if not success:
            break
        
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # print("g", type(frame))
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


# Return first 10 plt colors as (r,g,b) https://stackoverflow.com/questions/51350872/python-from-color-name-to-rgb
def color_list():
    def hex2rgb(h):
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))

    return [hex2rgb(h) for h in matplotlib.colors.TABLEAU_COLORS.values()]  # or BASE_ (8), CSS4_ (148), XKCD_ (949)

# outputs a PIL image with the bounding boxes for images outputted
def yolo_draw_boxes(model):
    colors = color_list()
    for i, (img, pred) in enumerate(zip(model.imgs, model.pred)):
        str = f'image {i + 1}/{len(model.pred)}: {img.shape[0]}x{img.shape[1]} '
        if pred is not None:
            for c in pred[:, -1].unique():
                n = (pred[:, -1] == c).sum()  # detections per class
                str += f"{n} {model.names[int(c)]}{'s' * (n > 1)}, "  # add to string
            img = Image.fromarray(img.astype(np.uint8)) if isinstance(img, np.ndarray) else img  # from np
            for *box, conf, cls in pred:  # xyxy, confidence, class
                # str += '%s %.2f, ' % (names[int(cls)], conf)  # label
                ImageDraw.Draw(img).rectangle(box, width=4, outline=colors[int(cls) % 10])  # plot
        return img

# outputs the bounding boxes for the live images
def yolo_frames():
    counter = 0
    object_classes = ""

    while True:
        success, frame = camera.read()  # read the camera frame

        if not success:
            break
        
        elif counter % yolo_refresh_rate == 0:
            counter = 0
    
            # save image for classification 
            yolo_image = frame
    
            # classify image
            results = model([yolo_image])

            # used to store the output of which objects are seen
            # this will be fed to the the backend
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            results.print()
            object_classes = new_stdout.getvalue()
            sys.stdout = old_stdout
            print("Output from YOLO:", object_classes)

            # get PIL image with bounding boxes drawn
            yolo_output = yolo_draw_boxes(results)

            # stores PIL image as buffer to be passed to front end
            buf = io.BytesIO()
            yolo_output.save(buf, format='JPEG')
            byte_im = buf.getvalue()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + byte_im + b'\r\n')  # concat frame one by one and show result
            # yield (results.print())  # concat frame one by one and show result
        
        counter += 1

# set html as the template
@app.route('/')
def index():
    return render_template('index.html')

# show live video feed
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# show bounding boxes drawn on live feed
@app.route('/object_classifier')
def object_classifier():
    return Response(yolo_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)

