import os
import glob
import shutil
import datetime
import time
import sys

import ConfigParser
config = ConfigParser.ConfigParser()
config.read('IBM_SI_LOG_HOUSEKEEPING.conf')

#### USER INPUT  ######################################
BASE_DIR = config.get('CONF_VARIABLES','BASE_DIR')
#######################################################


FILE_TYPES_TO_ARCIVE = config.get('CONF_VARIABLES','FILE_TYPES_TO_ARCIVE')
FOLDERS_NOT_TO_ARCHIVE= config.get('CONF_VARIABLES','FOLDERS_NOT_TO_ARCHIVE')
NUM_RETENTION_DAYS= config.get('CONF_VARIABLES','NUM_RETENTION_DAYS')
LOGS_BACKUP_FOLDER=config.get('CONF_VARIABLES','LOGS_BACKUP_FOLDER')
ARCHIVE_BASE_FOLDER=config.get('CONF_VARIABLES','ARCHIVE_BASE_FOLDER')
########## DO NOT TAMPER CODE BELOW THIS LINE #########

os.chdir( BASE_DIR)


TIMESTAMP=datetime.datetime.now().strftime("%d%m%y_%H%M%S")       
CUR_TIME = time.time()                                            
DATE = datetime.datetime.now().strftime("%y%m%d")#DATE=$(date '+%Y%m%d')
TIME = datetime.datetime.now().strftime("%H%M%S")#TIME=$(date '+%H%M%S')

si_log_dir="logs"
si_archive_dir=ARCHIVE_BASE_FOLDER + "/ISBI_logs_%s/SI_logs_%s"%(TIMESTAMP,TIMESTAMP)


si_logs_backup_dir =""
os.makedirs(si_archive_dir)
#Housekeep noapp.log

no_app_log = os.path.join(si_log_dir, "noapp.log")             ###os.path.join is useful to join two paths firstpatrh with /second name
no_app_log_bkup = no_app_log + ".systemD%s.T%s"%(DATE,TIME)     ###os.path.basename = current working Directory
if( os.path.exists(no_app_log)):                                 ###os.path.isdir(path)  returns true if it is directory  isfile(path) if it is file
        content = open(no_app_log).read()
        #print "no_app_log found ..... %s "%no_app_log_bkup
        fpt = open(  no_app_log_bkup, 'w')
        fpt.write(content)
        fpt.close()
        if( os.path.exists(no_app_log_bkup) ):
                fpt = open(  no_app_log, 'w')
                fpt.write("Copy is successful")
                fpt.close()
                #print "cleared noapp.log"
        else:
                print "Copy is NOT successful"
                #sys.exit(1)  ## Need to check if this is necessary

#Compress the files older than NUM_RETENTION_DAYS days under /si_install/logs directory and move to folder 'archive_logs'
##Added changes to consider external purge log files for moving to archive folder
##starts

all_files = []
# r=root, d=directories, f = files
path=os.path.join(BASE_DIR,"logs")
#print path
for r, dirs, f in os.walk(path):
    dirs[:] = [d for d in dirs if d not in FOLDERS_NOT_TO_ARCHIVE]
    for file in f:
            all_files.append(os.path.join(r, file))
                    

#print all_files
for f in all_files :
        if os.stat(f).st_mtime < CUR_TIME - float(NUM_RETENTION_DAYS) * 86400:             ######  stat(filename).st_mtime= timestamp
               # print "candidate %s"%f
                os.system( "gzip %s"%f)
                #print "candidate zipped %s"%f
                if( os.path.exists(f+".gz") ):
                       #print "Moving gz %s"%(f+".gz")
                        shutil.move( f+".gz", os.path.join(si_archive_dir,os.path.basename(f)) )         ###shutil.move(file,whereTOmove)
                                                                                                               ##logs/archive_logs/ISBI_logs_%s/SI_logs_%s"%(TIMESTAMP,TIMESTAMP)   /filename/filename.gz

																	   ### BACKUP #############################################################
if not os.path.exists(LOGS_BACKUP_FOLDER):
  os.makedirs(LOGS_BACKUP_FOLDER)

archived_dirs = [ os.path.join(ARCHIVE_BASE_FOLDER,d) for d in os.listdir(ARCHIVE_BASE_FOLDER)]
print ("***************************************************************************************************************************************************************")
#print (archived_dirs)
for dir in archived_dirs:
        print ("dirs in archived_dirs"+dir)
	if( os.path.isdir(dir) and os.stat(dir).st_mtime < CUR_TIME - float(NUM_RETENTION_DAYS) * 86400):
		shutil.move( dir, os.path.join(LOGS_BACKUP_FOLDER,os.path.basename(dir) )  )

#####################deleting last 7 days#############################################

### CLEAN UP Backup Directory ########################################################
bkup_dirs = [ os.path.join(LOGS_BACKUP_FOLDER,d) for d in os.listdir(LOGS_BACKUP_FOLDER)]
for dir in bkup_dirs:
	if( os.path.isdir(dir) and os.stat(dir).st_mtime < CUR_TIME - NUM_RETENTION_DAYS * 86400 ) :
		shutil.rmtree( dir )

