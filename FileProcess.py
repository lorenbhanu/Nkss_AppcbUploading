import os
import glob
from datetime import datetime
import Process as filesprocess
import AES as aesencryption
import zipfile
import upload
import Archiver as archiver
import log


def round_up(n):
    return (32 - n % 32) + n


def createappcbmetafile(file):
    try:
        with open(file, 'w') as f:
            metaData = "SITE_ID,SITE_UID,MONITORING_UNIT_ID,ANALYZER_ID,PARAMETER_ID,PARAMETER_NAME,READING,UNIT_ID,DATA_QUALITY_CODE,RAW_READING,UNIX_TIMESTAMP,CALIBRATION_FLAG,MAINTENANCE_FLAG"
            f.write(metaData)
            f.close()
    except Exception as ex:
        log.logger.error(ex)

def CreateZipFileWithMetaandDataFile(meta,datafile,zippath):
    iszipfilecreated=False    

    # Set the names of the files you want to zip
    files_to_zip = [meta,datafile]

    # Path to output zip file
    output_zip_file = zippath
    with zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files_to_zip:
            # Extract the file name from the full path
            file_name = os.path.basename(file)
            # Write the file to the zip archive with the same name as the original file
            zip_file.write(file, arcname=file_name)
        zip_file.close()
    iszipfilecreated=True
    return iszipfilecreated
    

def createappcbdatafilefromlist(list,appcbpath,currdate,monid,sitekey):
    datatobeencrypted=""
    isdatafilecreated=False
    completefilepath=""
    try:
        for appcbdata in list:
            sb=""
            sb+=str(appcbdata['SiteId']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['SiteUid']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['MonitoringUnitId']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['AnalyzerId']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['ParameterId']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['ParameterName']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['Reading']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['UnitId']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['DataQualityCode']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['RawReading']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['UnixTimestamp']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['CalibrationFlag']).strip('\n').strip('\r')
            sb+=','
            sb+=str(appcbdata['MaintainceFlag']).strip('\n').strip('\r')   
            filepath = os.path.dirname(appcbpath)
            fileName = os.path.splitext(os.path.basename(appcbpath))[0]
            fileextension = os.path.splitext(appcbpath)[1]   
            completefilepath = os.path.join(filepath, fileName+fileextension) 

            with open(completefilepath, 'a') as ff: 
                ff.write(sb)
                ff.close()
        with open(completefilepath, 'r') as ff: 
                datatobeencrypted=ff.readline().strip('\n').strip('\r')
                ff.close() 
        log.logger.info("ApPCB File info:dataTobeEncrypted " + str(datatobeencrypted))
        pad="#"  
        length = len(datatobeencrypted)
        paddinglength=round_up(length)
        dataafterpad=datatobeencrypted.ljust(paddinglength,pad)
        cipherdatatext=aesencryption.encrypt(dataafterpad,sitekey)
        cipherdatatexttt=str(cipherdatatext).strip("b'").strip("'")
        #decryptdata=aesencryption.decrypt(cipherdatatext,sitekey)
        with open(appcbpath,'w') as f:
            f.write(str(cipherdatatexttt))
            f.close()
        log.logger.info("ApPCB File info:Datastring cipher " + str(cipherdatatext))
        isdatafilecreated=True
    except Exception as ex:
        log.logger.error(ex)
    return isdatafilecreated
def processindsinwebapi(listinds,rawdatapath,nooffiles,path,metafilep,datafilep,zipfilep,rturl,dturl):
    delayresp=''
    normalresp=''
    currDate = datetime.now()
    current_year = datetime.now().strftime("%Y")    
    files = glob.glob(os.path.join(rawdatapath, "*.txt"))
    selected_files = files[:nooffiles]
    for station in listinds:
        try:
            siteId=station["siteId"]
            siteKey=station["siteKey"]
            stationId=station['stationId']
            log.logger.info("siteId  : " + str(siteId) + "  StationId  : " + str(stationId) + "  sitkey  : " + str(siteKey))
            Filterchannels = [path for path in path if path["StationId"] == stationId]
            channels={"Channels": Filterchannels}
            channel_list = channels["Channels"]
            monitoring_id = list(set([channel['MonitoringUnitId'] for channel in channel_list]))
            for monid in monitoring_id:
                if len(channel_list)>0:
                    filtered_channels = [x for x in channel_list if x['MonitoringUnitId'] == monid]
                    undeltefileslist=[]
                    appmodel,nondeletefilelist = filesprocess.GetDataFromFiles(filtered_channels, currDate, 1, selected_files)
                    createappcbmetafile(metafilep)
                    completefilename = siteId+"_"+str(monid).strip('\n').strip('\r')+"_"+current_year+ "{:02d}{:02d}{:02d}{:02d}{:02d}".format(currDate.month, currDate.day, currDate.hour, currDate.minute, currDate.second)
                    completefilepath=os.path.join(datafilep, completefilename + ".csv")                                               
                    normaldata  = [item for item in appmodel if item['DataQualityCode'] == 'U']
                    delaydata  = [item for item in appmodel if item['DataQualityCode'] == 'L']
                    log.logger.info("AppcbFileUploadService  delay data count: " +str(len(delaydata)))
                    log.logger.info("AppcbFileUploadService  normal data count: " +str(len(normaldata)))
                    if(len(delaydata)>0):
                        delayDataFileName = delaydata[0]['UnixTimestamp']
                        delayDateTime = datetime.fromtimestamp(delayDataFileName)
                        delayyear=delayDateTime.strftime("%Y")
                        completedelayFileName=siteId+"_"+str(monid).strip('\n').strip('\r')+"_"+delayyear+ "{:02d}{:02d}{:02d}{:02d}{:02d}".format(delayDateTime.month, delayDateTime.day, delayDateTime.hour, delayDateTime.minute, delayDateTime.second)
                        completedelaypath=os.path.join(datafilep, completedelayFileName + ".csv")    
                        createappcbdatafilefromlist(delaydata,completedelaypath,currDate,monid,siteKey)
                        CreateZipFileWithMetaandDataFile(metafilep,completedelaypath,os.path.join(zipfilep,completedelayFileName+'.zip'))
                        delayresp=upload.uploadtoappcbserver(dturl,os.path.join(zipfilep,completedelayFileName+'.zip'),currDate,siteKey,siteId)
                        archiver.DeleteDataFileAndArchiveZipFile(completedelaypath,os.path.join(zipfilep,completedelayFileName+'.zip'))
                    if(len(normaldata)>0):
                        createappcbdatafilefromlist(normaldata,completefilepath,currDate,monid,siteKey)
                        CreateZipFileWithMetaandDataFile(metafilep,completefilepath,os.path.join(zipfilep,completefilename+'.zip'))
                        normalresp=upload.uploadtoappcbserver(rturl,os.path.join(zipfilep,completefilename+'.zip'),currDate,siteKey,siteId)
                        archiver.DeleteDataFileAndArchiveZipFile(completefilepath,os.path.join(zipfilep,completefilename+'.zip'))
        except Exception as ex:
            log.logger.error(ex)
    if "success" in str(normalresp) or "success" in str(delayresp):
        for file in selected_files:
            try:
                os.remove(file)
            except Exception as e:
                pass



