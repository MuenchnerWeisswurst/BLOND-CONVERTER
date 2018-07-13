from ftplib import FTP
import os 

#Downloads all 1 second summery files from the FTP
#to your computer, keeping the same folder structure

"""
Helper function that finds a string in list of strings
return: string from the list conatining the keyword
"""
def find(a_list, keyword):
    for item in a_list:
        if item in keyword or keyword in item:
            return item 
    return None

"""
Helper function that safely creates a folder
"""
def save_create(path):
    if not os.path.isdir(path):
        os.makedirs(path)

"""
Helper function that maps unix paths to windows paths
"""
def path_to_win(path):
    path.replace('/','\\')
    return path 

"""
"""
def get():
    ftp_socket = FTP('138.246.224.34')
    ftp_socket.login(user='m1375836',passwd='m1375836')
    ftp_socket.cwd('BLOND/BLOND-250/')
    dates = ftp_socket.nlst()
    for date in dates:
        clear = '/clear/'
        directory = 'BLOND/BLOND-250/'+date+clear
        ftp_socket.cwd(date+clear)
        files = ftp_socket.nlst()
        file_name = find(files,'summary')
        print file_name
        if file_name is not None:
            home_dir = path_to_win("../" + directory + file_name)
            save_create(path_to_win('../' + directory))
            file = open(home_dir,'wb')
            ftp_socket.retrbinary('RETR %s' % file_name,file.write)
        ftp_socket.cwd('..')
        for medal_id in range(1,16):
            directory = 'medal-{}/'.format(medal_id)
            ftp_socket.cwd(directory)
            files = ftp_socket.nlst()
            file_name = find(files,'summary')
            print file_name
            if file_name is not None:
                home_dir = path_to_win("./BLOND/BLOND-250/" + date + '/' +directory + file_name)
                save_create(path_to_win("./BLOND/BLOND-250/" + date + '/' +directory))
                file = open(home_dir,'wb')
                ftp_socket.retrbinary('RETR %s' % file_name,file.write)
            ftp_socket.cwd('..')
        ftp_socket.cwd('..')

get()