import os
import win32security
import ntsecuritycon as con
import pandas as pd
import configparser
#ALWAYS RUN THIS SCRIPT AS ADMIN OTHERWISE YOU CANT CHANGE OTHERS PERMISSION

ps = configparser.ConfigParser()
ps.read('testong.ini')
#show accesss control list, from a file
def show_cacls (filename):
    for line in os.popen("cacls %s" % filename).read().splitlines():
        print(line)

if __name__ == '__main__':
    dlp_file = pd.read_csv('acl.csv')
    directory = ps.get('folder_protect', 'folder') + '/'
    for row in range(0, len(dlp_file)):
        if(dlp_file['tags'][row] == 'confidential'):
            #fucntion to get and set ACL
            access_info = win32security.GetFileSecurity(directory+dlp_file['filename'][row], win32security.DACL_SECURITY_INFORMATION)
            #funtion to get owner info of a file
            owner_info = win32security.GetFileSecurity(directory+dlp_file['filename'][row], win32security.OWNER_SECURITY_INFORMATION)

            #lookup for SID of user
            everyone, domain, type = win32security.LookupAccountName("", "Everyone")
            admins, domain, type = win32security.LookupAccountName("", "Administrators")
            owner_sid = owner_info.GetSecurityDescriptorOwner()

            # open(directory+dlp_file['filename'][row], "r").close()
            show_cacls(directory+dlp_file['filename'][row])

            #set permission
            dacl = win32security.ACL()
            dacl.AddAccessDeniedAce(win32security.ACL_REVISION, con.SECURITY_NULL_RID, everyone)
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE, owner_sid)
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admins)

            #EXECUTE ORDER 66!!!
            access_info.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(directory+dlp_file['filename'][row], win32security.DACL_SECURITY_INFORMATION, access_info)
            show_cacls(directory+dlp_file['filename'][row])

        elif(dlp_file['tags'][row] == 'public'):
            # fucntion to get and set ACL
            access_info = win32security.GetFileSecurity(directory + dlp_file['filename'][row],win32security.DACL_SECURITY_INFORMATION)
            # funtion to get owner info of a file
            owner_info = win32security.GetFileSecurity(directory + dlp_file['filename'][row],win32security.OWNER_SECURITY_INFORMATION)

            # lookup for SID of user
            everyone, domain, type = win32security.LookupAccountName("", "Everyone")
            admins, domain, type = win32security.LookupAccountName("", "Administrators")
            owner_sid = owner_info.GetSecurityDescriptorOwner()

            # open(directory+dlp_file['filename'][row], "r").close()
            show_cacls(directory + dlp_file['filename'][row])

            # set permission
            dacl = win32security.ACL()
            # dacl.AddAccessDeniedAce(win32security.ACL_REVISION, con.SECURITY_NULL_RID, everyone)
            # dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE,
            #                          owner_sid)
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, everyone)

            # EXECUTE ORDER 66!!!
            access_info.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(directory + dlp_file['filename'][row],win32security.DACL_SECURITY_INFORMATION, access_info)
            show_cacls(directory + dlp_file['filename'][row])