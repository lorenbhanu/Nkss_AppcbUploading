import json
import FileProcess as appcbfileprocess
import time
import log
import threading
# Open the JSON file and load its contents
try:
    with open("/root/Nkss_AppcbUploading/config.json", "r") as file:
        config = json.load(file)

    # Read the values and store them in variables
    Stations = config["AppcbStations"]
    Channels = config["Channels"]
    realtimeUploadurl = config["ConfigSettings"]["realtimeUploadurl"]
    delayuploadurl = config["ConfigSettings"]["delayuploadurl"]
    rawdatapath=config["ConfigSettings"]["RawDataPath"]
    noofflies=config["ConfigSettings"]["nooffiles"]
    metafile=config["ConfigSettings"]["metafile"]
    datafilepath=config["ConfigSettings"]["datafile"]
    zipFilePath=config["ConfigSettings"]["zipfile"]
    ServiceIntervalInSec=config["BootUpSettings"]["Interval"]    
except Exception as ex:
    log.logger.error('error reading yaml file '+str(ex))

def appcbupload():
    try:
        log.logger.info("APPCBFileUploadService " + "started")
        log.logger.info("APPCBFileUploadService " + realtimeUploadurl + "" + delayuploadurl + "")
        appcbfileprocess.processindsinwebapi(Stations,rawdatapath,noofflies,Channels,metafile,datafilepath,zipFilePath,realtimeUploadurl,delayuploadurl)
        log.check_log_file_size()
        timer = threading.Timer(ServiceIntervalInSec, appcbupload)
        timer.start()
    except Exception as ex:
        log.logger.error(ex)
    

appcbupload()