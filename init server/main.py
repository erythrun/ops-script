'''
Author: Athrun
Email: erythron@outlook.com
Date: 2023-01-06 10:24:19
LastEditTime: 2023-03-14 14:28:18
description: linux init, use: python2 init.py <ip.file>(ip port account password)
'''
import os,sys,time


disk_type=1
disk_init='vdb'
disk_mount='/app'
jdk_package='jdk-8u251-linux-arm64-vfp-hflt.tar.gz'
jdk_decompress='jdk1.8.0_251'
add_user='ctgcloud'
add_user_pd='bnStkgj_5w4eEDy'
add_user_home='/home/ctgcloud' #/app/ctgcache,/home/ctgcloud

#diy shell
customize_shell='init.sh'
customize_shell_args='sudo,dns,umask,'
#'sudo,dns,paas,ulimit,umask'

def Prepare(ip, port, username, password):
    prepare_exec1="chmod +x sshpass"
    prepare_exec2="./sshpass -p '{}' ssh -p{} {}@{} 'sudo chmod 777 /tmp'".format(password,port,username,ip)

    file_exec1="./sshpass -p '{}' scp -P {} init-disk.sh {}@{}:/tmp".format(password,port,username,ip)
    add_user_exec1="./sshpass -p '{}' ssh -p{} {}@{} 'sudo chmod 640 /etc/sudoers'".format(password,port,username,ip)
    exec_history=[prepare_exec2,file_exec1,add_user_exec1]
    WriteLog('exec-history.log',exec_history)

    print("Prepare exec: ",prepare_exec1)
    prepare_result1 = os.popen(prepare_exec1).read()
    print("Prepare result: ",prepare_result1)
    time.sleep(1)

    print("Prepare exec: ",prepare_exec2)
    prepare_result2=os.popen(prepare_exec2).read()
    print("Prepare result: ",prepare_result2)
    time.sleep(2)

    print("Prepare exec: ",file_exec1)
    prepare_result5=os.popen(file_exec1).read()
    print("Prepare result: ",prepare_result5)
    time.sleep(1)

    print("Prepare exec: ",add_user_exec1)
    prepare_result6=ip+" Prepare result: "+os.popen(add_user_exec1).read()
    print(prepare_result6)

    result_history=[prepare_result6]
    WriteLog('result-history.log',result_history)


def Java(ip, port, username, password):
    java_exec1="./sshpass -p '{}' scp -P {} {} {}@{}:/tmp/".format(password,port,jdk_package,username,ip)
    java_exec2="./sshpass -p '{}' scp -P {} install-jdk.sh {}@{}:/tmp".format(password,port,username,ip)
    java_exec3='''./sshpass -p '{}' ssh -p{} {}@{} 'bash /tmp/install-jdk.sh "{}" "{}"' '''.format(password,port,username,ip,jdk_package,jdk_decompress)
    exec_history=[java_exec1,java_exec2,java_exec3]
    WriteLog('exec-history.log',exec_history)

    print("Prepare exec: ",java_exec1)
    prepare_result3=os.popen(java_exec1).read()
    print("Prepare result: ",prepare_result3)
    time.sleep(5)

    print("Prepare exec: ",java_exec2)
    prepare_result4=os.popen(java_exec2).read()
    print("Prepare result: ", prepare_result4)
    time.sleep(1)

    java_result=ip+" Java result: "+ os.popen(java_exec3).read()
    print("Java exec: ", java_exec3)
    print(java_result)
    time.sleep(5)

    result_history=[java_result]
    WriteLog('result-history.log',result_history)


def FileSYS(ip, port, username, password):
    file_exec2="./sshpass -p '{}' ssh -p{} {}@{} 'bash /tmp/init-disk.sh {} {} {}'".format(password,port,username,ip, disk_type, disk_init, disk_mount)
    exec_history=[file_exec2]
    WriteLog('exec-history.log',exec_history)

    print("FileSYS exec: ", file_exec2)
    file_sys_result=ip+" FileSYS result: "+os.popen(file_exec2).read()
    print(file_sys_result)

    result_history=[file_sys_result]
    WriteLog('result-history.log',result_history)


def AddUser(ip, port, username, password):
    add_user_exec1="./sshpass -p '{}' ssh -p{} {}@{} 'sudo useradd {} -d {} '".format(password,port,username,ip,add_user,add_user_home)
    #change home folder
    #add_user_exec1="./sshpass -p '{}' ssh -p{} {}@{} 'sudo useradd {}'".format(password,port,username,ip,add_user)
    add_user_exec2='''./sshpass -p '{}' ssh -p{} {}@{} "echo '{}' | sudo passwd --stdin {}" '''.format(password,port,username,ip,add_user_pd,add_user)
    add_user_exec3='''./sshpass -p '{}' ssh -p{} {}@{} 'echo "{} ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers' '''.format(password,port,username,ip,add_user)
    exec_history=[add_user_exec1,add_user_exec2,add_user_exec3]
    WriteLog('exec-history.log',exec_history)
    print("AddUser exec: ", add_user_exec1)
    adduser_result1=ip+" AddUser result1: "+os.popen(add_user_exec1).read()
    print(adduser_result1)

    print("AddUser exec: ", add_user_exec2)
    adduser_result2=ip+" AddUser result2: "+os.popen(add_user_exec2).read()
    print(adduser_result2)

    print("AddUser exec: ", add_user_exec3)
    adduser_result3=ip+" AddUser result3: "+os.popen(add_user_exec3).read()
    print(adduser_result3)

    result_history=[adduser_result1,adduser_result2,adduser_result3]
    WriteLog('result-history.log',result_history)

def Customize(ip, port, username, password):
    customize_exec1="./sshpass -p '{}' scp -P {} {} {}@{}:/tmp".format(password,port,customize_shell,username,ip)
    customize_exec2='''./sshpass -p '{}' ssh -p{} {}@{} "bash /tmp/{} '{}' '{}' '{}' " '''.format(password,port,username,ip,customize_shell,customize_shell_args, add_user, add_user_home)
    exec_history=[customize_exec1,customize_exec2]
    WriteLog('exec-history.log',exec_history)

    print("Customize exec: ", customize_exec1)
    customize_reult1=ip+" Customize result1: "+os.popen(customize_exec1).read()
    print(customize_reult1)

    print("Customize exec: ", customize_exec2)
    customize_reult2=ip+" Customize result2: "+os.popen(customize_exec2).read()
    print(customize_reult2)

    result_history=[customize_reult1,customize_reult2]
    WriteLog('result-history.log',result_history)


def WriteLog(log_file, log_list):
    with open (log_file, 'a') as f:
        for i in log_list:
            f.write(i+"\n")


def CheckSSH(ip, port, username, password):
    check_ssh_exec1="chmod +x sshpass"
    os.popen(check_ssh_exec1)
    check_ssh_exec2='''./sshpass -p '{}' ssh -p{} {}@{} "echo 'sshpass success' " '''.format(password,port,username,ip)
    print ("now ssh to "+ip)
    check_ssh_result=os.popen(check_ssh_exec2).read()
    time.sleep(1)
    with open ('check-ssh-result.log', 'a') as f:
        if 'sshpass success' in check_ssh_result:
            f.write(ip+" ssh success\n")
            return 0
        else:
            f.write(ip+" ssh failed\n")
            return 1

if __name__ == "__main__":
    ip_file = sys.argv[1]
    #now=time.strftime("%dday,%H:%M:%S")
    with open(ip_file, "r") as f:
        for line in f:
            if '#' in line.split()[0]:
                pass
            else:
                ip = line.split()[0]
                port=line.split()[1]
                username = line.split()[2]
                password = line.split()[3]
                if CheckSSH(ip, port, username, password) == 0:
                    #pass
                    Prepare(ip, port, username, password)
                    FileSYS(ip, port, username, password)
                    AddUser(ip, port, username, password)
                    Java(ip, port, username, password)
                    Customize(ip, port, username, password)