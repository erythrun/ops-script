selinux_conf="/etc/selinux/config"
sshd_conf="/etc/ssh/sshd_config"
ntp_conf="/etc/ntp.conf"
profile_file="/etc/profile"
limit_file="/etc/security/limits.conf"

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
  content2=`sudo grep "umask" /home/$user/.bashrc`
  if [ -z "${content1}" ] ;then
      echo 'umask 002' | sudo tee -a /root/.bashrc
  fi
  if [ -z "${content2}" ] ;then
      echo 'umask 022' | sudo tee -a /home/$user/.bashrc
  fi
}


resultSudo=`echo $1 | grep 'sudo'`
resultDns=`echo $1 | grep 'dns'`
resultPaas=`echo $1 | grep 'paas'`
resultUlimit=`echo $1 | grep 'ulimit'`
resultUmask=`echo $1 | grep 'umask'`
user=$2


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


selinuxOff
iptablesOff
