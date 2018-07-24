#!/bin/bash
echo -e "\033[32;49;1m ########################################## \033[39;49;0m"
read -p "请输入用户名: " user
egrep "^$user" /etc/passwd >& /dev/null  
if [ $? -ne 0 ]  
then  
    useradd $user
    if [ $? -eq 0 ]
    then
        echo "${user}用户添加成功!"
        num=1
        while [ $num -le 3 ] 
        do
            read -p "请输入密码===》" password1
            read -p "确认重复输入密码===》" password2
            if [ -z "$password1" ] & [ -z "$password2" ]
            then
                break;
            elif [ "${password1}" = "${password2}" ]
            then
                echo "$password1" |passwd --stdin $user
                break;
            fi
            let "num++"
        done
    else
        exit
    fi
else
    echo "${user}已经存在，请继续!"
    if [ ! -d "/home/${user}" ]; then
       mkdir /home/$user
       chown -R ${user}:${user} /home/$user
    fi
fi
setfacl -R -m u:nginx:rwx /home/$user
function create-file {
    mkdir -p /home/${user}/${1}/
    sed -e "s/user.${1}.test.com/${user}.${1}.test.com/" -e "s/\/home\/user\/${1}/\/home\/${user}\/${1}/" -e "s/\/data\/log\/2hz-nginx-${1}-access.log/\/home\/${user}\/logs\/${1}-access.log/" -e "s/\/data\/log\/2hz-nginx-${1}-error.log/\/home\/${user}\/logs\/${1}-error.log/" /etc/nginx/conf.d/2hz-${1}.conf > /etc/nginx/conf.d/${user}-2hz-${1}.conf
    setfacl -m u:${user}:rwx /etc/nginx/conf.d/${user}-2hz-${1}.conf
}

echo -e "\033[32;49;1m ########################################## \033[39;49;0m"
echo -e "\033[32;49;1m  请选择用户需要创建的项目  \033[39;49;0m"
echo -e "\033[32;49;1m    1-frontend             \033[39;49;0m"
echo -e "\033[32;49;1m    2-backend              \033[39;49;0m"
echo -e "\033[32;49;1m    3-h5                   \033[39;49;0m"
echo -e "\033[32;49;1m ######################################### \033[39;49;0m"
read -p "输入数字选择项目，可多选（输入错误信息则默认选择123）！ ===》" pro
case $pro in
    1) create-file frontend
    ;;
    2) create-file backend
    ;;
    3) create-file h5
    ;;
    12) create-file frontend
        create-file  backend
    ;;
    23) create-file backend
        create-file h5
    ;;
    13) create-file frontend
        create-file h5
    ;;
    *) create-file frontend
       create-file backend
       create-file h5
    ;;
esac
if [ ! -d "/home/${user}/logs" ]; then
    mkdir /home/${user}/logs
fi
echo "创建成功！"
echo -e "\033[32;49;1m ########################################## \033[39;49;0m"
