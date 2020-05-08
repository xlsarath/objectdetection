import sys
import os,csv
import shutil
import time
from datetime import datetime, timedelta
import pandas as pd
from dateutil.parser import parser

class File_Copier:

    def __init__(self, input_dir, output_dir):
        self.input_dir = self.translate_path(input_dir)
        self.output_dir = self.translate_path(output_dir)
        if(os.path.isdir(self.input_dir) and os.path.isdir(self.output_dir)):
            self.directory_time=0
            self.files_dict={}
          
    @staticmethod
    def translate_path(path):
        """
        This will translate path from existing to path.replace("\\dir\\", "\\dir$\\")
        """
        try:
            if("\\e\\" in path):
                path = path.replace("\\e\\", "\\e$\\")
            elif ("\\c\\" in path):
                path = path.replace("\\c\\", "\\c$\\")
            print('Formatted path: {}'.format(path))
            return path
        except Exception as e:
             print('Unable to translate path: {} due to: {}'.format(path, e))
        
   

    @staticmethod
    def f_copy(input_f_p, output_f_p):
        try:
            shutil.copyfile(input_f_p, output_f_p)
            print('Successfully copied file: {} to: {}'.format(input_f_p, output_f_p))
            log_file.write(new_line+'Successfully copied file: {} to: {}'.format(input_f_p, output_f_p))
            #os.remove(input_f_p)
        except Exception as e:
            print('Unable to copy file: {} to: {} due to: {}'.format(input_f_p, output_f_p, e))
        

    @staticmethod
    def f_present(f, dir):
        try:
            return f in os.listdir(dir)
        except Exception as e:
            print('Unable to check file present: {} in directory: {} due to: {}'.format(f, dir, e))
        

    @staticmethod
    def f_not_lock(f_p):
        if os.path.exists(f_p):
            try:
                os.rename(f_p, f_p)
                #print('Access on file "' + f_p +'" is available!')
                return True
            except OSError as e:
                print('Access-error on file "' + f_p + '"! \n' + str(e))
        return False
    
    @staticmethod
    def f_lastModified(f_in, files_dict):
      try:
            return os.path.basename(f_in) in files_dict and files_dict[os.path.basename(f_in)] != os.path.getmtime(f_in)
      except Exception as e:
            print('Unable to get last modified of file: {} due to: {}'.format(f_in, e))
        
    @staticmethod
    def f_merge(f,input_f_p, output_f_p):
        try:
            with open(output_f_p+f, 'a+') as file_p:
                with open(input_f_p+f) as infile:
                    i = 0
                    for line in infile:
                        if i>0:#(Skip header)
                            file_p.write(line) 
                        i+=1
            infile.close   
            file_p.close()    
            print('Merged file: {} to: {}'.format(input_f_p+f, output_f_p+f))
            log_file.write(new_line+'Merged file: {} to: {}'.format(input_f_p+f, output_f_p+f))
        except Exception as e:
            print('Unable to merge file: {} to: {} due to: {}'.format(input_f_p, output_f_p, e))
    @staticmethod
    def f_delete(input_f_p):
        try:
            print("file {} successfully removed".format(input_f_p))
            os.remove(input_f_p)
        except Exception as e:
            print("Unable to delete file due to {}".format(e))


    def copy_check_file(self, f):
        try:
            if (os.path.isdir(self.input_dir) and os.path.isdir(self.output_dir))==True:
                if self.f_not_lock(self.input_dir+f) and not self.f_present(f, self.output_dir):
                    self.f_copy(self.input_dir+f, self.output_dir+f)
                    return True
                elif self.f_not_lock(self.input_dir+f) and self.f_present(f, self.output_dir) and self.f_lastModified(self.output_dir+f, self.files_dict):
                    self.f_merge(f, self.input_dir, self.output_dir)
                    return True
            if (os.path.isdir(self.input_dir) and os.path.isdir(self.output_dir))==False:
                    return False
        except Exception as e:
            print('Unable to copy file: {} to: {} due to: {}'.format(self.input_dir, self.output_dir, e))

    def get_logger(self):
        log_file.write("\nLog created at :" +datetime.today().strftime('%Y-%m-%d-%H-%M-%S'))
        log_file.write(new_line+" Files pickup location :"+self.input_dir)
        print(new_line+" Files pickup location :"+self.input_dir)
        log_file.write(new_line+"To location"+self.output_dir)
        print(new_line+"To location"+output_dir)
        log_file.write(new_line+"Logs will be avaialble at :"+os.path.dirname(os.path.dirname(self.input_dir))+"\\log.txt")
        print(new_line+"Logs will be avaialble at :"+os.path.dirname(os.path.dirname(self.input_dir))+"\\log.txt")
        log_file.write(new_line+"to terminate this process use --> " +os.getcwd()+"\\copier_kill.bat")
        print(new_line+"to terminate this process use --> " +os.getcwd()+"\\copier_kill.bat")


    def call_copy(self):
        try:
                while True:
                    last_time = os.path.getmtime(self.input_dir)
                    if self.directory_time is not last_time:                
                        for f in os.listdir(self.input_dir):
                            self.files_dict[f] = os.path.getmtime(self.input_dir+f)
                            if(self.copy_check_file(f)):
                                self.f_delete(self.input_dir+f)
                    self.directory_time = last_time
                    time.sleep(10)
        except Exception as e:
            print('Unable to execute call copy due to: {}'.format(e))


if __name__ == "__main__":
    # provide the location of paths to be moved!! (pls ensure \\ while specifying)
    output_dir = "C:\\Users\\psma018\\Pictures\\test\\".lower()
    input_dir = "C:\\Users\\psma018\\Results\\".lower()  # destination to save'em 
    process_kill = open("copier_kill.bat","w+")
    process_kill.write("taskkill /F /PID "+str(os.getpid()))
    process_kill.close()
    new_line = "\n"+datetime.today().strftime('%Y-%m-%d-%H-%M-%S')+" pid : "+str(os.getpid())+" "+os.getlogin()+"\t\t"
    log_file = open((os.path.dirname(os.path.dirname(input_dir)))+"\\log.txt", "a+")
    #get_logger()
    f_c = File_Copier(input_dir, output_dir)
    f_c.get_logger()
    f_c.call_copy()