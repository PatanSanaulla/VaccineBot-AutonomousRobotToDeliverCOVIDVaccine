import smtplib
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import imaplib
import time

# Email Personal information
smtpUser = 'vaccinebot786@gmail.com'
smtpPass = '809Tfinale'

initiatorEmail = 'ENPM809TS19@gmail.com'

def sendEmail(picName):
    
    # Destination email information
    toAdd = ['spatan07@terpmail.umd.edu', initiatorEmail, 'skotasai@umd.edu']
    fromAdd = smtpUser
    subject = 'Assignment output: Image recorded of '+ picName
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = fromAdd
    #msg['To'] = toAdd
    msg['To'] = ",".join(toAdd)
    msg.preamble = "Image recorded of "+picName
    
    #Email Text
    body = MIMEText("Image recorded of "+ picName)
    msg.attach(body)

    #Attach image
    fp = open(picName+'.jpg','rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    
    #send email
    s = smtplib.SMTP('smtp.gmail.com',587)

    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtpUser, smtpPass)
    s.sendmail(fromAdd, toAdd, msg.as_string())
    s.quit()
    
    print('[INFO] Email Sent!')
    
    # Define time stamp & record an image
    #pic_time = datetime.now().strftime('%Y%m%d%H%M%S')
    #command = 'raspistill -w 1280 -h 720 -vf -hf -o ' +pic_time+ '.jpg'
    #os.system(command)

def checkStartEmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(smtpUser, smtpPass)
    mail.list();
    
    count = 0
    
    while count < 60:
        try:
            #connect to inbox
            mail.select("inbox")
            
            #search for an unread email form user's email address
            result, data = mail.search(None, '(UNSEEN FROM "spatan07@terpmail.umd.edu")') 
            #result, data = mail.search(None, '(UNSEEN FROM "ENPM809TS19@gmail.com")') #initiatorEmail
            print("[INFO] Checking for mail...")
            #print(result)
            #print(len(data))
            
            ids = data[0] #data is the list of the emails
            id_list = ids.split()
            
            latest_email_id = id_list[-1] #get the last email
            result, data = mail.fetch(latest_email_id, "(RFC822)")
            
            if data is None:
                print("[INFO] Checking for mail...")
                
            if data is not None:
                print("[INFO] Process Initiated!")
                return True

                
        except IndexError:
            time.sleep(2)
            if count < 59:
                count = count + 1
                continue
            else:
                print("[INFO] Email not received!")
                return False
                count = 60