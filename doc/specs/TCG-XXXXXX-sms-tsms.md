# TCG-XXXXXX 对接短信商 TSMS

短信商域名: https://dash.tsms.top
API对接文档: [tsms] api documents V2

## API

### 1. Send SMS (Create OTP)
**[POST]**: `https://dash.tsms.top/api/v2/service/singlechannel`

**Sign**: HMAC-SHA256 `trans_code|type_id|receiver|api_key` (lowercase)

**Success Msg**
```json
{
  "status": "success",
  "errorCode": 0,
  "data": {
    "trans_id": "20242710044144815860",
    "trans_code": "0eea2feb-e88c-46ff-b48f-5224c4d39587",
    "code": "401341",
    "status": 1
  },
  "message": "OK"
}
```

**Error Msg**
```json
{
  "status": "error",
  "errorCode": 400,
  "data": null,
  "message": "Invalid parameters"
}
```

| 参数名称   | 类型   | 是否必填 | 说明                          |
|------------|--------|----------|-------------------------------|
| sign       | string | 是       | HMAC-SHA256 签名 (lowercase)  |
| api_key    | string | 是       | merchant api key              |
| type_id    | int    | 是       | 1=SMS, 2=Voice, 3=ZNS-Zalo   |
| trans_code | string | 是       | merchant order no (UUID)      |
| receiver   | string | 是       | 手机号 (越南)                 |
| code       | string | 是       | OTP 验证码                    |
| callback   | string | 否       | callback address              |

### 2. Get Balance
**[POST]**: `https://dash.tsms.top/api/v2/user/balance`

**Sign**: HMAC-SHA256 `timestamp|api_key` (lowercase)

| 参数名称  | 类型   | 是否必填 | 说明                     |
|-----------|--------|----------|--------------------------|
| sign      | string | 是       | HMAC-SHA256 签名         |
| timestamp | string | 是       | timestamp (length 10)    |
| api_key   | string | 是       | merchant api key         |

**Response**
```json
{
  "status": "success",
  "errorCode": 0,
  "data": {
    "balance": 1015000,
    "created": "2024-10-26T03:25:26.000000Z"
  },
  "message": "OK"
}
```

### 3. Get Status
**[POST]**: `https://dash.tsms.top/api/v2/service/status`

**Sign**: SHA256 `trans_code|trans_id|type_id|api_key`

| 参数名称   | 类型   | 是否必填 | 说明             |
|------------|--------|----------|------------------|
| sign       | string | 是       | 签名             |
| trans_code | string | 条件必填 | merchant order no |
| trans_id   | string | 条件必填 | gate order no    |
| api_key    | string | 是       | merchant api key |
| type_id    | int    | 是       | 类型             |

### 4. Callback Body
**Method**: POST
**Sign**: MD5 `trans_id|status|api_key`

```json
{
  "url": "https://webhook.site/xxx",
  "cost": 1000,
  "trans_id": "20242710044144815860",
  "trans_code": "0eea2feb-e88c-46ff-b48f-5224c4d39587",
  "status": 3,
  "sign": "b478b6746f9df189188e410f01043755",
  "type": 1,
  "extra": null
}
```

| Key        | Description                          |
|------------|--------------------------------------|
| status     | 1 = Waiting, 2 = Success, 3 = Failed |
| type       | 1 = SMS                              |
| cost       | order cost                           |
| trans_code | gate order no                        |
| trans_id   | merchant order no                    |

## 3. Error Code

| errorCode | 描述         | 系统映射                |
|-----------|--------------|-------------------------|
| 400       | 参数错误     | REQ_PARAM_ERR           |
| 401       | 认证失败     | SMS_NO_AUTHENTICATION   |
| 403       | 无权限       | SMS_NO_AUTHENTICATION   |
| 500       | 服务端错误   | PROVIDER_INTERNAL_ERROR |

## 4. BO Settings Mapping

| Parameter          | Description       | Example |
|--------------------|-------------------|---------|
| apiKey             | merchant api key  |         |
| privateKey         | HMAC 签名密钥     |         |
| countryOptions     | 支援国家          | VN      |
| countryDialingCode | 國碼              | 84      |

## 5. Notes

- 认证方式: HMAC-SHA256 签名，签名结果需 lowercase
- 签名格式 (发送): `trans_code|type_id|receiver|api_key`
- 签名格式 (余额): `timestamp|api_key`
- 目前仅实现 type_id=1 (SMS)，未实现 Voice 和 ZNS-Zalo
- 越南市场专用
- Provider ID: **191**
- Provider Class: `TsmsSMSProviderImpl`
