import imaplib
from imaplib import IMAP4_SSL 
from email import message_from_bytes, message
from dateutil import parser
import time
from pprint import pprint as p

class mainObject:
    
     
    src = None
    dst = None
    indexes = {}
    separator_src = None
    separator_dst = None
    mapfolders = {}
    count=0
    
    
    def conDate(self, date):
        date = parser.parse(date)
        date = date.timetuple()
        return date
        
    
    def __init__(self,  s, d, logopass):
        self.src = IMAP4_SSL(s)
        time.sleep(1)
        self.dst = IMAP4_SSL(d)
        time.sleep(1)
        self.src.login(user = logopass[0], password = logopass[1])
        self.dst.login(user = logopass[0], password = logopass[1])
        
        
        
        ans, folders = self.src.list()
        src_folders = [x.split()[-1].strip(b"'").strip(b'"') for x in folders]
        self.separator_src = folders[0].split()[1].strip(b"'").strip(b'"')
        print(f"self.separator_src:  {self.separator_src}")
        ans, folders = self.dst.list()
        self.separator_dst = folders[0].split()[1].strip(b"'").strip(b'"')
        
        dst_folders = [x.split()[-1].strip(b"'").strip(b'"') for x in folders]
        p(f"self.separator_dst:  {self.separator_dst}")
        
        self.mapfolders = {src_folder:dst_folder for src_folder, dst_folder in zip(src_folders, src_folders) }
        
        #p("mapfolders")
        #p(self.mapfolders)
        
        

        for folder in src_folders:
             if folder not in dst_folders:
                 res = folder.strip(b"'").strip(b'"').replace(self.separator_src, self.separator_dst)
                 # формат для создания почтового язика у Timeweb
#                 print(f'{res.strip()}'.encode().strip(b'"').strip(b"'")) 
                 
                 if not res.upper().startswith(b"INBOX"): 
                     res=self.separator_dst.join([b"INBOX" , res])
                     
                 self.dst.create(res) 
                 self.mapfolders[folder] = res;
                 
                 #p(self.mapfolders)
        
        
    def seen_unseen(self, folder):
        
        self.src.select(folder)
        
        self.indexes[folder]={ "SEEN" : None,
                               "UNSEEN" : None, 
                               "ALL" : None
                               }
        
        self.indexes[folder]["SEEN"] = self.src.search(None, 'SEEN')[1][0].split()
        self.indexes[folder]["UNSEEN"] = self.src.search(None, 'UNSEEN')[1][0].split()
        self.indexes[folder]["ALL"] = self.src.search(None, 'ALL')[1][0].split()

    
    def coping_folders_mails(self, folder):
        for num in self.indexes[folder]["ALL"]:
            
            ans, data = self.src.select(folder)
            p(f"self.src.select({folder}) ans: {ans} data: {data} ")            
                       
            ans, data = self.dst.select(self.mapfolders[folder])
            
            p(f"self.dst.select({self.mapfolders[folder]}) ans: {ans} data: {data} ")            
            
            
            ans, data = self.src.fetch(num, '(RFC822)')
            em = message_from_bytes(data[0][1], _class=message.EmailMessage)
            d = self.conDate(str(em['date']))
            flag = r''    
            
            if num in self.indexes[folder]["UNSEEN"]:
                
                flag = None,
                self.src.store(num, r'-FLAGS', r'\SEEN')
              
            else:
                
                flag = r'\SEEN',
            
            ans, stat = self.dst.append(
                            self.mapfolders[folder],
                            flag,
                            imaplib.Time2Internaldate(time.mktime(d)),
                            em.as_bytes()
                            )
            time.sleep(1)
            self.count+=1
            print(f"{self.count} >>> {folder} : {flag} : {num} \n ans {ans} {stat}")
            
            
    
    def prep(self):
        for key in self.mapfolders.keys():
            self.seen_unseen(key)
        
        p(self.indexes)
            
     
    def cp(self):       
        for key in self.mapfolders.keys():
            print(f" coping from {key} to {self.mapfolders[key]}")
            self.coping_folders_mails(key)
    
    def logout(self):
        
        self.src.logout()
        self.dst.logout()
            
    
a=mainObject("imap.mail.ru",
             "imap.timeweb.ru",
             [ "test@mposter.tk ",
              "6rrrrrrA" ]
             )
a.prep()
a.cp()        
a.logout()
print(0)
