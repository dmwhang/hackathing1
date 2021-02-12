# Dylan Whang - Hackathing 1 
## Flask app for real time object classification using YOLOv5

I have developed a flask app that allows users to live stream webcam or security camera footage on to a web application. This web app also classify objects found by the YOLOv5 model and shows the images with bounding boxes drawn around found images.

## Requirements

Python 3.8 or later with all [requirements.txt](https://github.com/ultralytics/yolov5/blob/master/requirements.txt) dependencies installed, including `torch>=1.7`. To install run:
```bash
$ pip install -r requirements.txt
```

## Deploy

To run:

```
python3 -m flask run
```

Then navigate to `http://127.0.0.1:5000/` to view the application.

Note, in order to use a webcam instead of the security camera that is set up, uncomment line 19 and comment out line 20

```
19 # camera = cv2.VideoCapture(0)
20 camera = cv2.VideoCapture("rtsp://admin:admin@172.24.28.36/11")
```

## Example output

terminal will output the object classifications as identified by the YOLO model: 

```
Output from YOLO: image 1/1: 1080x1920 4 cars, 3 trucks
```

Below is an example of what the webpage will look like:

![example](/images/example.png)

## Credit

Guide for deploying a live stream application with flask can be found here: https://github.com/NakulLakhotia/Live-Streaming-using-OpenCV-Flask.

Tutorial for deploying a YOLO model can be found here: https://github.com/ultralytics/yolov5/issues/36
