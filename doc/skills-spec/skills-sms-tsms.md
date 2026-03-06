# Skill: 对接短信商 TSMS (Provider ID: 191)

## 概要

| 项目           | 值                                      |
|----------------|------------------------------------------|
| Provider Name  | TSMS                                     |
| Provider ID    | 191                                      |
| Provider Class | `TsmsSMSProviderImpl`                    |
| API Base URL   | `https://dash.tsms.top`           |
| 认证方式       | HMAC-SHA256 签名                         |
| 支援类型       | SMS (type_id=1)                          |
| 支援国家       | VN (越南)                                |

## 文件清单

| 文件类型       | 路径                                                                                              |
|----------------|---------------------------------------------------------------------------------------------------|
| Provider 实现  | `src/main/java/.../service/sms/provider/TsmsSMSProviderImpl.java`                                |
| 对接文档       | `~/Desktop/TCG-XXXXXX-sms-tsms.md`                                                               |

## API 端点

| 功能       | Method | URL                                         |
|------------|--------|---------------------------------------------|
| 发送短信   | POST   | `https://dash.tsms.top/api/v2/service/singlechannel`   |
| 查询余额   | POST   | `https://dash.tsms.top/api/v2/user/balance`            |
| 查询状态   | POST   | `https://dash.tsms.top/api/v2/service/status`          |

## BO 参数设定

| BO Parameter       | 用途             | 对应 GwSmsParamsConstant |
|--------------------|------------------|--------------------------|
| apiKey             | merchant api key | `API_KEY`                |
| privateKey         | HMAC 签名密钥    | `PRIVATE_KEY`            |
| countryOptions     | 支援国家         | `COUNTRY_OPTIONS`        |
| countryDialingCode | 國碼             | `COUNTRY_DIALING_CODE`   |

## 签名规则

| 场景     | 算法        | 格式                                      |
|----------|-------------|-------------------------------------------|
| 发送短信 | HMAC-SHA256 | `trans_code\|type_id\|receiver\|api_key`  |
| 查询余额 | HMAC-SHA256 | `timestamp\|api_key`                      |
| 查询状态 | SHA256      | `trans_code\|trans_id\|type_id\|api_key`  |
| Callback | MD5         | `trans_id\|status\|api_key`               |

## 实现特点

1. **HMAC-SHA256 签名**: 使用 `privateKey` 作为 HMAC 密钥，输出 lowercase hex
2. **动态域名**: domain 由 BO 设定，非硬编码
3. **trans_code**: 使用 UUID 生成唯一订单号
4. **余额查询**: 已实现，使用 timestamp 签名
5. **仅 SMS**: type_id 固定为 1，未实现 Voice / ZNS-Zalo

## 快速调试

```bash
# 测试发送 SMS
curl --location 'https://dash.tsms.top/api/v2/service/singlechannel' \
--header 'Content-Type: application/json' \
--data '{
  "sign": "YOUR_HMAC_SIGN",
  "api_key": "YOUR_API_KEY",
  "type_id": 1,
  "trans_code": "test-order-001",
  "receiver": "84123456789",
  "code": "123456"
}'

# 查询余额
curl --location 'https://dash.tsms.top/api/v2/user/balance' \
--header 'Content-Type: application/json' \
--data '{
  "sign": "YOUR_HMAC_SIGN",
  "timestamp": "1709600000",
  "api_key": "YOUR_API_KEY"
}'
```
