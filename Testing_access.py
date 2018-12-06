import os
import win32security
import ntsecuritycon as con

FILENAME = "D:/temp2.txt"


#ALWAYS RUN THIS SCRIPT AS ADMIN OTHERWISE YOU CANT CHANGE OTHERS PERMISSION

#show accesss control list, from a file
def show_cacls (filename):
  print
  print
  for line in os.popen ("cacls %s" % filename).read ().splitlines ():
    print(line)

#fucntion to get and set ACL
access_info = win32security.GetFileSecurity(FILENAME, win32security.DACL_SECURITY_INFORMATION)
#funtion to get owner info of a file
owner_info = win32security.GetFileSecurity (FILENAME, win32security.OWNER_SECURITY_INFORMATION)

#lookup for SID of user
everyone, domain, type = win32security.LookupAccountName ("", "Everyone")
admins, domain, type = win32security.LookupAccountName ("", "Administrators")
owner_sid = owner_info.GetSecurityDescriptorOwner ()

open(FILENAME, "r").close()
show_cacls(FILENAME)

#set permission
dacl = win32security.ACL ()
dacl.AddAccessDeniedAce (win32security.ACL_REVISION, con.SECURITY_NULL_RID, everyone)
dacl.AddAccessAllowedAce (win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE, owner_sid)
dacl.AddAccessAllowedAce (win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admins)

#EXECUTE ORDER 66!!!
access_info.SetSecurityDescriptorDacl (1, dacl, 0)
win32security.SetFileSecurity (FILENAME, win32security.DACL_SECURITY_INFORMATION, access_info)
show_cacls (FILENAME)