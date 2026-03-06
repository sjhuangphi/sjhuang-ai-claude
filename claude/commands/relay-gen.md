Generate and validate relay entries for tcg-wps-fe-sql.

Arguments: $ARGUMENTS
Parse as: `<patch-folder> [version]`
- `<patch-folder>`: 目標 patch 資料夾名稱，例如 `WSD-Miscellaneous`、`TP4828`
- `[version]`: 可選版本號，例如 `v03.00`（預設取該資料夾下最新版 +1）

Examples:
- `/relay-gen WSD-Miscellaneous`
- `/relay-gen WSD-Miscellaneous v03.00`
- `/relay-gen TP4828 v01.00`

---

## 執行流程

### Step 1 — 讀取 Excel
- 檔案：`~/Desktop/WSD Miscellaneous.xlsx`，Sheet：`API Relay`
- 欄位對照：

| Excel 欄 | 說明 |
|----------|------|
| F (`NEW WPS Relay`) | api_code |
| G (`Method`) | HTTP method |
| H (`WPS Module ID`) | module_id（逗號分隔取第一個）|
| I (`Before login`) | Y → require_login=0；N/? → require_login=1 |
| K (`NEW MCSFE API`) | 含 Method 前綴的路徑，解析出 api_loc |
| L (`MCSFE Swagger`) | Swagger URL |

### Step 2 — 查詢 Oracle Dev DB
```
host: 10.80.0.11  port: 1521  sid: tcgdev
user: TCG_GW  password: DAbzAVz8H5J3G9qC
```
```sql
SELECT API_CODE FROM TCG_GW.SYS_SETT_RELAY
```
使用 `python3 -c "import oracledb; ..."` (thin mode，不需 Oracle Client)

### Step 3 — 比對找出 Missing
在 Excel 有、DB 沒有的 api_code，過濾條件：
- api_loc 不為空
- subsystem_id 可從前綴對照表查到

### Step 3.5 — Auto-Name（api_code 為空時）
若 Excel 某筆的 `NEW WPS Relay` 欄位為空，自動生成 relay name：

**邏輯：**
1. **前綴**：從該筆的 **Swagger URL domain** 推斷
   - 取 swagger URL 的 `host:port`（例：`10.80.0.82:7009`）
   - 掃 Excel 整張 API Relay Sheet，找到**相同 swagger domain** 且 api_code 不為空的所有行
   - 統計這些行最常出現的 api_code 前綴（`UCSFE_`、`MCSFE_` 等），取最多的那個
   - 都找不到則 fallback `MCSFE_`
   - 範例：swagger `http://10.80.0.82:7009/...` → 同 domain 的行都是 `UCSFE_xxx` → 前綴 `UCSFE_`
2. **動詞**：依 HTTP method 對應
   - GET → `get`、POST → `submit`、PUT → `update`、DELETE → `delete`、PATCH → `update`
3. **名詞**：取 api_loc 最後 2 段 path segment，轉 CamelCase
   - `/verification/materials` → `VerificationMaterials`
4. **組合**：`{prefix}{verb}{Noun}`
   - 例：swagger domain `10.80.0.82:7009` → `UCSFE_` + `submit` + `VerificationMaterials` → `UCSFE_submitVerificationMaterials`

**SQL 備註**：在 SQL 該筆上方加上 `-- [AUTO-GENERATED NAME]` 標記，方便人工 review。

### Step 4 — Subsystem ID 對照表

| Prefix | ID | 系統名稱 |
|--------|----|----------|
| MCSFE_ | 43 | TCG-MCS-FE |
| ODSFE2_ | 23 | TCG-ODSFE |
| PROMOFE_ | 47 | TCG-PROMO-FE |
| CBS_ | 41 | TCG-CBS |
| CSP_ | 36 | TCG-CSP |
| WPSCORE_ | 48 | TCG-WPS-CORE |
| WPS3RD_ | 50 | TCG-WPS-3RD |
| LGWVN_ | 49 | TCG-LGW-VN |
| MRSFE_ | 55 | TCG-MRS-FE |
| EMDFE_ | 54 | TCG-EMD |
| UCSFE_ | 57 | TCG-UCS-FE |
| CCSFE_ | 52 | TCG-CCS-ANNOUNCEMENT-FE |
| GCSGAME_ | 39 | TCG-GCS-GAME |
| GCS_ / GCS2_ | 35 | TCG-GCS |
| GHRS_ | 45 | TCG-GHRS |
| LGS_ | 33 | TCG-LGS |
| VIS_ | 7 | TCG-VIS |
| MIS_ | 56 | TCG-MISCONSOLE |

若無法對應 subsystem，需先建立 `TCG_SUBSYSTEM` 記錄再繼續。

### Step 5 — 生成 SQL Patch
- 路徑：`20.patches/<patch-folder>/<version>/TCG_GW_SYS-SETT-RELAY-<patch-folder>-<YYYYMMDD>.sql`
- 檔頭只留 2 行 comment，之後每筆之間空一行，無分隔線
- AUTO-GENERATED 的那筆在前面加一行 `-- <api_code> [AUTO-GENERATED NAME]`
- 全部 **單行**，不換行；`SYS_SETTING_MODULE` DELETE 用小寫 `and`

```sql
-- <patch-folder> <version> | <YYYY-MM-DD>
-- <api_code1>, <api_code2>, ...

DELETE FROM TCG_GW.SYS_SETT_RELAY WHERE API_CODE = '<api_code>';
DELETE FROM TCG_GW.SYS_SETTING_MODULE WHERE MODULE_ID = '<MODULE>' and FUNCTION_ID = TCG_GW.get_func_id('relay/<api_code>', '<METHOD>');
DELETE FROM TCG_GW.SYS_SETTING_FUNCTION WHERE URI = 'relay/<api_code>' AND HTTP_METHOD = '<METHOD>';
INSERT INTO TCG_GW.SYS_SETT_RELAY(IDX, API_CODE, API_LOC, SUBSYSTEM_ID, REQUIRE_LOGIN) VALUES (TCG_GW.SETT_RELAY_SEQ.nextval, '<api_code>', '<api_loc>', <sys_id>, <req_login>);
INSERT INTO TCG_GW.SYS_SETTING_FUNCTION (FUNCTION_ID, URI, HTTP_METHOD, FUNCTION_NAME, COMMENTS) VALUES (TCG_GW.SETT_FUNC_ID.nextval, 'relay/<api_code>', '<METHOD>', '<desc>', null);
INSERT INTO TCG_GW.SYS_SETTING_MODULE(IDX, MODULE_ID, FUNCTION_ID, COMMENTS) VALUES (TCG_GW.SETT_MODU_MAPP_SEQ.nextval, '<MODULE>', TCG_GW.get_func_id('relay/<api_code>', '<METHOD>'), '');

COMMIT;
```

### Step 6 — 推送到 Dev DB
使用 oracledb 直接執行（DELETE idempotent，INSERT，最後 COMMIT）

### Step 7 — Rebuild & 測試
```bash
# Rebuild
curl -s GET http://10.80.0.34:7001/tcg-service/resources/system/database/rebuild/common

# 測試每筆
curl -s -X GET \
  --header 'Accept: application/json' \
  --header 'Language: CN' \
  --header 'ModuleId: <MODULE>' \
  'http://10.80.0.34:7001/tcg-service/resources/relay/info?code=<api_code>'
```
驗證：`success=true` 且 `value` = `<subsystem_base_url><api_loc>`

### Step 8 — 生成文件
1. **Release lst**：`99.release/<patch-folder>/<version>.lst`（列出 SQL 檔名）
2. **Relay 說明文件**：`~/Desktop/doc/relay/<YYYY-MM-DD>.md`（見格式）
3. **工作紀錄**：append 到 `~/Desktop/doc/logs/tcg-wps-fe-sql.md`

## Relay 文件格式（每個 api_code 一張表）

```markdown
## <api_code>

| 欄位 | 值 |
|------|-----|
| Swagger | [連結](<swagger_url>) |
| Api Code | <api_code> |
| ModuleId | <module_id> |
| Http Method | <method> |
| Api Loc | <api_loc> |
| System Id | <subsystem_id> |
| Require Login | <require_login> |
| Description | <desc> |
| DB Patch List | <patch-folder>/<version>.lst |
```

## 注意事項
- dev server 正確 IP：`10.80.0.34`（非 `10.80.1.32`）
- `Before login = Y` → `require_login = 0`
- module_id 若逗號分隔，取第一個
- 測試前必須先呼叫 rebuild/common
- git commit 與 notion-sync **等用戶確認後再執行**
