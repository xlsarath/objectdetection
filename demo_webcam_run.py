
import argparse
import time
import os
import smtplib
from datetime import datetime
import gluoncv as gcv
gcv.utils.check_version('0.4.0')
import mxnet as mx
import codecs
import json
import logging
import logging.config
from DBus_Module import ComponentRole, DBus, Var, VarType
from gluoncv.utils import try_import_cv2
cv2 = try_import_cv2()
import shutil
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import _pickle as cPickle


    
def get_index(subsController,col_name):
    return next((index for (index, d) in enumerate(subsController) if d.name == col_name), None)

def check_span(exec_stop):
    return ( exec_stop - datetime.now())

contlll =""
def prep_df_to_fat(subsController,subsOpen,subPvSim,subRmSim,header,vals,t_new):
    iterate = 1
    for sub in subsOpen:
                        header.append(sub.name)
                        vals.append(str(sub.value))
    for sub in subPvsim:
                        header.append(sub.name)
                        vals.append(str(sub.value))
    for sub in subRmSim:
                        header.append(sub.name)
                        vals.append(str(sub.value)) 
    for sub in subsController:
                        if(sub.name=="cv2.COLOR_BGR2RGB" or  sub.name=="unit8"):
                              header.append(sub.name)
                              vals.append(str(sub.value))
                             #Contl = ''.join([Contl,str(sub.value)])
                             #global contlll  
                             #contlll += str(sub.value)
                        if( iterate == len(subsController)):
                            #header.append("time_vals")
                            vals.append(str(t_new.strftime("%m/%d/%Y, %H:%M:%S")))
                            return header,vals  
                        iterate +=1
    return header,vals 

def prep_df_to_long(arr):
    return([datetime.utcnow(),arr.name,arr.value])


def get_filename(data_frame):
    if((len(data_frame.columns))>5):
        return output_csv_file_location_fat + 'Results_' + '_fat_'+case_str+'_'+str(it) + '.csv'
    else:
        return output_csv_file_location_long + 'Results_'+ '_long_'+case_str+'_'+str(it) + '.csv'       

"""def get_columnindex(df,col_val):
    return np.unique(np.flatnonzero((df==col_val).values)%df.shape[1])"""
   

def prep_df_to_file(arr_list):
     df = pd.DataFrame(arr_list)
     #print(df[148])
     logging.info("total records in the data-frame:"+str(df.shape))
     #print(df.loc[df.isin(["Month"]).any(axis=1)].index.tolist())
     #print(np.unique(np.flatnonzero((df=='Month').values)%df.shape[1]))
     df.to_csv(get_filename(df), index=True, index_label=False) 
     df = df.iloc[0:0]
     return True 

def log_folder_check(fpath):
    if(os.path.exists(fpath+"\\Logs")):
        return True
    else:
       os.mkdir(fpath+"\\Logs")
       return True     
    return True


def log_end_time_append():
    

    if(os.path.isfile(path+"\\info.log")):
        if(log_folder_check(log_location) == True):
            shutil.move(path+"\\info.log",log_location+"\\info_"+case_str+"_"+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+".log")
            #os.rename(path+"\\info.log", path+"\\info_"+case_str+"_"+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+".log")
    if(os.path.isfile(path+"\\warning.log")):
        if(log_folder_check(log_location) == True):
            shutil.move(path+"\\warning.log", log_location+"\\warning_"+case_str+"_"+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+".log")
            #os.rename(path+"\\warning.log", path+"warning_"+case_str+"_"+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+".log")
    if(os.path.isfile(path+"\\errors.log")):
        if(log_folder_check(log_location) == True):
            shutil.move(path+"\\errors.log", log_location+"\\errors_"+case_str+"_"+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+".log")
            #os.rename(path+"\\errors.log", path+"errors_"+case_str+"_"+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+".log")
    return True



parser = argparse.ArgumentParser(description="Webcam object detection script",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--num-frames', type=int, default=200)


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

with open(dbus_path) as json_file:
    json_data = json.load(json_file)
###Access all the variables in Sim Controller
#data_frame contents
#logging.warning('Creating Open Dss')
length = len(json_data['External Variables']['Component Name' == 'Controller']['Variables to subscribe'])


subsOpen = []
for p in json_data['Internal Variables']:
    #if (p['OpenDSS response type'] == 'monitor'):
    subsOpen.append(Var(str(p['Name']), VarType.FLOAT))

for x in range(length):
        if((json_data['External Variables'][x]['Component Name'])=='Frame'):
            subsController = []
            for p in json_data['External Variables'][x]['Variables to subscribe']:
                    subsController.append(Var(p['Name'], VarType.FLOAT))
            subsController.append(Var('layer', VarType.FLOAT)) 
            subsController.append(Var('step',VarType.FLOAT))
            subsController.append(Var('barc',VarType.FLOAT))
            subsController.append(Var('carc',VarType.FLOAT))
            subsController.append(Var('x_1',VarType.FLOAT))
            subsController.append(Var('y_1',VarType.FLOAT))    
        elif ((json_data['External Variables'][x]['Component Name'])=='corr'):
            subPvsim = []
            for p in json_data['External Variables'][x]['Variables to subscribe']:
                 subPvsim.append(Var(p['Name'], VarType.FLOAT))
        elif((json_data['External Variables'][x]['Component Name'])=='RM-SIM'):
            subRmSim = []
            for p in json_data['External Variables'][x]['Variables to subscribe']:
                subRmSim.append(Var(p['Name'], VarType.FLOAT))
   



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
while bol:
    #logging.info("remaining time for simulation:"+str(check_span(get_time())))
    #if(simStep%int(sim_sequence_diff)==0):
     #   logging.info("we're at simulation step:"+str(simStep))
    # State machine for stages in each simulation step.
    state = 'readLocalFlag'
    stopFlag = False 
    while not stopFlag:
        if state == 'readLocalFlag':
            logging.warning('Waiting for local flag to be false.') if Component.verbose else None
            Component.getLocalFlag()
            state = 'wait'  # Wait for reply to this message
        elif state == 'processValues':
            # Process if needed
            # Calculate P and Q for next step

            if(int(subsController[get_index(subsController,"TimeCtrl")].value) > 0):

                t_new = datetime(int(subsController[get_index(subsController,"Year")].value),int(subsController[get_index(subsController,"Month")].value),int(subsController[get_index(subsController,"Day")].value),int(subsController[get_index(subsController,"Hour")].value),int(subsController[get_index(subsController,"Minute")].value),int(subsController[get_index(subsController,"Second")].value))              
          
#                if (t_new!=t_old): 
                if(simStep%int(sim_sequence_diff)==0):
                        #logging.info("sub-controller simulation-step :"+str(subsController[0].value))
                        logging.info("sub-controller re-indexed img :"+str(t_new.strftime("%m/%d/%Y, %H:%M:%S")))
                prep_df_to_fat(subsController,subsOpen,subPvsim,subRmSim,header,vals,t_new)
                if(itr==0):
                    data_val_fat.append(['UTC_TIMESTAMP',*header,'Time_Stamp'])
                    header =[]
                    itr += 1
                data_val_fat.append([str(datetime.utcnow()),*vals])
                vals=[]
                contlll =""
                for sub in subsOpen:
                        data_val_long.append(prep_df_to_long(sub))
                for sub in subPvsim:
                        data_val_long.append(prep_df_to_long(sub))
                for sub in subRmSim:
                        data_val_long.append(prep_df_to_long(sub))                                                       
                for sub in subsController:
                        data_val_long.append(prep_df_to_long(sub))
                t_old = t_new
            logging.warning('Updating values for next simulation step.') if Component.verbose else None 
            myVars[0].value = simStep  
            Component.update(myVars)
            state = 'wait'  # Wait for reply to this message
        elif state == 'writeLocalFlag':
            logging.warning('Setting the local flag to true (ready for next step).') if Component.verbose else None
            Component.setLocalFlag(True)
            state = 'wait'  # Wait for reply to this message

        # Wait until next incoming package
        data = Component._getData()
        dataType = Component.getMsgType(data[4])
        dataPayload = data[5:]

        # Processing the incoming package
        if dataType == 'readLocalFlag':
            if dataPayload == b'\x00':
                state = 'processValues'
            else:
                Component.getLocalFlag()
        elif dataType == 'updateValues':
            if dataPayload == 0x11:
                Component.update(myVars)
            else:
               # logging.info('Dbus returns : '+str(dataPayload.decode('ascii'))+';')
                #logging.info('Dbus returns : '+str(dataPayload)+';')
                state = 'writeLocalFlag'
        elif dataType == 'writeLocalFlag':
            if dataPayload == 0x11:
                logging.error('error message.', exc_info=True)
                Component.setLocalFlag(True)
            else:
                #logging.info('Dbus returns'+str(dataPayload)+';')
                stopFlag = True
      
            else:
                offs = 0
                for comp in Component.subscribed:
                    for v in comp[1]:
                        offs = v.read_from(dataPayload, offs) 
        else:
            logging.error('---------- Unexpected message was received ----------')
            logging.info('Message: '+str(data)+'- Received data type: '+str(dataType))
        time.sleep(0.05)  # Delay between iterations




    if ((simStep % int(sim_step) == 0 and simStep > 0 )or check_span(exec_stop)<=timedelta(hours=00,minutes=00,seconds=1) ): #line check for saving and prelim check for sim duration
        it += 1 
        b4_saving = datetime.now()
        if(prep_df_to_file(data_val_fat)==True):
            itr=0  
            header=[]
        else:
        if(prep_df_to_file(data_val_long)==True):
        else:
        aftr_saving = datetime.now() - b4_saving
        tot_time = aftr_saving.total_seconds()
        
        #logging.info('Time after saving data' + str(datetime.now()))  # include time taken to save csv
        if(check_span(exec_stop)<=timedelta(hours=00,minutes=00,seconds=1)):
            bol = False
 
        data_val_fat = []
        data_val_long = []
        itr=0 

    simStep += 1


logging.info('End of Simulation.')
# Close the connection with DBus
Component.close()
logging.info("connection closed successfully")
logging.shutdown()
log_end_time_append()
