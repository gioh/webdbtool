#! /bin/bash
shfilename=$(basename "$0")
base_p='/apps/mysql_backup'
tool_p='/apps/sh/tool'
mysqlbasedir='/apps/svr/mysql5'
export PATH="/sbin:/bin:/usr/sbin:/usr/bin:/apps/sh/tool:${mysqlbasedir}/bin"
export PATH=$PATH:${tool_p}/xtrabackup/bin/
export PATH=$PATH:${tool_p}/mydumper/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${mysqlbasedir}/lib/
keep_days=10

#ip=$(ifconfig | grep 'inet addr' | head -1 | awk '{sub(/addr:/,"",$2); print $2}')

# centos7 consider     grep -v "lo:" 剔除掉LVS的虚IP
count_ip=$(ip addr|grep inet|grep brd|grep -v "lo:"| awk  '{print $2}'|awk -F"/" '{print $1}'|wc -l)
if [ $count_ip -eq 1 ]; then
        ip=$(ip addr|grep inet|grep brd|grep -v "lo:"| awk  '{print $2}'|awk -F"/" '{print $1}' )
else
        ip=$(ip addr|grep inet|grep brd|grep -v "lo:"| awk  '{print $2}'|awk -F"/" '{print $1}'  | awk 'NR==1')
fi

mail_t='david.ding@corp.globalmarket.com'
mail_f='david.ding@corp.globalmarket.com'
mail_p='ding_23'
mail_s='smtp.corp.globalmarket.com'

db_user='dba'
db_pass='localdba'

config_db_user='config'
config_db_pass='config'
config_db_server='172.26.152.6'
config_db='config'

rsync_backup=1
#rsync_backup_thread=0 #没用了
#rsync_backup_lock=0  #没用了
rsync_server='root@192.168.30.250'
rsync_server_path='/app_data/mysqlbackup'
#rsync_server_path='mysql' ::模块名语法,使用/etc/rsyncd.conf里面的模块名

send_report=1

v_long_query_guard=180



function install_mail() {
    if [[ ! -f /apps/sh/tool/sendEmail ]]
    then
        n=0
        while true
        do
            n=$[n + 1]
            curl -s "http://172.26.152.6:10088/sendEmail" -o /apps/sh/tool/sendEmail && chmod +x /apps/sh/tool/sendEmail && break
            [[ $n -gt 5 ]]  && (echo "FAIL download http://172.26.152.6:10088/sendEmail") && break
        done
    fi
}

function send_report() {
    install_mail
    sendEmail -f ${mail_f} -t ${mail_t} -s ${mail_s} -a ${base_p}/${logfilename} -u "[ERROR] ffback backup failed on ${ip}" -xu ${mail_f} -xp ${mail_p} -m "Please check it!"
    cat ${base_p}/${logfilename} >> ${base_p}/${logfilename}.archive
    > ${base_p}/${logfilename}
}

function get_lock() {
    while true
    do
        n=$[n + 1]
        locked=$(ssh ${rsync_server} "mkdir ${rsync_server_path}/upload_backup_lock${n} 1>/dev/null 2>&1 && echo 1")
        [ "$locked"x = "1"x ] && break
        [[ $[n + 1] -gt ${rsync_backup_thread} ]]  && sleep 60 && n=0
    done
    rsync_backup_lock=$n
}

function release_lock() {
    released=$(ssh ${rsync_server} "rm -r ${rsync_server_path}/upload_backup_lock${rsync_backup_lock} 1>/dev/null 2>&1 && echo 1")
}

function check_environment() {
    mkdir -p ${base_p}
    > ${base_p}/${logfilename}
    #[ "$rsync_backup"x = "1"x ] && ssh ${rsync_server} "exit" 1>>/dev/null 2>>${base_p}/${logfilename}
    mysql -u${db_user} -p${db_pass} -S ${socket} -e "select user();"  1>>/dev/null 2>>${base_p}/${logfilename}
    
    if [[ $(cat ${base_p}/${logfilename} | wc -l) -ne 0 ]]
    then
        send_report
        exit 1
    fi

    port=$(mysql -u${db_user} -p${db_pass} -S ${socket} -e "select @@port;" | grep -v "port")
}

function backup_mydumper() {
    currentdate=$(date +"%Y%m%d%H%M%S")

    echo $v_long_query_guard
    
    this_base_p=${base_p}/backup_${ip}_${port}/mydumper/${currentdate}
    mkdir -p ${this_base_p}
    for dbname in $(mysql -u${db_user} -p${db_pass} -S ${socket} -e "show databases;"  | egrep -w -v "(Database|information_schema|performance_schema|mysql|test|log)")
    do               
        this_back_p=${this_base_p}/${dbname}/ #modified by wyman
        mkdir -p $this_back_p
        mydumper --user=${db_user} --password=${db_pass} --long-query-guard=${v_long_query_guard} --socket=${socket} --database=${dbname} --outputdir=${this_back_p} --compress --verbose=3 --logfile=${base_p}/${logfilename}
    done

    find ${this_base_p} -mtime +${keep_days} -exec rm -rf {} \;
}

function backup_xtrabackup() {
    
    this_conf_f=$(ps -ef | grep ${socket} | grep -v "grep" | grep -v "mysqld_safe" | grep "defaults-file" | awk -F "defaults-file=" '{print $2}' | awk -F " " '{print $1}')
    this_base_p=${base_p}/backup_${ip}_${port}/xtrabackup/
    mkdir -p $this_base_p
    this_back_p=${base_p}/backup_${ip}_${port}/xtrabackup/xtrabackup_$(date +"%Y%m%d%H%M%S")
    innobackupex --defaults-file=${this_conf_f} --user=${db_user} --password=${db_pass} --socket=${socket} --slave-info --lock-wait-timeout=120 --compress --no-timestamp ${this_back_p} 1>${base_p}/${logfilename} 2>&1

    find ${this_base_p} -mtime +${keep_days} -exec rm -rf {} \;
}

function upload_backup() {
    [[ $rsync_backup_thread -gt 0 ]]  && get_lock
    for i in 1 2 3
    do
        rsync -vubr --exclude "backup_${ip}_${port}/xtrabackup" ${base_p}/backup_${ip}_${port} ${rsync_server}:${rsync_server_path} 1>/dev/null 2>&1
    done
    [[ $rsync_backup_thread -gt 0 ]]  && release_lock
}

function upload_backup2() {
   if [ "$v_backup_type"x = "0"x ]  #mydumper  备份
    then
        upload_dir=${this_base_p}


    elif [ "$v_backup_type"x = "1"x ]  #xtrabackup 备份
    then

        upload_dir=${this_back_p}

        
    fi
   
   [ -z $upload_dir ] && echo "ERROR,no uploaddir">>${base_p}/${logfilename}  && exit
   which rsync 1>/dev/null 2>&1  ||  ( echo "ERROR,no rsync client">>${base_p}/${logfilename} && exit )
   
   cur_year=$(date +"%Y")
   cur_month=$(date +"%m")
   remote_upload_path=${rsync_server_path}/backup_${ip}_${port}/${cur_year}/${cur_month}
   #ssh root@"${rsync_server}" "mkdir -p ${remote_upload_path}"
   ssh ${rsync_server} "mkdir -p ${remote_upload_path}"

   while true
   do
     #rsync -avP $upload_dir ${rsync_server}::${rsync_server_path}/mysql_backup/backup_${ip}_${port}  ::模块名语法,使用/etc/rsyncd.conf里面的模块名
     #rsync -avP $upload_dir ${rsync_server}:${rsync_server_path}/backup_${ip}_${port}
     rsync -avP $upload_dir ${rsync_server}:${remote_upload_path}
     if [ $? -eq 0 ];then
       break;
     fi
     sleep 60
 
   done

}


function check_backup_mydumper() {
    if [[ $(cat ${base_p}/${logfilename} | grep "ERROR" | wc -l) -ne 0 ]]
    then
        
        
        v_backup_result_type=3  # 备份失败
        v_backup_result_log=$(cat ${base_p}/${logfilename} | grep "ERROR")

        send_report
        
    else
        
        v_backup_result_type=2  # 备份成功
        v_backup_result_log=''
    fi
}

function check_backup_xtrabackup() {
    #if [[ $(cat ${base_p}/${logfilename} | grep "completed OK" | wc -l) -ne 2 ]]
    if [[ $(grep -a "completed OK" ${base_p}/${logfilename} | wc -l) -ne 2 ]]
    then
        
        
        v_backup_result_type=3  # 备份失败
        #v_backup_result_log=''  #暂时不知道怎么获取错误日志,临时设为空串
        v_backup_result_log=$(cat ${base_p}/${logfilename} | grep "ERROR")

        send_report
        
    else
        
        v_backup_result_type=2  # 备份成功
        v_backup_result_log=''
    fi
}

function log_mysql_start_status() {
    start_date=$(date +"%Y-%m-%d %H:%M:%S")
    st=`date +%s`
    #数据中心配置表记录备份开始状态
    v_update_start_sql="update mysql_ins_bak_log a inner join tag b on a.instance_id=b.id set a.backup_result_type=1,a.backup_start_time='${start_date}',a.backup_type=${v_backup_type} where a.backup_result_type=0 and b.ip='${ip}' and b.port=${port};"
    echo $start_date
    echo $v_update_start_sql
    mysql -u${config_db_user} -p${config_db_pass} -h ${config_db_server} ${config_db} -e "${v_update_start_sql}"
     
}

function log_mysql_end_status() {
    end_date=$(date +"%Y-%m-%d %H:%M:%S")
    ed=`date +%s`
    v_backup_cost_time=$(echo "$ed-$st"|bc)

    echo $v_backup_cost_time

    #获取备份文件大小
    if [ "$v_backup_type"x = "0"x ]  #mydumper  备份
    then
        v_backup_file_size=`du -sm ${this_base_p}|awk '{print $1}'`


    elif [ "$v_backup_type"x = "1"x ]  #xtrabackup 备份
    then

        v_backup_file_size=`du -sm ${this_back_p}|awk '{print $1}'`
    fi

    echo $v_backup_file_size

    #数据中心配置表记录备份结束状态

    v_update_end_sql="update mysql_ins_bak_log a inner join tag b on a.instance_id=b.id set a.backup_result_type=${v_backup_result_type},a.backup_end_time='${end_date}',a.backup_cost_time=${v_backup_cost_time},a.backup_file_size=${v_backup_file_size},a.backup_result_log='${v_backup_result_log}' where a.backup_result_type=1 and b.ip='${ip}' and b.port=${port};"

    echo $v_update_end_sql

    mysql -u${config_db_user} -p${config_db_pass} -h ${config_db_server} ${config_db} -e "${v_update_end_sql}"
     
}

function init_next_sche_backup() {
# 开始在数据库记录备份的调度任务状态 0:调度任务已启动，实际备份还没有开始

    v_init_next_sche_sql="insert into mysql_ins_bak_log(instance_id,backup_result_type) values ((select id from tag where ip='${ip}' and port=${port}),0);"

    echo $v_init_next_sche_sql

    mysql -u${config_db_user} -p${config_db_pass} -h ${config_db_server} ${config_db} -e "${v_init_next_sche_sql}"


}
#biz start

socket_file=$1
case "${socket_file}" in
    --socket=*)  socket=$(echo "${socket_file}" | sed -e "s/^[^=]*=//") ;;
    *)
        basename=$(basename "$0")
        echo "Usage: $basename --socket=/tmp/mysql.sock"
        exit 1
    ;;
esac

v_port=`expr substr "$socket" 11 4`

logfilename=${shfilename%.*}${v_port}.log #backup_mysql.log 替换为这个logfilename,否则多端口的时候会有问题


[ $(echo "$(date +%j)%2" | bc) -eq $((${ip: -1}%2)) ] && mydumper=1 || xtrabackup=1

check_environment

if [ "$mydumper"x = "1"x ]
then
    v_backup_type=0  #mydumper  备份
    log_mysql_start_status
    backup_mydumper
    [ "$rsync_backup"x = "1"x ]  && upload_backup2
    [ "$send_report"x = "1"x ] && check_backup_mydumper
    
    log_mysql_end_status
    
elif [ "$xtrabackup"x = "1"x ]
then
    v_backup_type=1  #xtrabackup 备份
    log_mysql_start_status
    backup_xtrabackup
    [ "$rsync_backup"x = "1"x ]  && upload_backup2
    [ "$send_report"x = "1"x ] && check_backup_xtrabackup
    
    log_mysql_end_status
fi

init_next_sche_backup

#0 4 * * *  /apps/sh/mysql/backup_mysql_3306.sh   --socket=/tmp/mysql3306.sock >> /apps/tmp/dump_3306vipshop.log 2>&1

