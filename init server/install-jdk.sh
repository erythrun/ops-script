#! /bin/bash
###
 # @Author: Athrun
 # @Email: erythron@outlook.com
 # @Date: 2022-12-13 18:48:55
 # @LastEditTime: 2022-12-19 19:24:52
 # @description: bash install-jdk.sh "jdk-8u202-linux-x64.tar.gz" "jdk1.8.0_202"
###

function JDKInstall {
    content=`grep "export JAVA_HOME=/usr/local/$jdk_decompress" /etc/profile.d/java-init.sh`
    if [ -z "${content}" ] ;then
        sudo sh -c "echo export JAVA_HOME=/usr/local/$jdk_decompress >> /etc/profile.d/java-init.sh"
        sudo tar -xf /tmp/$jdk_package -C /usr/local/
        sudo chmod 775 -R /usr/local/$jdk_decompress
        #rm $jdk_package
    else
        echo "grep /etc/profile.d/java-init.sh, find export JAVA_HOME=/usr/local/$jdk_decompress"
    fi
    content=`grep "CLASSPATH=.:\$JAVA_HOME/jre/lib/rt.jar:\$JAVA_HOME/lib/dt.jar:\$JAVA_HOME/lib/tools.jar" /etc/profile.d/java-init.sh`
    if [ -z "${content}" ] ;then
        sudo sh -c "echo 'CLASSPATH=.:\$JAVA_HOME/jre/lib/rt.jar:\$JAVA_HOME/lib/dt.jar:\$JAVA_HOME/lib/tools.jar' >> /etc/profile.d/java-init.sh"
    else
        echo "grep /etc/profile.d/java-init.sh, find CLASSPATH=.:\$JAVA_HOME/jre/lib/rt.jar:\$JAVA_HOME/lib/dt.jar:\$JAVA_HOME/lib/tools.jar"
    fi
    content=`grep "export PATH=\$JAVA_HOME/bin:\$PATH" /etc/profile.d/java-init.sh`
    if [ -z "${content}" ] ;then
        sudo sh -c "echo 'export PATH=\$JAVA_HOME/bin:\$PATH' >> /etc/profile.d/java-init.sh"
    else
        echo "grep /etc/profile.d/java-init.sh, find export PATH=\$JAVA_HOME/bin:\$PATH"
    fi
    source /etc/profile.d/java-init.sh
    if [ -L /usr/bin/java ]; then
        echo "/usr/bin/java exists"
    else
        sudo ln -s /usr/local/$jdk_decompress/bin/java /usr/bin
    fi
}

#cd `dirname $0`
version=`java -version 2>&1`
echo $version | grep -q 'java version'
if [ $? -ne 0 ] ;then
    echo "jdk not install"
else
    echo "jdk installed"
    exit 0
fi

jdk_package=$1
jdk_decompress=$2

echo "begin install jdk"

if [[ -f /tmp/$jdk_package ]]; then
    JDKInstall
    sudo chmod 644 /etc/profile.d/java-init.sh
elif [[ -f $jdk_package ]]; then
    sudo cp $jdk_package /tmp/
    sleep 3
    JDKInstall
    sudo chmod 644 /etc/profile.d/java-init.sh
else
    echo "no file"
fi

