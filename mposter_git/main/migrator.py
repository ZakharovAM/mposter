import imaplib
from email import message_from_bytes, message
from imapclient import imap_utf7
from dateutil import parser
import time
from pprint import pprint as p


decode = imap_utf7.decode
encode = imap_utf7.encode


class ImapConnect:

    def conDate(self, date):
        date = parser.parse(date)
        date = date.timetuple()
        return date

    @staticmethod
    def _box_name_and_seen_unseen_(bx_name, src):
        """¬ыбери почтовый €щик, верни его название + количества прочитанных и непрочитанных писем """
        src.select(bx_name.decode("utf8").strip())
        SEEN = src.search(None, '(SEEN)')[-1][0].split()
        UNSEEN = src.search(None, '(UNSEEN)')[-1][0].split()
        return decode(bx_name), dict(ascii_name=bx_name, seen=SEEN, unseen=UNSEEN)

    def __init__(self,
                 imap_src,
                 logopass_src,

                 imap_dst='imap.timeweb.ru',
                 logopass_dst=None
                 ):
        """
        logopass_xxx - список [логин, пароль]

        """

        if logopass_dst is None:
            logopass_dst = logopass_src

        """Constructor"""
        self.src = imaplib.IMAP4_SSL(imap_src)
        self.src.login(logopass_src[0], logopass_src[1])
        #        self.src.enable('UTF8=ACCEPT')

        self.dst = imaplib.IMAP4_SSL(imap_dst)
        self.dst.login(logopass_dst[0], logopass_dst[1])
        #        self.dst.enable('UTF8=ACCEPT')

        # ѕолучи список с названием папок на сервере (не латинские символы будут в нечитаемом формате)
        box_list = self.src.list()
        if box_list[0] == 'OK' or box_list[0] == "OK":
            self.not_readable_box_list = [
                x.decode().replace('"', '').replace("'", '').replace("\\", '').replace('|', '').replace('.',
                                                                                                        '').split()[-1]
                for x in box_list[-1]]
        else:
            p(f"wrong statos code:  {box_list[0]}")



        # print(self.not_readable_box_list)
        # Cоздай словарь, ключ - им€ папки: значение список [прочитанные письма, непрочитанные письма]
        self.copied_emails = dict(
            (self._box_name_and_seen_unseen_(x, self.src) for x in self.not_readable_box_list)
        )
        p(self.copied_emails)

    def coping(self):
        p('start copping:')
        for key, value in self.copied_emails.items():
            p(key + f"( ascii_name:  {value['ascii_name']})")
            if not self.dst.select(value['ascii_name'].strip())[0].endswith('OK'):
                self.dst.create(value['ascii_name'].strip())

            if value['seen']:
                p('seen---->' + decode(key) + ':')
                for x in value['seen']:
                    p(x)
                    p(self.src.fetch(x, '(RFC822)'))
                    msg = self.src.fetch(x, '(RFC822)')[1]
                    try:
                        em = message_from_bytes(msg[0][1], _class=message.EmailMessage)

                    except:
                        p(msg)
                        input('except')

                    d = self.conDate(str(em['date']))
                    time.mktime(d)
                    self.dst.append(value['ascii_name'].strip().decode('utf8').strip(),
                                    r'\SEEN',
                                    imaplib.Time2Internaldate(time.mktime(d)),
                                    em.as_bytes())

            if value['unseen---->' + decode(key) + ':']:
                p('unseen')
                for x in value['unseen']:
                    p(x)
                    msg = self.src.fetch(x, '(RFC822)')[1]
                    p('msg:  \n')
                    p(msg)
                    print(self.src.store(x, r'-FLAGS', r'\SEEN'))
                    em = message_from_bytes(msg[0][1], _class=message.EmailMessage)

                    d = self.conDate(str(em['date']))
                    time.mktime(d)
                    self.dst.append(value['ascii_name'].strip().decode('utf8').strip(),
                                    r'\UNSEEN',
                                    imaplib.Time2Internaldate(time.mktime(d)),
                                    em.as_bytes())
                    
print(115)