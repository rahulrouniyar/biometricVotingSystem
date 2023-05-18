import serial

VERIFY_PASSWORD = b'\x00'
GET_IMAGE = b'\x01'
IMAGE2TZ = b'\x02'
CREATE_MODEL = b'\x03'
UPLOAD_TEMPLATE = b'\x04'
DOWNLOAD_TEMPLATE = b'\x05'
MATCH_TEMPLATE = b'\x06'

TEMPLATE_SIZE = 556

'''All of the constants below are written from the perspective of fingerprint below.
These are the confirmations sent by the fingerprint module upon sending some instructions.'''

FINGERPRINT_OK = b'\x00'                #Command execution is complete
FINGERPRINT_PACKETRECIEVEERR = b'\x01'  #Error when receiving data package

FINGERPRINT_PASSFAIL = b'\x13'          #wrong password

FINGERPRINT_NOFINGER = b'\x02'          #can't detect finger
FINGERPRINT_IMAGEFAIL = b'\x03'         #fail to collect finger image

FINGERPRINT_IMAGEMESS = b'\x06'         #fail to generate character file due to the over-disorderly fingerprint image
FINGERPRINT_FEATUREFAIL = b'\x07'       #fail to generate character file due to lackness of character point or over-smallness of fingerprint image
FINGERPRINT_INVALIDIMAGE = b'\x15'      #fail to generate the image for the lackness of valid primary image

FINGERPRINT_ENROLLMISMATCH = b'\x0A'    #fail to combine the character files. That’s, the character files don’t belong to one finger

FINGERPRINT_TIMEOUT = b'\x09'           #Timeout was reached

FINGERPRINT_UPLOADFEATUREFAIL = b'\x0D' #error when uploading template
DOWNLOAD_COMPLETE = b'\x0C'             #download to pc complete

FINGERPRINT_PACKETRESPONSEFAIL = b'\x0E'#fail to receive the following data packages
UPLOAD_COMPLETE = b'\x0B'               #upload to FP module complete

FINGERPRINT_MATCH = b'\x00'             #templates of the two buffers are matching
FINGERPRINT_NOMATCH = b'\x08'           #templates of the two buffers aren’t matching


'''Exception classes below.'''

class PacketRecieveError(Exception):
    def __str__(self):
        return "Error in module receiving packets."

class PasswordError(Exception):
    def __str__(self):
        return "Wrong password."

class ImageError(Exception):
    def __init__(self, param):
        self.code = param

    def __str__(self):
        if (self.code == FINGERPRINT_NOFINGER):
            return "Can't detect finger."
        elif (self.code == FINGERPRINT_IMAGEFAIL):
            return "Fail to collect finger image."
        else:
            return "sorry image error"

class TemplateCreationError(Exception):
    def __init__(self, param):
        self.code = param

    def __str__(self):
        if (self.code == FINGERPRINT_IMAGEMESS):
            return "over-disorderly fingerprint image."
        elif (self.code == FINGERPRINT_FEATUREFAIL):
            return "lackness of character point or over-smallness of fingerprint image."
        elif (self.code == FINGERPRINT_INVALIDIMAGE):
            return "lackness of valid primary image."
        else:
            return "sorry template creation"

class ModelCreationError(Exception):
    def __init__(self, param):
        self.code = param

    def __str__(self):
        if (self.code == FINGERPRINT_ENROLLMISMATCH):
            return "fail to combine the character files. That’s, the character files don’t belong to one finger."
        else:
            return "sorry model creation"

class UploadError(Exception):
    def __init__(self, param):
        self.code = param

    def __str__(self):
        if (self.code == FINGERPRINT_UPLOADFEATUREFAIL):
            return "upload failed."
        elif (self.code == FINGERPRINT_TIMEOUT):
            return "timout reached."

class DownloadError(Exception):
    def __init__(self, param):
        self.code = param

    def __str__(self):
        if (self.code == FINGERPRINT_PACKETRESPONSEFAIL):
            return "download failed."
        elif (self.code == FINGERPRINT_TIMEOUT):
            return "timout reached."
        elif (self.code == FINGERPRINT_PACKETRECIEVEERR):
            return "packet receive error"
        else:
            return "sorry downloaderror"
        

class MatchingError(Exception):
    def __init__(self, param):
        self.code = param

    def __str__(self):
        if (self.code == FINGERPRINT_NOMATCH):
            return "fingerprint does not match."
        else:
            return str(self.code)

ser = serial.Serial('COM5', baudrate = 9600)

def handleOperation(instructionCode, exceptionName = None):
    ser.write(instructionCode)
    confirmationCode = ser.read()
    if not confirmationCode == FINGERPRINT_OK:
        raise exceptionName(confirmationCode)

def verifyPassword():
    handleOperation(VERIFY_PASSWORD, PasswordError)
    return True 

def getImage():
    handleOperation(GET_IMAGE, ImageError)
    return FINGERPRINT_OK

def createTemplate(charBuffer):
    ser.write(IMAGE2TZ)
    ser.write(charBuffer)
    confirmationCode = ser.read()
    if not confirmationCode == FINGERPRINT_OK:
        raise TemplateCreationError(confirmationCode)

def createModel():
    handleOperation(CREATE_MODEL, ModelCreationError)

def uploadTemplate(template):
    ser.write(UPLOAD_TEMPLATE)
    confirmationCode = ser.read()
    if not confirmationCode == FINGERPRINT_OK:
        raise UploadError(confirmationCode)
    for i in range(TEMPLATE_SIZE):
        try:
            ser.write(template[i].to_bytes(1, byteorder='big'))
        except serial.SerialTimoutException:
            raise serial.SerialTimeoutException()

def downloadTemplate():
    ser.write(DOWNLOAD_TEMPLATE)
    confirmationCode = ser.read()
    if not confirmationCode == FINGERPRINT_OK:
        raise DownloadError(confirmationCode)
    for i in range(TEMPLATE_SIZE):
        databyte = ser.read()
        # print(databyte)
        yield databyte

def matchTemplate():
    ser.write(MATCH_TEMPLATE)
    confirmationCode = ser.read()
    if not confirmationCode == FINGERPRINT_MATCH:
        raise MatchingError(confirmationCode)
