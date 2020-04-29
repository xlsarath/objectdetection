
import argparse
import time
import os
import smtplib
from datetime import datetime
import gluoncv as gcv
gcv.utils.check_version('0.4.0')
from gluoncv.utils import try_import_cv2
cv2 = try_import_cv2()
import mxnet as mx

parser = argparse.ArgumentParser(description="Webcam object detection script",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--num-frames', type=int, default=200,
                    help='number of frames to run the demo for. -1 means infinite')


args = parser.parse_args()

# Load the model
net = gcv.model_zoo.get_model('ssd_512_mobilenet1.0_voc', pretrained=True)

process_kill = open("C:\\Users\psma018\\Desktop\\FaceRec-master\\ObjDetect.bat", "w+")
process_kill.write("taskkill /F /PID "+str(os.getpid()))
process_kill.close()

# Load the webcam handler
cap = cv2.VideoCapture(0)
time.sleep(1)  ### letting the camera autofocus
count = 0
NUM_FRAMES = args.num_frames
i = 0
while i < NUM_FRAMES or NUM_FRAMES == -1:
    i += 1

    # Load frame from the camera
    ret, frame = cap.read()

    # Image pre-processing
    frame = mx.nd.array(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).astype('uint8')
    rgb_nd, scaled_frame = gcv.data.transforms.presets.ssd.transform_test(frame, short=512, max_size=700)

    # Run frame through network
    class_IDs, scores, bounding_boxes = net(rgb_nd)
    
   # print(bounding_boxes)
    #print(class_IDs)
    # Display the result
    scale = 1.0 * frame.shape[0] / scaled_frame.shape[0]
    img = gcv.utils.viz.cv_plot_bbox(frame.asnumpy(), bounding_boxes[0], scores[0], class_IDs[0], class_names=net.classes, scale=scale)
    if(scores[0][96]!=-1 and count <1):
        gmail_user = 'gmail@gmail.com'
        gmail_password = 'enter_pwd'

        sent_from = gmail_user
        to = ['example@gmail.com', 'example@sjsu.edu']
        subject = 'Alert from home monitoring app!!'
        body = 'Hi There, \n Your package is detected at the doorStep @'+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'\n login into app to find realtime feed'
        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, body)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        log_file = open("C:\\Users\psma018\\Desktop\\FaceRec-master\\history295b.txt", "a+")
        log_file.write("Package received @"+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        log_file.close()

        print('Email sent!')
        count += 1
    gcv.utils.viz.cv_plot_image(img)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
