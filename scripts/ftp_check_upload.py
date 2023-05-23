import os
from ftplib import FTP

print("logging in...")
ftp = FTP(os.environ.get("FTP_SERVER"), timeout=30)
ftp.login(os.environ.get('FTP_USER'),  os.environ.get('FTP_PASS'))
ftp.cwd(os.environ.get('FTP_DIR'))
ftp.set_pasv(False)

print("uploading...")
ftp.storbinary('STOR test.srt', fp=open('./test.srt', 'rb'))
print("done")
