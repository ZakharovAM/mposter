from imaplib import IMAP4_SSL 
from email import message_from_bytes, message
from dateutil import parser
import time

class mainObject:
    
     
    src, dst = None
    indexes = {}
    
    def conDate(self, date):
        date = parser.parse(date)
        date = date.timetuple()
        return date
        
    
    def __init__(self,  s, d, logopass,):
        src = IMAP4_SSL(s)
        dst = IMAP4_SSL(d)
        src.login(user = logopass[0], password = logopass[1])
        dst.login(user = logopass[0], password = logopass[1])
        
        
        
        ans, folders = src.list()
        src_folders = [x.split()[-1] for x in folders]
        
        ans, folders = dst.list()
        dst_folders = [x.split()[-1] for x in folders]
        
        for folder in src_folders:
             if folder not in dst_folders:
                 dst.create(folder.strip()) 

        
    def seen_unseen(self, folder):
        
        self.src.select(folder)
        
        self.indexes[folder]={ "SEEN" : None,
                               "UNSEEN" : None, 
                               "ALL" : None
                               }
        
        self.indexes[folder]["SEEN"] = self.src.search(None, 'SEEN')[1][0].split()
        self.indexes[folder]["UNSEEN"] = self.src.search(None, 'UNSEEN')[1][0].split()
        self.indexes[folder]["ALL"] = self.src.search(None, 'ALL')[1][0].split()

    
    def get_mail(self, folder):
        for num in self.indexes[folder]["ALL"]:
            
            ans, data = self.src.fetch(num, '(RFC822)')
            em = message_from_bytes(data[0][1], _class=message.EmailMessage)
            d = self.conDate(str(em['date']))
            flag = r''    
            
            if num in self.indexes[folder]["UNSEEN"]:
                
                flag = r'\UNSEEN',
                self.src.store(num, r'-FLAGS', r'\SEEN')
            
            else:
                
                flag = r'\SEEN',
            
            
            self.dst.append(
                            folder,
                            flag,
                            imaplib.Time2Internaldate(time.mktime(d)),
                            em.as_bytes()
                            )
        
            
            
