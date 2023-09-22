import os
import log
def DeleteDataFileAndArchiveZipFile(dataFilePath,zipfilepath):
    try:
        destinationpath = os.path.join(os.path.dirname(zipfilepath), "Archive")
        os.remove(dataFilePath)
        if not os.path.exists(destinationpath):
            os.makedirs(destinationpath)
        new_zip_file_path = os.path.join(destinationpath, os.path.basename(zipfilepath))
        os.rename(zipfilepath, new_zip_file_path)
    except Exception as e:
        log.logger.error(e)
    