# TCG-XXXXXX 对接短信商 OTP Expert

短信商域名: https://api.otp.expert
API对接文档: (由商務提供)

## API

### 1. Send SMS
**[POST]**: `https://api.otp.expert/api/send`

**Headers:**
| Header        | Value            |
|---------------|------------------|
| X-API-KEY     | `YOUR_API_KEY`   |
| Content-Type  | application/json |

**Request Body:**
```json
{
  "recipient": "+60123456789",
  "message": "654321",
  "type": "sms"
}
```

**Parameters:**

| 参数名称   | 类型   | 是否必填 | 说明                                                         |
|------------|--------|----------|--------------------------------------------------------------|
| recipient  | string | 是       | E.164 格式手机号 (e.g. +60123456789)                         |
| message    | string | 是       | 纯数字内容，OTP: 1-10 位数字                                |
| type       | enum   | 是       | `sms` / `whatsapp`                                           |
| message_type | enum | 否       | `otp` (默认) / `credential` / `password`                     |
| username   | string | 条件必填 | message_type=credential 时必填                               |
| password   | string | 条件必填 | message_type=password 或 message_type=credential 时必填      |

### 2. Get Balance
**[GET]**: `https://api.otp.expert/api/balance`

**Headers:**
| Header    | Value          |
|-----------|----------------|
| X-API-KEY | `YOUR_API_KEY` |

### 3. Get Message Logs
**[GET]**: `https://api.otp.expert/api/logs`

**Headers:**
| Header    | Value          |
|-----------|----------------|
| X-API-KEY | `YOUR_API_KEY` |

**Query Parameters (all optional):**

| 参数名称     | 类型    | 说明                                          |
|--------------|---------|-----------------------------------------------|
| page         | integer | min: 1                                        |
| per_page     | integer | min: 1, max: 100                              |
| message_type | enum    | `whatsapp` / `sms`                            |
| recipient    | string  | max: 50 (支持模糊搜索)                       |
| country_code | string  | max: 10                                       |
| date_from    | date    | 格式: Y-m-d                                   |
| date_to      | date    | 格式: Y-m-d; >= date_from                     |
| sort         | enum    | `created_at` / `final_cost` / `country_code`  |
| order        | enum    | `asc` / `desc`                                |

## 3. Error Code

待 API 回傳確認後補充。預設錯誤碼映射:

| Error Code            | 描述                   | 系统映射                          |
|-----------------------|------------------------|-----------------------------------|
| invalid_api_key       | API Key 无效           | SMS_NO_AUTHENTICATION             |
| invalid_recipient     | 手机号无效             | SMS_PROVIDER_INVALID_MOBILE       |
| invalid_message       | 短信内容无效           | SMS_PROVIDER_INVALID_CONTENT      |
| insufficient_balance  | 余额不足               | SMS_PROVIDER_ACCOUNT_BALANCE_NOT_ENOUGH |
| rate_limit_exceeded   | 触发频率限制           | TOO_MANY_REQUEST                  |
| invalid_type          | 类型参数无效           | REQ_PARAM_ERR                     |
| validation_error      | 验证错误               | REQ_PARAM_ERR                     |
| server_error          | 服务端错误             | PROVIDER_INTERNAL_ERROR           |

## 4. BO Settings Mapping

| Parameter          | Description | Example  |
|--------------------|-------------|----------|
| apiKey             | X-API-KEY   |          |
| countryOptions     | 支援国家    | GLOBAL   |
| countryDialingCode | 國碼        |          |

## 5. Notes

- 认证方式: 通过 `X-API-KEY` Header 传递 API Key，无需 account/password
- 手机号格式: E.164 格式，需带 `+` 前缀 (e.g. `+60123456789`)
- 支持短信类型: SMS 和 WhatsApp
- 支持消息类型: OTP (默认)、Credential、Password
- Provider ID: **190**
- Provider Class: `OtpExpertSMSProviderImpl`
