# TCG 開發環境建置說明

> 本文件供 Claude 或其他自動化工具讀取，用於在 macOS 上快速建置 TCG 開發環境。
> 適用於不同 Mac 使用者帳號，可複製到其他電腦使用。

---

## 0. 跨機器 / 跨用戶注意事項

本文件設計為可在不同 Mac、不同使用者帳號下使用。以下列出所有**會因用戶或環境而異**的項目，部署時需確認或替換：

### 因「macOS 使用者帳號」而異

| 項目 | 影響的設定 | 處理方式 |
|------|-----------|---------|
| Homebrew 路徑 | Apple Silicon: `/opt/homebrew/`<br>Intel Mac: `/usr/local/` | 用 `$(brew --prefix)` 動態取得 |
| Nginx cache 路徑 | `proxy_cache_path /Users/__USER__/...` | 部署時執行 `sed` 替換 `__USER__` |
| JDK 路徑 | `/Library/Java/JavaVirtualMachines/` 下的版本名稱 | 用 `brew install --cask zulu@{8,11,21}` 統一版本；若已有其他 JDK，用 `/usr/libexec/java_home -V` 確認實際路徑 |
| NVM 路徑 | `$(brew --prefix)/opt/nvm/nvm.sh` | 改用 `$(brew --prefix)` 而非寫死 `/opt/homebrew` |
| WebLogic 路徑 | `$HOME/Workspace/weblogic/wls1411-arm` | bash_profile 用 `$HOME` 動態解析；需從舊電腦複製整個 weblogic 目錄或重新安裝 |
| SSH Key | `~/.ssh/` 下的檔案 | 從舊電腦遷移（見第 7 章 SSH Key 遷移） |
| SSH alias | `mac="ssh chrishuang@ChrisdeMac-mini.local"` | 依實際用戶名修改 |

### 因「環境 (DEV / SIT)」而異

| 項目 | 說明 |
|------|------|
| `/etc/hosts` | 用 SwitchHosts 切換 DEV / SIT profile |
| Nginx upstream | `includes/tac.conf` 中的 upstream 指向，依需要註解/啟用 |
| SSH 連線主機 | DEV 網段 `10.80.0.x` / SIT 網段 `10.80.1.x` |

### 一鍵初始化腳本

部署到新電腦時，執行以下腳本自動處理所有用戶相關路徑：

```bash
#!/bin/bash
# tcg-env-init.sh — 新電腦環境初始化
# 用法：bash tcg-env-init.sh

set -e
BREW_PREFIX=$(brew --prefix)
CURRENT_USER=$(whoami)

echo "=== 初始化環境：使用者 $CURRENT_USER，Homebrew 路徑 $BREW_PREFIX ==="

# 1. 建立工作目錄
mkdir -p ~/Workspace/{web,java8,java11,java21,sql,weblogic,nginx-temp}
mkdir -p ~/bin

# 2. Nginx 配置 - 替換 __USER__
if [ -f "$BREW_PREFIX/etc/nginx/nginx.conf" ]; then
  sed -i '' "s/__USER__/$CURRENT_USER/g" "$BREW_PREFIX/etc/nginx/nginx.conf"
  echo "[OK] Nginx proxy_cache_path 已設定為 /Users/$CURRENT_USER/Workspace/nginx-temp"
fi

# 3. bash_profile 中的 NVM 路徑修正
if [ -f ~/.bash_profile ]; then
  sed -i '' "s|/opt/homebrew|$BREW_PREFIX|g" ~/.bash_profile
  echo "[OK] bash_profile Homebrew 路徑已修正為 $BREW_PREFIX"
fi

# 4. JDK 路徑確認
echo ""
echo "=== 已安裝的 JDK ==="
/usr/libexec/java_home -V 2>&1 || echo "尚未安裝 JDK"

# 5. SSH Key 權限修正
if [ -d ~/.ssh ]; then
  chmod 700 ~/.ssh
  chmod 600 ~/.ssh/id_rsa ~/.ssh/sjhuang.phi ~/.ssh/dev.root.tc168 2>/dev/null
  chmod 644 ~/.ssh/*.pub ~/.ssh/config 2>/dev/null
  echo "[OK] SSH 權限已修正"
fi

# 6. tcg-ssh.sh 安裝
if [ -f ~/bin/tcg-ssh.sh ]; then
  chmod +x ~/bin/tcg-ssh.sh
  echo "[OK] tcg-ssh.sh 已設定為可執行"
fi

echo ""
echo "=== 初始化完成 ==="
echo "請執行 source ~/.bash_profile 載入新設定"
```

---

## 1. 前置工具安裝

```bash
# Homebrew（macOS 套件管理）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Git
brew install git

# 多版本 Java（Zulu JDK，手動安裝）
brew install --cask zulu@8       # Java 8
brew install --cask zulu@11      # Java 11
brew install --cask zulu@21      # Java 21
# 安裝後 JDK 位於 /Library/Java/JavaVirtualMachines/zulu-{8,11,21}.jdk/

# Node.js（前端開發用，透過 nvm）
brew install nvm
mkdir -p ~/.nvm

# Maven（Java 建置工具，透過 Homebrew 統一管理）
brew install maven
# brew maven 預設安裝在 $(brew --prefix)/opt/maven
# mvn 指令自動在 $(brew --prefix)/bin/mvn

# MySQL Client
brew install mysql-client

# 其他常用工具
brew install gh                             # GitHub CLI
brew install --cask intellij-idea           # IntelliJ IDEA
brew install --cask switchhosts             # hosts 快速切換工具
brew install --cask postman                 # API 測試
brew install --cask dbeaver-community       # 資料庫管理
brew install --cask docker                  # Docker
brew install --cask lark                    # Lark（公司協作通訊）

# Node.js LTS
nvm install --lts
```

---

## 2. Shell 環境配置

### 2.1 `~/.bash_profile`

```bash
# ============================================
# Homebrew prefix（Apple Silicon: /opt/homebrew, Intel: /usr/local）
# ============================================
export BREW_PREFIX=$(brew --prefix 2>/dev/null || echo "/opt/homebrew")

# ============================================
# NVM
# ============================================
export NVM_DIR="$HOME/.nvm"
[ -s "$BREW_PREFIX/opt/nvm/nvm.sh" ] && \. "$BREW_PREFIX/opt/nvm/nvm.sh"
[ -s "$BREW_PREFIX/opt/nvm/etc/bash_completion.d/nvm" ] && \. "$BREW_PREFIX/opt/nvm/etc/bash_completion.d/nvm"

# ============================================
# Java 多版本設定
# 用 /usr/libexec/java_home 動態解析，不寫死版本號
# 如果找不到對應版本，fallback 到寫死路徑
# ============================================
export JAVA_8_HOME=$(/usr/libexec/java_home -v 1.8 2>/dev/null || echo "/Library/Java/JavaVirtualMachines/zulu-8.jdk/Contents/Home")
export JAVA_11_HOME=$(/usr/libexec/java_home -v 11 2>/dev/null || echo "/Library/Java/JavaVirtualMachines/zulu-11.jdk/Contents/Home")
export JAVA_21_HOME=$(/usr/libexec/java_home -v 21 2>/dev/null || echo "/Library/Java/JavaVirtualMachines/zulu-21.jdk/Contents/Home")

# 預設使用 Java 21
export JAVA_HOME=$JAVA_21_HOME
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/dt.jar:.

# JDK 快速切換 alias
alias jdk8='export JAVA_HOME=$JAVA_8_HOME && export PATH=$JAVA_HOME/bin:$PATH && java -version'
alias jdk11='export JAVA_HOME=$JAVA_11_HOME && export PATH=$JAVA_HOME/bin:$PATH && java -version'
alias jdk21='export JAVA_HOME=$JAVA_21_HOME && export PATH=$JAVA_HOME/bin:$PATH && java -version'

# ============================================
# WebLogic 14.1.1（Java 8 / Java 11 專案部署用）
# ============================================
export MW_HOME=$HOME/Workspace/weblogic/wls1411-arm
export ORACLE_HOME=$MW_HOME
export WL_HOME=$MW_HOME/wlserver

# WebLogic 快速指令
alias wl-start="$WL_HOME/../user_projects/domains/base_domain/startWebLogic.sh"
alias wl-stop="$WL_HOME/../user_projects/domains/base_domain/stopWebLogic.sh"

# ============================================
# Maven（Homebrew 管理，無需額外設定 PATH）
# ============================================
# brew install maven 後 mvn 已在 $(brew --prefix)/bin/mvn
# 如需自訂 settings.xml：~/.m2/settings.xml

# ============================================
# MySQL Client
# ============================================
export PATH="$BREW_PREFIX/opt/mysql-client/bin:$PATH"

# ============================================
# SSH 快速連線
# ============================================
alias ssh-sit-elk="ssh root@10.8.90.111"
alias m1="ssh macmini@172.20.168.31"
alias m2="ssh macmini@172.20.168.32"
alias m3="ssh macmini@172.20.168.33"
# alias mac="ssh <your-username>@<your-mac-hostname>.local"  # 依實際用戶名修改

# SSH 互動選單
alias ss="~/bin/tcg-ssh.sh"
```

### 2.2 `~/.zshrc`（追加到末尾）

```bash
# 載入 bash_profile
[ -f ~/.bash_profile ] && source ~/.bash_profile

# 重新載入設定
alias sourceb="source ~/.bash_profile"

# Kill process by port
killport() {
  if [ -z "$1" ]; then
    echo "Usage: killport <port>"
    return 1
  fi
  local pids=($(lsof -t -i:"$1"))
  if [ ${#pids[@]} -eq 0 ]; then
    echo "No process found on port $1"
    return 1
  fi
  kill -9 "${pids[@]}" && echo "Killed ${#pids[@]} process(es) on port $1"
}
```

---

## 3. 工作目錄結構

所有專案統一放在 `~/Workspace/` 下，依技術棧分類：

```
~/Workspace/
├── web/                        # 前端專案
│   ├── wps-console-web/
│   └── csp-console-web/
├── java8/                      # Java 8 專案（WebLogic 14 部署）
│   └── wps-v1-module/
├── java11/                     # Java 11 專案（WebLogic 14 部署）
│   └── wps-console-v1-module/
├── java21/                     # Java 21 專案（Spring Boot）
│   ├── wps-console-module/
│   ├── wps-core-module/
│   ├── csp-console-v2/
│   ├── csp-console-module/
│   └── wps-3rd-handler-module/
├── sql/                        # SQL 專案
│   ├── tcg-wps-fe-sql/
│   └── tcg-wps-console-sql/
├── weblogic/                   # WebLogic Server
│   └── wls1411-arm/            # WebLogic 14.1.1（Java 8 / 11 專案用）
└── nginx-temp/                 # Nginx proxy cache 目錄
```

---

## 4. Git Clone 全部專案

```bash
# 建立目錄結構
mkdir -p ~/Workspace/{web,java8,java11,java21,sql,weblogic,nginx-temp}

# === Web 前端 ===
git clone git@github.com:tt-win/wps-console-web.git   ~/Workspace/web/wps-console-web
git clone git@github.com:tt-win/csp-console-web.git   ~/Workspace/web/csp-console-web

# === Java 8 ===
git clone git@github.com:tt-win/wps-v1-module.git     ~/Workspace/java8/wps-v1-module

# === Java 11 ===
git clone git@github.com:tt-win/wps-console-v1-module.git  ~/Workspace/java11/wps-console-v1-module

# === Java 21 ===
git clone git@github.com:tt-win/wps-console-module.git     ~/Workspace/java21/wps-console-module
git clone git@github.com:tt-win/wps-core-module.git        ~/Workspace/java21/wps-core-module
git clone git@github.com:tt-win/csp-console-v2.git         ~/Workspace/java21/csp-console-v2
git clone git@github.com:tt-win/csp-console-module.git     ~/Workspace/java21/csp-console-module
git clone git@github.com:tt-win/wps-3rd-handler-module.git ~/Workspace/java21/wps-3rd-handler-module

# === SQL ===
git clone git@github.com:tt-win/tcg-wps-fe-sql.git        ~/Workspace/sql/tcg-wps-fe-sql
git clone git@github.com:tt-win/tcg-wps-console-sql.git    ~/Workspace/sql/tcg-wps-console-sql
```

---

## 5. Git Pull 全部專案（一鍵更新）

```bash
for dir in ~/Workspace/*/*; do
  if [ -d "$dir/.git" ]; then
    echo "=== Pulling: $dir ==="
    git -C "$dir" pull --rebase
  fi
done
```

---

## 6. WebLogic 14.1.1 安裝（Java 8 / 11 專案用）

Java 8 (`wps-v1-module`) 和 Java 11 (`wps-console-v1-module`) 專案使用 WebLogic 作為 Application Server（JAX-RS 部署），Java 21 專案則用 Spring Boot，不需要 WebLogic。

### 6.1 安裝方式

WebLogic 無法透過 brew 安裝，需手動安裝或從舊電腦複製。

**方式一：從舊電腦複製（推薦）**

```bash
# 在舊電腦上打包
tar czf ~/Desktop/weblogic-backup.tar.gz -C ~/Workspace weblogic/

# 在新電腦上還原
mkdir -p ~/Workspace/weblogic
tar xzf ~/Desktop/weblogic-backup.tar.gz -C ~/Workspace/

# 修正 domain 內的絕對路徑（WebLogic domain 設定會寫死使用者路徑）
WL_DOMAIN=$HOME/Workspace/weblogic/wls1411-arm/user_projects/domains/base_domain
if [ -d "$WL_DOMAIN" ]; then
  # 替換舊使用者路徑為新使用者路徑
  find "$WL_DOMAIN" -type f \( -name "*.xml" -o -name "*.properties" -o -name "*.sh" -o -name "*.cmd" \) \
    -exec sed -i '' "s|/Users/[a-zA-Z0-9_-]*/Workspace/weblogic|$HOME/Workspace/weblogic|g" {} +
  echo "[OK] WebLogic domain 路徑已修正為 $HOME/Workspace/weblogic"
fi
```

**方式二：全新安裝**

```bash
# 1. 從 Oracle 官網下載 WebLogic 14.1.1 Generic Installer
#    https://www.oracle.com/middleware/technologies/weblogic-server-installers-downloads.html
# 2. 使用 Java 11 執行安裝（WebLogic 14 需要 Java 11）
jdk11
java -jar fmw_14.1.1.0.0_wls_lite_generic.jar

# 安裝目錄選擇：~/Workspace/weblogic/wls1411-arm
# 3. 建立 domain
cd ~/Workspace/weblogic/wls1411-arm/oracle_common/common/bin
./wlst.sh
# WLST 中執行：
# readTemplate('/Users/<your-user>/Workspace/weblogic/wls1411-arm/wlserver/common/templates/wls/wls.jar')
# cd('Servers/AdminServer')
# set('ListenPort', 7001)
# writeDomain('/Users/<your-user>/Workspace/weblogic/wls1411-arm/user_projects/domains/base_domain')
# closeTemplate()
# exit()
```

### 6.2 WebLogic 環境變數（已含在 bash_profile 中）

```bash
export MW_HOME=$HOME/Workspace/weblogic/wls1411-arm
export ORACLE_HOME=$MW_HOME
export WL_HOME=$MW_HOME/wlserver
```

### 6.3 WebLogic 常用指令

```bash
wl-start     # 啟動 WebLogic（alias）
wl-stop      # 停止 WebLogic（alias）

# 手動啟動/停止
$WL_HOME/../user_projects/domains/base_domain/startWebLogic.sh
$WL_HOME/../user_projects/domains/base_domain/stopWebLogic.sh

# 管理控制台
# http://localhost:7001/console
```

### 6.4 專案部署對照

| 專案 | Java 版本 | 部署方式 | Port |
|------|-----------|---------|------|
| wps-v1-module | 8 | WebLogic WAR 部署 | 7001 |
| wps-console-v1-module | 11 | WebLogic WAR 部署 | 7001 |
| wps-core-module | 21 | Spring Boot 獨立運行 | - |
| wps-console-module | 21 | Spring Boot 獨立運行 | - |
| wps-3rd-handler-module | 21 | Spring Boot 獨立運行 | - |
| csp-console-v2 | 21 | Spring Boot 獨立運行 | 9002 |

> **跨用戶注意**：WebLogic domain 設定檔（`config.xml`、`startWebLogic.sh` 等）會寫死絕對路徑。
> 從舊電腦複製後，務必用上面的 `sed` 指令替換路徑，否則啟動會失敗。

---

## 7. Nginx 配置（Homebrew）

```bash
brew install nginx
```

Nginx 配置路徑：`$(brew --prefix)/etc/nginx/`
Cache 目錄：`~/Workspace/nginx-temp/`

### 7.1 安裝 Nginx 配置

> **注意**：`nginx.conf` 中的 `proxy_cache_path` 包含使用者家目錄路徑，不同 Mac 帳號需替換。
> 以下指令會自動將 `__USER__` 替換為當前使用者名稱。

```bash
NGINX_DIR=$(brew --prefix)/etc/nginx

# 備份原始設定
cp "$NGINX_DIR/nginx.conf" "$NGINX_DIR/nginx.conf.default.bak"

# 建立 includes 目錄
mkdir -p "$NGINX_DIR/includes"

# 建立 cache 目錄
mkdir -p ~/Workspace/nginx-temp

# 將本文件 6.2 的內容寫入 nginx.conf、6.3 的內容寫入 includes/tac.conf 後
# 替換 __USER__ 為當前使用者
sed -i '' "s/__USER__/$(whoami)/g" "$NGINX_DIR/nginx.conf"

# 驗證
grep proxy_cache_path "$NGINX_DIR/nginx.conf"
```

### 7.2 主設定 `$(brew --prefix)/etc/nginx/nginx.conf`

```nginx
#user  nobody;

worker_processes  1;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}

http {
include includes/*.conf;
    include       mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

log_format host_log '$remote_addr - $remote_user [$time_local] "$request" '
                    'to "$proxy_host$request_uri" '
                    'status=$status upstream=$upstream_addr '
                    'response_time=$upstream_response_time';


    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;

    proxy_cache_path /Users/__USER__/Workspace/nginx-temp levels=1:2 keys_zone=backcache:8m max_size=256m inactive=60m;
    proxy_headers_hash_max_size 2048;
    proxy_headers_hash_bucket_size 256;


    server {
        listen       80;
        server_name  localhost;

        proxy_set_header Host $host:$server_port;
        proxy_set_header Proxy-Client-IP $http_x_real_ip;
        proxy_set_header X-Forwarded-For $http_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        #proxy_intercept_errors    on;
        #proxy_next_upstream     error timeout invalid_header;
        proxy_connect_timeout   2;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        #location / {
        #    root   html;
        #    index  index.html index.htm;
        #}


       #location /tac/api/ 測試修改為 tac-test-api

       location /tac/api/ {
          add_header X-Debug-Proxy-URI "$proxy_host$request_uri";
          add_header Access-Control-Allow-Methods 'GET, POST, DELETE, PUT, OPTIONS';

          if ($request_method = OPTIONS ) {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods 'GET, POST, DELETE, PUT, OPTIONS';
            add_header Access-Control-Allow-Headers 'Authorization, Content-Type, Accept, environment, platform, Merchant, language, MerchantCode, Tac-Trace-Id';

            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }

            proxy_pass http://sit-admin2.tcg.com/tac/api/;
            proxy_http_version 1.1;
            proxy_set_header Host sit-admin2.tcg.com;
#            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            proxy_set_header Authorization $http_authorization;
            proxy_set_header Content-Type $http_content_type;
            proxy_set_header Content-Length $http_content_length;


            add_header Access-Control-Allow-Origin *;
            client_max_body_size 50M;
        }


        location /{
            proxy_pass http://localhost:8080;
           location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
            proxy_cache backcache;
            proxy_cache_bypass $http_cache_control;
            expires 8h;
            add_header Cache-Control "public";
            proxy_pass http://localhost:8080;
           }
        }

        location /tac/ {
            proxy_pass http://10.8.95.18:7001/tcg-admin/resources/;
            location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
                proxy_cache backcache;
                proxy_cache_bypass $http_cache_control;
                expires 8h;
                add_header Cache-Control "public";
                #add_header X-Proxy-Cache $upstream_cache_status;
                proxy_pass http://10.8.95.29:7001;
            }
        }


        location /rtmsg {
#        proxy_pass http://TCG-IMSBO01:7001/imbo-gateway-service/rtmsg/web;
#            proxy_http_version 1.1;
#            proxy_set_header Upgrade $http_upgrade;
#            proxy_set_header Connection "upgrade";
#            add_header X-Frame-Options "SAMEORIGIN";
        }


#       location /adminconsole/ {
#           proxy_pass http://localhost:7001;
#           location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
#           proxy_cache backcache;
#           proxy_cache_bypass $http_cache_control;
#           expires 8h;
#           add_header Cache-Control "public";
#           #add_header X-Proxy-Cache $upstream_cache_status;
#
#           proxy_pass http://localhost:7001;
#
#       }
#   }


        location /wps-console/sse/{
    #  proxy_pass http://10.8.95.28:7001/wps-console-service/resources/sse/;
        proxy_pass http://0.8.90.44:7001/wps-console-service/resources/sse/;
#       proxy_pass http://localhost:7001/wps-console-service/resources/sse/;

            proxy_pass_header Server;
            proxy_set_header Connection Keep-Alive;
            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
            proxy_set_header Host TCG-GW01:7001;
            proxy_set_header Accept 'text/event-stream';

        location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
                proxy_cache backcache;
                proxy_cache_bypass $http_cache_control;
                expires 8h;
                add_header Cache-Control "public";
                #add_header X-Proxy-Cache $upstream_cache_status;
                proxy_pass http://127.0.0.1:88;
        }
    }




        location /wps-console/{
   #    proxy_pass http://10.8.95.28:7001/wps-console-service/resources/;
      proxy_pass http://localhost:7001/wps-console-service/resources/;
      #  proxy_pass http://10.8.90.44:7001/wps-console-service/resources/;
            proxy_pass_header Server;
            proxy_http_version 1.1;
            proxy_set_header Connection Keep-Alive;
            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
            proxy_set_header Host TCG-GW01:7001;
            proxy_set_header Accept 'application/json;v=3';

        location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
                proxy_cache backcache;
                proxy_cache_bypass $http_cache_control;
                expires 8h;
                add_header Cache-Control "public";
                #add_header X-Proxy-Cache $upstream_cache_status;
                proxy_pass http://127.0.0.1:88;
        }
    }


    location /csp-console/{
#       proxy_pass http://10.8.95.28:7001/csp-console/resources/;
#       proxy_pass http://localhost:7001/csp-console/;
       proxy_pass http://localhost:9002/csp-console-v2/;

#            proxy_pass_header Server;
#            proxy_http_version 1.1;
#            proxy_set_header Connection Keep-Alive;
#            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
#            proxy_set_header Host TCG-GW01:7001;
#            proxy_set_header Accept 'application/json;v=3';

        location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
                proxy_cache backcache;
                proxy_cache_bypass $http_cache_control;
                expires 8h;
                add_header Cache-Control "public";
                #add_header X-Proxy-Cache $upstream_cache_status;
                proxy_pass http://127.0.0.1:88;
        }
    }


    location /csp-console-v2/{
#       proxy_pass http://10.8.95.28:7001/csp-console/resources/;
       proxy_pass http://localhost:9002/csp-console-v2/;

        add_header X-Debug-Proxy-URI "$proxy_host$request_uri";
          add_header Access-Control-Allow-Methods 'GET, POST, DELETE, PUT, OPTIONS';

          if ($request_method = OPTIONS ) {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods 'GET, POST, DELETE, PUT, OPTIONS';
            add_header Access-Control-Allow-Headers 'Authorization, Content-Type, Accept, environment, platform, Merchant, language, MerchantCode, Tac-Trace-Id';

            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }



            proxy_pass_header Server;
            proxy_http_version 1.1;
            proxy_set_header Connection Keep-Alive;
            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
            proxy_set_header Host TCG-GW01:7001;
            proxy_set_header Accept 'application/json;v=3';
            client_max_body_size 50M;

        location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
                proxy_cache backcache;
                proxy_cache_bypass $http_cache_control;
                expires 8h;
                add_header Cache-Control "public";
                #add_header X-Proxy-Cache $upstream_cache_status;
                proxy_pass http://127.0.0.1:88;
        }
    }



    location /wps-console-web/{
    proxy_pass http://localhost:8081/;
    }
    location /wps-console-web{
        proxy_pass http://localhost:8081;
        location ~* \.(?:css|js|swf|png|jpg|jpeg|gif|ico)$ {
            proxy_cache backcache;
            proxy_cache_bypass $http_cache_control;
            expires 8h;
            add_header Cache-Control "public";
            proxy_pass http://localhost:9000;
        }
    }


        #THIS IS FOR PAYMENT CONSOLE UI
        location /ps-ops-mgmt/ {
                proxy_buffering off;
                proxy_set_header Console "OMC";
                proxy_pass http://localhost:7001/payment-system-mgmt-console/resources/;
        }


        location /ps-mer-mgmt/ {
                proxy_buffering off;
                proxy_set_header Console "MMC";
                proxy_pass http://localhost:7001/payment-system-mgmt-console/resources/;
        }


        location /ps-merchant-console/ {
            proxy_buffering off;
                proxy_pass http://localhost:7001/payment-system-merchant-console/;
        }




        location /tac  {
            proxy_pass http://10.8.90.15:7001/tcg-admin/resources;
#           proxy_pass http://localhost:7001/tcg-admin/resources;
#           proxy_pass http://10.8.95.29:7001/tcg-admin/resources;
        }


        location /tac/tac.global.css     {
            proxy_pass http://localhost:8080/tac.global.css;
        #   proxy_pass http://sit-admin.tcg.com/tac/tac.global.css;

            if ($mobile_rewrite = perform) { rewrite ^.+ http://$host/tac/m/bundle.css last;}
        }

        location /tac/m/bundle.css   {
            proxy_pass http://10.8.90.15:7001/tcg-admin/dist/m/bundle.css;
        }

#        location /wps-console {
#            proxy_pass http://10.8.95.28:7001/wps-console-service/resources;
#            #proxy_pass http://localhost:7001/wps-console-service/resources;
#        }

        location /wps-console-v3/ {
            if ($request_method = OPTIONS ) {
                add_header Access-Control-Allow-Origin *;
                add_header Access-Control-Allow-Methods 'GET, POST, DELETE, PUT, OPTIONS';
                add_header Access-Control-Allow-Headers 'Authorization, Content-Type, Accept, environment, platform, Merchant, language, MerchantCode, Tac-Trace-Id';

                add_header Content-Length 0;
                add_header Content-Type text/plain;
                return 204;
            }
            proxy_pass http://sit-admin2.tcg.com/;
            #proxy_pass http://10.80.1.39:7001/wps-console/;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header Proxy-Client-IP $http_x_real_ip;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Real-IP $remote_addr;

            # proxy_connect_timeout       600;
            proxy_send_timeout          600;
            proxy_read_timeout          600;
            # send_timeout                600;
            client_max_body_size 50M;
        }




        location /csp-console {
            #proxy_pass http://10.8.95.28:7001/csp-console/resources;
            proxy_pass http://localhost:7001/csp-console;
        }


        #location /wps-console-web/ {
        #   rewrite /localhost:8081/(.*) /$1  break;
        #   proxy_pass http://WPS-CONSOLE-WEB/;
        #}

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

    }

}
```

### 7.3 Upstream 設定 `$(brew --prefix)/etc/nginx/includes/tac.conf`

```nginx
upstream TAC-WEB {
    server localhost:8080;
}

upstream TAC-SERVER {
    server 10.8.95.29:7001;
	#server localhost:7001;
}

upstream WPS-CONSOLE-WEB {
    server localhost:8081;
}

upstream WPS-CONSOLE {
    server localhost:7001;
  # server 10.80.1.39:7001;
     # server 10.8.90.44:7001;
}

upstream CSP-CONSOLE-WEB {
    server localhost:8082;
}

upstream CSP-CONSOLE {
    server localhost:7001;
  #  server 10.8.95.28:7001;
}

server {
    listen       8000;
    server_name  _;

    proxy_connect_timeout 2;

    access_log  tac.access.log;
    error_log   tac.error.log;

    gzip  on;
    gzip_static on;
    gzip_min_length  1k;
    gzip_http_version 1.1;
    gzip_comp_level 6;
    gzip_proxied  any;
    gzip_buffers     16 8k;
    gzip_disable "MSIE [1-6].(?!.*SV1)";
    gzip_types
        text/plain
        text/css
        text/js
        text/xml
        text/javascript
        image/svg+xml svg svgz
        application/javascript
        application/json
        application/x-javascript
        application/xml
        application/xml+rss;
    gzip_vary         on;
    if ($http_user_agent ~* "(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino") {
        set $mobile_rewrite perform;
    }
    if ($http_user_agent ~* "^(1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-)") {
        set $mobile_rewrite perform;
    }

    location /tac    {
#        proxy_pass http://TAC-SERVER/tcg-admin/resources;
    }

    location /tac/tac.global.css     {
 #      proxy_pass http://TAC-WEB/tac.global.css;
 #       if ($mobile_rewrite = perform) { rewrite ^.+ http://$host/tac/m/bundle.css last;}

    }

    location /tac/m/bundle.css   {
   #     proxy_pass http://TAC-SERVER/tcg-admin/dist/m/bundle.css;
    }

    location /wps-console {
        proxy_pass http://WPS-CONSOLE/wps-console-service/resources;
    }

    location /wps-console-v2 {
        proxy_pass http://WPS-CONSOLE/wps-console;
    }

    location /wps-console-web/ {
        rewrite /wps-console-web/(.*) /$1  break;
        proxy_pass http://WPS-CONSOLE-WEB/;
    }

	location /csp-console {
		#proxy_pass http://CSP-CONSOLE/csp-console;
        proxy_pass http://10.80.1.53:9002/csp-console-v2;

	}


	location /csp-console-web/ {
	  rewrite /csp-console-web/(.*) /$1  break;
	  proxy_pass http://CSP-CONSOLE-WEB/;
	}

}
```

### 7.4 Nginx 常用指令

```bash
# 啟動
sudo nginx

# 停止
sudo nginx -s stop

# 重載設定（不中斷服務）
sudo nginx -s reload

# 測試設定檔語法
sudo nginx -t
```

---

## 8. SSH 遠端主機設定

`~/.ssh/config` 基礎配置（SSH Key 對應規則）：

```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/sjhuang.phi

Host codelab.tcg.local
    HostKeyAlgorithms +ssh-rsa
    PubkeyAcceptedKeyTypes +ssh-rsa

Host gitlab.tcg.com
    HostKeyAlgorithms +ssh-rsa
    PubkeyAcceptedKeyTypes +ssh-rsa

Host 10.*
    HostKeyAlgorithms +ssh-rsa,ssh-dss

Host 10.8.90.* 10.8.95.*
    HostkeyAlgorithms +ssh-rsa
    PubkeyAcceptedAlgorithms +ssh-rsa
    IdentitiesOnly yes
    IdentityFile ~/.ssh/id_rsa

Host 10.80.*
    AddKeysToAgent yes
    UseKeychain yes
    User root
    IdentityFile ~/.ssh/dev.root.tc168
```

> 以上為基礎配置，DEV/SIT 主機直接用 IP 連線即可（`ssh 10.80.0.34`），`10.80.*` 規則會自動套用 root + dev.root.tc168 key。
> 如需 Host 別名（如 `ssh dev-wps`），使用者可自行追加。

### SSH Key 遷移（從舊電腦搬到新電腦）

舊電腦上需要遷移的 SSH Key 檔案：

| 檔案 | 用途 |
|------|------|
| `~/.ssh/config` | SSH 連線設定（GitHub、GitLab、DEV/SIT 主機規則） |
| `~/.ssh/sjhuang.phi` + `.pub` | GitHub SSH Key |
| `~/.ssh/id_rsa` + `.pub` | 舊環境主機 (10.8.x) SSH Key |
| `~/.ssh/dev.root.tc168` | DEV/SIT 主機 (10.80.x) SSH Key |
| `~/.ssh/known_hosts` | 已知主機指紋 |

**在舊電腦上執行（打包 SSH 資料夾）：**

```bash
# 備份整個 .ssh 目錄（排除 .DS_Store）
tar czf ~/Desktop/ssh_backup.tar.gz -C ~ --exclude='.DS_Store' .ssh/
```

**在新電腦上執行（還原，保留原有資料）：**

```bash
# 先備份新電腦上現有的 .ssh（如果有的話）
[ -d ~/.ssh ] && cp -r ~/.ssh ~/.ssh.bak.$(date +%Y%m%d)

# 從舊電腦複製過來的 ssh_backup.tar.gz 解壓（合併，不覆蓋已有檔案）
cd ~
tar xzf ~/Desktop/ssh_backup.tar.gz --keep-old-files 2>/dev/null

# 如果要強制覆蓋（用舊電腦的設定為主）：
# tar xzf ~/Desktop/ssh_backup.tar.gz

# 修正權限（必須）
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa ~/.ssh/sjhuang.phi ~/.ssh/dev.root.tc168
chmod 644 ~/.ssh/*.pub ~/.ssh/config
```

**SSH config 中的規則說明：**

```
# GitHub → 使用 sjhuang.phi key
Host github.com → IdentityFile ~/.ssh/sjhuang.phi

# 舊環境 10.8.x → 使用 id_rsa key
Host 10.8.90.* 10.8.95.* → IdentityFile ~/.ssh/id_rsa

# DEV/SIT 10.80.x → 使用 dev.root.tc168 key，自動 root 登入
Host 10.80.* → IdentityFile ~/.ssh/dev.root.tc168, User root
```

> **注意**：`ssh_backup.tar.gz` 包含私鑰，遷移完成後請刪除，切勿上傳到 GitHub 或任何公開位置。

---

## 9. Hosts 環境切換（SwitchHosts）

安裝 SwitchHosts 後，建立兩組 hosts profile：

### Profile: TCG-DEV
```
######TCG-DEV START######
10.80.0.9   TCG-DEV-REDIS01
10.80.0.41  TCG-DEV-REDIS02
10.80.0.42  TCG-DEV-REDIS03
10.80.0.10  TCG-DEV-KAFKA01
10.80.0.10  TCG-KAFKA01 TCG-KAFKA-CLUSTER01
10.80.0.59  TCG-WRD-RDS01
10.80.0.39  TCG-USS-AE TCG-USS-SE TCG-ACS01 TCG-CCS-ANNOUNCEMENT-FE
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
######TCG-DEV END######
```

### Profile: TCG-SIT
```
######TCG-SIT START######
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
10.80.1.32  TCG-WPS09
######TCG-SIT END######
```

---

## 10. IntelliJ IDEA 設定建議

### 多 JDK 設定
1. `File > Project Structure > SDKs` 分別加入 Java 8、11、21
2. 各專案設定對應 SDK：
   - `java8/*` → Java 8
   - `java11/*` → Java 11
   - `java21/*` → Java 21

### 建議安裝的 Plugin
- Lombok
- MapStruct Support
- Maven Helper
- Key Promoter X
- .env files support
- GitToolBox

---

## 11. 快速參考表

### 專案 ↔ Java 版本 ↔ 環境對照

| 專案 | Java | App Server | DEV 主機 | SIT 主機 |
|------|------|-----------|----------|----------|
| wps-v1-module | 8 | WebLogic 14 | 10.80.0.34 | 10.80.1.32 |
| wps-console-v1-module | 11 | WebLogic 14 | 10.80.0.45 | 10.80.1.31 |
| wps-core-module | 21 | Spring Boot | 10.80.0.58 | - |
| wps-console-module | 21 | Spring Boot | - | 10.80.1.53 / .55 |
| wps-3rd-handler-module | 21 | Spring Boot | 10.80.0.58 | 10.80.1.53 / .55 |
| csp-console-v2 | 21 | Spring Boot | 10.80.0.58 | - |
| nginx (前端) | - | - | 10.80.0.39 | 10.80.1.34 |

### JDK 切換

```bash
jdk8    # 切換到 Java 8，自動顯示版本
jdk11   # 切換到 Java 11
jdk21   # 切換到 Java 21（預設）
```

### SSH 快速連線

```bash
# 直接用 IP（10.80.* 自動套用 root + key）
ssh 10.80.0.34           # DEV WPS (V1)
ssh 10.80.0.58           # DEV WPS Core / CSP
ssh 10.80.0.39           # DEV Nginx
ssh 10.80.1.32           # SIT WPS (V1)
ssh 10.80.1.31           # SIT Console V1
ssh 10.80.1.53           # SIT Console V2 節點1
ssh 10.80.1.34           # SIT Nginx

# 或用互動選單
ss                       # 叫出 tcg-ssh.sh 選單
```

### SSH 互動選單腳本 `~/bin/tcg-ssh.sh`

將以下腳本存為 `~/bin/tcg-ssh.sh` 並加入 alias，即可用選單快速連線。

```bash
mkdir -p ~/bin
```

```bash
#!/bin/bash
# TCG SSH 互動選單
# 用法：tcg-ssh 或直接輸入 ss（alias）

BLUE='\033[1;34m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}       TCG SSH 快速連線選單${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}  ── DEV 環境 ──${NC}"
echo -e "  ${CYAN}1)${NC}  dev-wps              (10.80.0.34)  WPS V1"
echo -e "  ${CYAN}2)${NC}  dev-wps-console-v1   (10.80.0.45)  WPS Console V1"
echo -e "  ${CYAN}3)${NC}  dev-wps-core         (10.80.0.58)  WPS Core"
echo -e "  ${CYAN}4)${NC}  dev-csp-push         (10.80.0.58)  CSP Push"
echo -e "  ${CYAN}5)${NC}  dev-csp-console-v2   (10.80.0.58)  CSP Console V2"
echo -e "  ${CYAN}6)${NC}  dev-nginx            (10.80.0.39)  Nginx"
echo ""
echo -e "${YELLOW}  ── SIT 環境 ──${NC}"
echo -e "  ${CYAN}7)${NC}  sit-wps              (10.80.1.32)  WPS V1"
echo -e "  ${CYAN}8)${NC}  sit-wps-console-v1   (10.80.1.31)  WPS Console V1"
echo -e "  ${CYAN}9)${NC}  sit-wps-console-v2-1 (10.80.1.53)  Console V2 節點1"
echo -e "  ${CYAN}10)${NC} sit-wps-console-v2-2 (10.80.1.55)  Console V2 節點2"
echo -e "  ${CYAN}11)${NC} sit-wps-3rd-1        (10.80.1.53)  3rd Handler 節點1"
echo -e "  ${CYAN}12)${NC} sit-wps-3rd-2        (10.80.1.55)  3rd Handler 節點2"
echo -e "  ${CYAN}13)${NC} sit-nginx            (10.80.1.34)  Nginx"
echo ""
echo -e "  ${CYAN}14)${NC} ssh-sit-elk          (10.8.90.111) ELK"
echo -e "  ${CYAN}15)${NC} m1 (Mac mini 1)      (172.20.168.31)"
echo -e "  ${CYAN}16)${NC} m2 (Mac mini 2)      (172.20.168.32)"
echo -e "  ${CYAN}17)${NC} m3 (Mac mini 3)      (172.20.168.33)"
echo ""
echo -e "  ${CYAN}0)${NC}  離開"
echo ""
echo -e "${BLUE}========================================${NC}"
read -p "請選擇 [0-17]: " choice

case $choice in
  1)  ssh 10.80.0.34 ;;
  2)  ssh 10.80.0.45 ;;
  3)  ssh 10.80.0.58 ;;
  4)  ssh 10.80.0.58 ;;
  5)  ssh 10.80.0.58 ;;
  6)  ssh 10.80.0.39 ;;
  7)  ssh 10.80.1.32 ;;
  8)  ssh 10.80.1.31 ;;
  9)  ssh 10.80.1.53 ;;
  10) ssh 10.80.1.55 ;;
  11) ssh 10.80.1.53 ;;
  12) ssh 10.80.1.55 ;;
  13) ssh 10.80.1.34 ;;
  14) ssh root@10.8.90.111 ;;
  15) ssh macmini@172.20.168.31 ;;
  16) ssh macmini@172.20.168.32 ;;
  17) ssh macmini@172.20.168.33 ;;
  0)  echo "Bye!" ; exit 0 ;;
  *)  echo "無效選項" ; exit 1 ;;
esac
```

**安裝方式：**

```bash
# 建立腳本
mkdir -p ~/bin
# （將上述內容寫入 ~/bin/tcg-ssh.sh）
chmod +x ~/bin/tcg-ssh.sh

# 在 ~/.bash_profile 加入 alias
alias ss="~/bin/tcg-ssh.sh"
```

使用時只要在終端輸入 `ss`，就會出現互動選單讓你選擇要連哪台主機。

### 常用排查指令

```bash
# 查看 Java 應用 log（登入主機後）
tail -f /data/logs/*.log

# 查看服務狀態
systemctl status <service-name>

# 查看 Nginx 設定
cat /etc/nginx/conf.d/*.conf

# 查看端口佔用
ss -tlnp | grep <port>

# 本機殺掉佔用 port 的 process
killport 8080
```

---

## 12. 給 Claude 的自動化指令

```
# 一鍵 pull 所有專案
請幫我執行 ~/Workspace 下所有 git 專案的 pull --rebase

# 檢查所有專案狀態
請幫我檢查 ~/Workspace 下所有 git 專案的 branch 和 status

# 連線到遠端主機排查
請幫我 ssh 到 dev-wps 查看最新的 log
```
