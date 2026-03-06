你是系統環境建置專家 

幫我寫個工作環境Workspace的 tcg_environment.md 建置規格書, 

讓claude 能自動幫我 git pull 
之後我能複製到其他電腦也能同時使用, mac 系統 不同用戶
環境有分 dev /sit , ip 有的還不確定 
幫我生成好的架構分類, 我是使用intelji


git pull: 

web 
git@github.com:tt-win/wps-console-web.git
git@github.com:tt-win/csp-console-web.git

java8
git@github.com:tt-win/wps-v1-module.git

java 11
git@github.com:tt-win/wps-console-v1-module.git


java21

git@github.com:tt-win/wps-console-module.git
git@github.com:tt-win/wps-core-module.git
git@github.com:tt-win/csp-console-v2.git
git@github.com:tt-win/csp-console-module.git
git@github.com:tt-win/wps-3rd-handler-module.git

sql:
git@github.com:tt-win/tcg-wps-fe-sql.git
git@github.com:tt-win/tcg-wps-console-sql.git


最後完成後幫我生成一份說明, 跟 skills 讓我之後也能使用
還有能查詢相關代碼的agent


我有一堆主機得連, 幫我設定主機專案環境, 專家都怎麼快速連線這些能排查
帳密是root 1qaz2wsx


dev
wps 10.80.0.34
wps-console-v1 10.80.0.45
wps core 10.80.0.58
csp push 10.80.0.58
nginx 10.80.0.39
csp console v2 10.80.0.58

sit
wps 10.80.1.32
wps-console-v1	10.80.1.31
wps console v2 1 10.80.1.53
wps console v2 2 10.80.1.55
wps 3rd 1 10.80.1.53
wps 3rd 2 10.80.1.55
nginx 10.80.1.34


etc/hosts , 工程師有時需要測試, 用什麼工具或者方式可以快速切換環境

dev:
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
######TCG-DEV-WSD02 START######
#COMMON HOSTS START #
10.80.0.9 TCG-DEV-REDIS01
10.80.0.41 TCG-DEV-REDIS02
10.80.0.42 TCG-DEV-REDIS03
10.80.0.10 TCG-DEV-KAFKA01
#COMMON HOSTS END #
######TCG-DEV-WSD02 END######


#### WRD PARTS START
10.80.0.10  TCG-KAFKA01 TCG-DEV-KAFKA01 TCG-KAFKA-CLUSTER01
10.80.0.59  TCG-WRD-RDS01
10.80.0.39  TCG-USS-AE TCG-USS-SE TCG-ACS01 TCG-CCS-ANNOUNCEMENT-FE
10.80.0.27  TCG-ACS01
10.80.0.39  TCG-WPS-CORE TCG-WPS-3RD TCG-CSP01
10.80.0.34  TCG-WPS-MIGRATE01
10.80.0.39  TCG-CONSOLE04
10.80.0.28  TCG-ODSFE01
10.80.0.30  TCG-GCS-GAME01
10.80.0.30  TCG-GLS02
10.80.0.39  TCG-GEOIP
10.80.0.39  TCG-MCS-FE
10.80.0.82  TCG-MRS-FE
10.80.0.21  TCG-MCS-CONSOLE
10.80.0.24  TCG-PROM-FE
10.80.0.39  TCG-PROM-21-FE
10.80.0.14  TCG-LOTTERY02
10.80.0.16  TCG-LGS-VN01
10.80.0.35  TCG-CBS01
10.80.0.29  TCG-CONSOLE01
10.80.0.29  TCG-MIS-CONSOLE01
10.80.0.39  TCG-WPS-CAMPAIGN-REDIRECT
10.80.0.39  TCG-EMD
#### WRD PARTS END




sit

127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
######TCG-SIT-WSD02 START######
#COMMON HOSTS START #
#COMMON HOSTS END #
######TCG-SIT-WSD02 END######


#### WRD PARTS START
10.80.1.7   TCG-KAFKA-F1
10.80.1.7   TCG-KAFKA01 TCG-SIT-KAFKA01 TCG-KAFKA-CLUSTER01
10.80.1.54  TCG-WRD-RDS01
10.80.1.34  TCG-USS-AE TCG-USS-SE TCG-ACS01 TCG-CCS-ANNOUNCEMENT-FE
10.80.1.34  TCG-WPS-CORE TCG-WPS-3RD TCG-CSP01
10.80.1.31  TCG-WPS-MIGRATE01
10.80.1.34  TCG-CONSOLE04
10.80.1.24  TCG-ODSFE01
10.80.1.27  TCG-GCS-GAME01
10.80.1.27  TCG-GLS02
10.80.1.34  TCG-GEOIP
10.80.1.34  TCG-MCS-FE
10.80.1.34  TCG-MRS-FE
10.80.1.17  TCG-MCS-CONSOLE
10.80.1.20  TCG-PROM-FE
10.80.1.34  TCG-PROM-21-FE
10.80.1.10  TCG-LOTTERY02
10.80.1.13  TCG-LGS-VN01
10.80.1.33  TCG-CBS01
10.80.1.25  TCG-CONSOLE01
10.80.1.25  TCG-MIS-CONSOLE01
10.80.1.34  TCG-WPS-CAMPAIGN-REDIRECT
10.80.1.34  TCG-EMD
#### WRD PARTS END



#### WRD PARTS START
10.80.1.7   TCG-KAFKA-F1
10.80.1.7   TCG-KAFKA01 TCG-SIT-KAFKA01 TCG-KAFKA-CLUSTER01
10.80.1.54  TCG-WRD-RDS01
10.80.1.34  TCG-USS-AE TCG-USS-SE TCG-ACS01 TCG-CCS-ANNOUNCEMENT-FE
10.80.1.34  TCG-WPS-CORE TCG-WPS-3RD TCG-CSP01
10.80.1.31  TCG-WPS-MIGRATE01
10.80.1.34  TCG-CONSOLE04
10.80.1.24  TCG-ODSFE01
10.80.1.27  TCG-GCS-GAME01
10.80.1.27  TCG-GLS02
10.80.1.34  TCG-GEOIP
10.80.1.34  TCG-MCS-FE
10.80.1.34  TCG-MRS-FE
10.80.1.17  TCG-MCS-CONSOLE
10.80.1.20  TCG-PROM-FE
10.80.1.34  TCG-PROM-21-FE
10.80.1.10  TCG-LOTTERY02
10.80.1.13  TCG-LGS-VN01
10.80.1.33  TCG-CBS01
10.80.1.25  TCG-CONSOLE01
10.80.1.25  TCG-MIS-CONSOLE01
10.80.1.34  TCG-EMD
#### WRD PARTS END

10.80.1.32 TCG-WPS09


看還有什麼補充的可以幫我補充到文件上, 可列出其他我需要安裝的工具, 我是java開發工程師, 也會碰到前端


