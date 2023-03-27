###
 # @Author: Athrun
 # @Email: erythron@outlook.com
 # @Date: 2022-12-10 10:22:22
 # @LastEditTime: 2023-03-27 10:29:23
 # @description: now it is null
###


selinux_conf="/etc/selinux/config"
sshd_conf="/etc/ssh/sshd_config"
ntp_conf="/etc/ntp.conf"
profile_file="/etc/profile"
limit_file="/etc/security/limits.conf"
resultSudo=`echo $1 | grep 'sudo'`
resultDns=`echo $1 | grep 'dns'`
resultPaas=`echo $1 | grep 'paas'`
resultUlimit=`echo $1 | grep 'ulimit'`
resultUmask=`echo $1 | grep 'umask'`
resultCron=`echo $1 | grep 'cron'`
resultHostKey=`echo $1 | grep 'hostkey'`
user=$2
home=$3

function sudoIssue {
  content=`sudo cat /etc/sudoers| grep "# Defaults secure_path"`
  if [[ -n $content ]] ;then
    sudo sed 's/# Defaults secure_path/Defaults secure_path/g' -i /etc/sudoers
  fi
}

function cleanDns {
  sudo cp /etc/resolv.conf /etc/resolv.conf.init-bak
  sudo sed 's/^/##&/g' -i /etc/resolv.conf
}

function selinuxOff {
    sudo sed -i "s/SELINUX=enforcing/SELINUX=disabled/g" $selinux_conf
    sudo setenforce 0
}

function iptablesOff {
    sudo systemctl stop firewalld.service
    sudo systemctl disable firewalld.service
    sudo iptables -F
}

function sshdConfig {
    sudo sed -i 's/^GSSAPIAuthentication yes$/GSSAPIAuthentication no/' $sshd_conf
    sudo sed -i 's/#UseDNS yes/UseDNS no/g' $sshd_conf
    sudo systemctl restart sshd
}

function ulimitConfig {
cat << EOF | sudo tee -a /etc/security/limits.conf
$user - nofile 65536
$user - nproc 4096
$user - fsize unlimited
$user - as unlimited
$user - memLock unlimited
EOF
}

function forPaas {
  mkdir /app/paas_deploy_data
  mkdir /app/paas_installation
  chown $user:$user /app/paas_*
}

function configUmask {
  content1=`sudo grep "umask" /root/.bashrc`
  content2=`sudo grep "umask" $home/.bashrc`
  if [ -z "${content1}" ] ;then
      echo 'umask 002' | sudo tee -a /root/.bashrc
  fi
  if [ -z "${content2}" ] ;then
      echo 'umask 022' | sudo tee -a $home/.bashrc
  fi
}

function configCron {
    content=`sudo grep "$user" /etc/cron.allow`
    if [ -z "${content}" ] ;then
        echo "$user" | sudo tee -a /etc/cron.allow
    fi
}

function hostKeyConfig {
  content=`grep "StrictHostKeyChecking" ~/.ssh/config`
  if [ -z "${content}" ] ;then
  cat << EOF | sudo tee -a ~/.ssh/config
Host *
  StrictHostKeyChecking no
EOF
  fi
}

if [[ -n $resultSudo ]] ;then
    echo 'info: exec sudoIssue'
    sudoIssue
fi

if [[ -n $resultDns ]] ;then
    echo 'info: exec cleanDns'
    cleanDns
fi

if [[ -n $resultPaas ]] ;then
    echo 'info: exec forPaas'
    umask
fi

if [[ -n $resultUlimit ]] ;then
    echo 'info: exec ulimitConfig'
    ulimitConfig
fi

if [[ -n $resultUmask ]] ;then
    echo 'info: exec Umask'
    configUmask
fi

if [[ -n $resultCron ]] ;then
    echo 'info: exec Cron'
    configCron
fi

if [[ -n $resultHostKey ]] ;then
    echo 'info: exec hostKeyConfig'
    hostKeyConfig
fi

selinuxOff
iptablesOff