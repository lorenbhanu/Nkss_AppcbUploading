from datetime import datetime, timedelta
from datetime import datetime
from datetime import datetime, timezone
import log



def to_unixtime(dt):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return int((dt - epoch).total_seconds())

def GetDataFromFiles(filtered_channels, currDate, offset, selected_files):
    nondeletefileslist=[]
    rawDataList=[]
    datamodel_list=[]
    try:
        if len(selected_files) >0:
            for file in selected_files:
                with open(file, 'r') as f:
                    lstparameterwithData = f.readlines()
                lstparameterwithData = [x.strip() for x in lstparameterwithData]       
                rawDataList.extend(lstparameterwithData)      
        if len(rawDataList)>0:
            for main_string in rawDataList:
                split_data = main_string.split(',')
                device_id = split_data[1]
                date_time = split_data[0]
                channel_name = split_data[2]   
                oxidename=""                       
                dt_latest = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
                dataQuality=''
                if dt_latest < currDate - timedelta(minutes=15):
                    dataQuality = "L"
                else:
                    dataQuality = "U"      
                chnl = next((x for x in filtered_channels if x['StationId'] == int(device_id) and x['ChannelName'] == channel_name), None)
                utcdate = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                if chnl is not None:
                    chnldataValue=''
                    chnldataValue = format(float(split_data[3]), '.3f')  
                    unixtime=to_unixtime(dt_latest)
                    channel=chnl
                    # Create a dictionary for channel_model
                    channel_model = {
                        "Id": channel['Id'],
                        "StationId": channel['StationId'],
                        "ChannelName": channel['ChannelName'],
                        "PCBChannelName": channel['PCBChannelName'],
                        "ANALYZER_ID": channel['ANALYZER_ID'],
                        "UNIT_ID": channel['UNIT_ID'],
                        "MonitoringUnitId": channel['MonitoringUnitId'],
                        "ParameterId": channel['ParameterId'],
                        "siteId": channel['siteId'],
                        "SiteUid": channel['SiteUid'],
                        "CalibrationFlag": channel['CalibrationFlag'],
                        "MaintenanceFlag": channel['MaintenanceFlag']
                    }

                    # Create a list of dictionaries for datamodel_list
                    datamodel =                     {
                            "datauploadId": "",
                            "StationId": "",
                            "ChannelId": channel_model["Id"],
                            "SiteId": channel_model["siteId"],
                            "SiteUid": channel_model["SiteUid"],
                            "MonitoringUnitId": channel_model["MonitoringUnitId"],
                            "AnalyzerId": channel_model["ANALYZER_ID"],
                            "ParameterId": channel_model["ParameterId"],
                            "ParameterName": channel_model["PCBChannelName"],
                            "Reading": chnldataValue,
                            "UnitId": channel_model["UNIT_ID"],
                            "DataQualityCode": dataQuality,
                            "RawReading": chnldataValue,
                            "UnixTimestamp": unixtime,
                            "LogTime": dt_latest,
                            "CalibrationFlag": channel_model["CalibrationFlag"],
                            "MaintainceFlag": channel_model["MaintenanceFlag"]
                        }
                    datamodel_list.append(datamodel)

    except Exception as ex:
        log.logger.error(ex)
    return datamodel_list,nondeletefileslist


     