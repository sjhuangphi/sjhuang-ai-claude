# Skill: 对接短信商 OTP Expert (Provider ID: 190)

## 概要

| 项目           | 值                                      |
|----------------|------------------------------------------|
| Provider Name  | OTP Expert                               |
| Provider ID    | 190                                      |
| Provider Class | `OtpExpertSMSProviderImpl`               |
| API Base URL   | `https://api.otp.expert`                 |
| 认证方式       | `X-API-KEY` Header                       |
| 支援类型       | SMS / WhatsApp                           |
| 支援国家       | GLOBAL                                   |

## 文件清单

| 文件类型       | 路径                                                                                              |
|----------------|---------------------------------------------------------------------------------------------------|
| Provider 实现  | `src/main/java/.../service/sms/provider/OtpExpertSMSProviderImpl.java`                           |
| 对接文档       | `docs/TCG-XXXXXX-sms-otp-expert.md`                                                              |

## API 端点

| 功能       | Method | URL                                  |
|------------|--------|--------------------------------------|
| 发送短信   | POST   | `https://api.otp.expert/api/send`    |
| 查询余额   | GET    | `https://api.otp.expert/api/balance` |
| 发送记录   | GET    | `https://api.otp.expert/api/logs`    |

## BO 参数设定

| BO Parameter       | 用途             | 对应 GwSmsParamsConstant |
|--------------------|------------------|--------------------------|
| apiKey             | X-API-KEY 认证   | `API_KEY`                |
| countryOptions     | 支援国家         | `COUNTRY_OPTIONS`        |
| countryDialingCode | 國碼             | `COUNTRY_DIALING_CODE`   |

## 实现特点

1. **认证**: 使用 `X-API-KEY` Header，无需 account/password 组合
2. **手机号格式**: E.164 格式，加 `+` 前缀 (e.g. `+60123456789`)
3. **请求格式**: JSON POST
4. **余额查询**: 已实现 `getBalance()` 方法
5. **发送方式**: 仅实现 `sendOnceGlobal()`（全球短信），`sendOnce()` 返回空 `SMSReply`

## 注意事项

- Error Code 映射为预设值，需根据实际 API 回传调整
- API 响应格式中的 success/error key 需实测确认（当前假设 `status` 字段）
- 如 API 响应格式与预期不符，需调整 `getErrorCodeKey()` / `getSuccessCodeKey()` / `getMsgIdKey()`

## 快速调试

```bash
# 测试发送 SMS
curl --location 'https://api.otp.expert/api/send' \
--header 'X-API-KEY: YOUR_API_KEY_HERE' \
--header 'Content-Type: application/json' \
--data '{"recipient":"+60123456789","message":"654321","type":"sms"}'

# 查询余额
curl --location 'https://api.otp.expert/api/balance' \
--header 'X-API-KEY: YOUR_API_KEY_HERE'

# 查询发送记录
curl --location 'https://api.otp.expert/api/logs?page=1&per_page=10&message_type=sms' \
--header 'X-API-KEY: YOUR_API_KEY_HERE'
```
