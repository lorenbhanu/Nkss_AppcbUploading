import os
import uuid
import io
import urllib.request
import AES as aesencryption
import log

class FileParameter:
    def __init__(self, file, filename, content_type=None):
        self.file = file
        self.filename = filename
        self.content_type = content_type

def round_up(n):
    return (32 - n % 32) + n

def PostForm(posturll,useragentt,conttype,formmdata,appcbtimedate,aeskeyy,siteiddd):
    request = urllib.request.Request(posturll)
    if not isinstance(request, urllib.request.Request):
        raise ValueError("request is not a urllib.request.Request")
    request.method = 'POST'
    request.add_header('Content-Type', conttype)
    request.add_header('Content-Length', len(formmdata))
    request.timeout = 10
    currentDateTime = appcbtimedate.strftime("%Y-%m-%dT%H:%M:%SZ")
    strheader = siteiddd + ",ver_2.0," + currentDateTime + "," + aeskeyy
    pad ='#'
    lenght=len(strheader)
    padlength=round_up(lenght)
    strheaderafterpad=strheader.ljust(padlength,pad)
    ciphertext=aesencryption.encrypt(strheaderafterpad,aeskeyy)
    cipherdatatexttt=str(ciphertext).strip("b'").strip("'")
    request.add_header('siteId', siteiddd)
    request.add_header('Timestamp', currentDateTime)
    request.add_header("Authorization", "Basic " + cipherdatatexttt)
    ressp=''
    try:
        with urllib.request.urlopen(request, formmdata,timeout=5.0) as response:
            ressp=response.read()
    except Exception as e:
        print(e)
        ressp=e    
    return ressp





def GetMultipartFormData(postp,bounds):
    formDataStream = io.BytesIO()
    needsCLRF=False
    for key, value in postp.items():
        if needsCLRF is True:
            formDataStream.write("\r\n".encode())
        needsCLRF=True
        if isinstance(value, FileParameter):
            file_to_upload = value
            header = f'--{bounds}\r\nContent-Disposition: form-data; name="{key}"; filename="{file_to_upload.filename if file_to_upload.filename else key}"\r\nContent-Type: {file_to_upload.content_type if file_to_upload.content_type else "application/octet-stream"}\r\n\r\n'
            formDataStream.write(bytes(header, 'utf-8'))
            formDataStream.write(file_to_upload.file)
        else:
            postData = f"--{bounds}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}"
            formDataStream.write(postData.encode('utf-8'))
    footer="\r\n--" + bounds + "--\r\n"
    formDataStream.write(footer.encode('utf-8'))
    formDataStream.seek(0)
    formData = formDataStream.read()
    formDataStream.close()
    return formData







def MultipartFormDataPost(postURL,useragent,postparams,appcbdatetime,aeskey,siteid):    
    formDataBoundary = f"----------{uuid.uuid4().hex}"
    content_type = f"multipart/form-data; boundary={formDataBoundary}"
    formmdata=GetMultipartFormData(postparams,formDataBoundary)
    return(PostForm(postURL,useragent,content_type,formmdata,appcbdatetime,aeskey,siteid))

    

def uploadtoappcbserver(url,zipFile,appcbdate,key,siteid):
    responsee=None
    try:
        log.logger.info("-----------APPCB File uploding is started-----------")
        fs = open(zipFile, 'rb')
        data = fs.read()
        fs.close()
        name = os.path.basename(zipFile)
        postParameters = {}
        postParameters["filename"] = name
        postParameters["fileformat"] = "zip"
        postParameters["file"]= FileParameter(data, name, "application/zip")    
        postURL=url
        userAgent = "Someone"
        responsee= MultipartFormDataPost(postURL,userAgent,postParameters,appcbdate,key,siteid)
        log.logger.info("ApPCB File uploding responce status: " + str(responsee))
        log.logger.info("-----------ApPCB File uploding is ended-----------")
    except Exception as ex:
        log.logger.error(ex)
    return responsee