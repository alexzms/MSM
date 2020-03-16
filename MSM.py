import paramiko
import datetime
import hashlib
import os
import threading
import time
import msvcrt
import sys


#ver0.1: fuckass - 0b9a54438fba2dc0d39be8f7c6c71a58
#ver0.2: shit - 1223b8c30a347321299611f873b449ad
spid = '1223b8c30a347321299611f873b449ad'
password = ''
permission = 0
configexist = False
config = []

rts_flag = True
rts_pauseflag = False
rflc = 0

def readconfig():
    global config
    global configexist
    if os.path.exists('config.txt'):
        configexist = True
        f = open(r"./config.txt",'r')
        config = f.readlines()

def login():
    global password
    if configexist:
        password = config[0]
        print ("已从文件读取服务器密码")
        return
    password = input('server-passcode>')

def getPermission(ssh):
    stdin, stdout, stderr = ssh.exec_command('grep -q "' + spid + '" /root/spid.msm; echo $?')
    permissionid = stdout.readlines()[0].replace("\n", "")
    if permissionid == '0':
        return 1
    else :
        return 0

def startserver(ssh):
    stdin, stdout, stderr = ssh.exec_command('screen -rd server2 -p 0 -X stuff "java -Xmx1786M -jar craftbukkit-1.15.2.jar nogui";screen -rd server2 -p 0 -X stuff $\'\n\'')

def terminal(ssh):
    global rts_flag
    global rts_pauseflag
    global rflc
    rts_flag = True
    threadrts = threading.Thread(target=remoteTerminalStream,args = (ssh,))
    threadrts.start()
    uinput = ""
    while 1:
        while 1:
            time.sleep(0.2)
            if(msvcrt.kbhit()):
                rts_pauseflag = True
                uinput = input()
                break
        if uinput == '.help':
            helpterminal()
        elif uinput == '.back':
            rts_pauseflag = False
            rts_flag = False
            threadrts.join()
            return
        elif uinput == '.backup':
            theTime = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
            myexec(ssh,'zip -r /root/server_pure/backup/"' + theTime + '".zip /root/server_pure/world /root/server_pure/world_the_end /root/server_pure/world_nether')
            #myexec(ssh,'zip -r /root/server_pure/backup/"' + theTime + '".zip /root/server_pure/world_test/t1 /root/server_pure/world_test/t2')
            print(theTime + '.zip已备份')
        elif uinput == '.restore':
            myexec2(ssh,"dir /root/server_pure/backup")
            rfile = input("请输入需要恢复的文件名(无需书写.zip,若输入为空,则退出恢复): ")
            if rfile != "":
                #send_command(ssh,'stop')
                myexec2(ssh,"rm -rf /root/server_pure/world;rm -rf /root/server_pure/world_the_end;rm -rf /root/server_pure/world_nether")
                print("文件已删除，正在恢复备份..")
                myexec2(ssh,"unzip /root/server_pure/backup/\""+rfile+".zip\" -d /")
                print("恢复已完成，请启动服务器")
            else:
                print("恢复备份已取消")
        elif uinput == '.start':
            rflc = 0
        else:
            send_command(ssh,uinput)
        rts_pauseflag = False


def remoteTerminalStream(ssh):
    global rflc
    global rts_flag
    global rts_pauseflag
    sftp = ssh.open_sftp()
    while 1:
        while 1:
            time.sleep(0.5)
            if (not rts_flag):
                return
            while True:
                if (rts_pauseflag):
                    time.sleep(1)
                else:
                    break
            rfl = int(myexec(ssh,"sed -n '$=' /root/server_pure/logs/latest.log"))
            if rfl > rflc:
                break
        rfs = sftp.open('/root/server_pure/logs/latest.log', 'r+')
        rf = rfs.readlines()
        for x in range(rflc,rfl):
            print(rf[x].replace('[m','').replace('[0;37;1m','').replace('[0;33;22m','').replace('[0;32;1m',''),end='')
        rflc = rfl

def send_command(ssh,uinput):
    ssh.exec_command('screen -rd server2 -p 0 -X stuff "'+ uinput + '";screen -rd server2 -p 0 -X stuff $\'\n\'')

def myexec(ssh,str):
    stdin, stdout, stderr = ssh.exec_command(str)
    return stdout.readlines()[0].replace("\n", "")

def myexec2(ssh,str):
    stdin, stdout, stderr = ssh.exec_command(str)
    s = stdout.readlines()
    for x in s:
        print (x,end="")

def helpterminal():
    print ("命令支持:\n\t所有MC原生指令\n\t.back,.help,.backup,.restore + {backupname}")

def helpmain():
    print('start,terminal,exit')
 
def mainfunc():
    readconfig()
    login()
    ssh = paramiko.SSHClient()
    key = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(key)
    print('正在连接至MC服务器...')
    try:
        ssh.connect('47.114.188.135', 22, 'root', password ,timeout=5)
    except:
        print ("密码错误!正在退出程序")

    print('连接成功，正在请求权限...')

    permission = getPermission(ssh)
    if permission == 1:
        print('欢迎使用MC服管理软件 !')
    else:
        print('权限申请失败！该软件已过期！')
        exit()
    helpmain()
    while 1:
        uinput = input('>')
        if uinput == 'help':
            helpmain()
        if uinput == 'start':
            startserver(ssh)
        if uinput == 'terminal':
            terminal(ssh)
        if uinput == 'exit':
            return
        


mainfunc()