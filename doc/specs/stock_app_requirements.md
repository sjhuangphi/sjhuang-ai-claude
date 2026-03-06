# Stock App 便宜價分析系統需求文檔

---

**文件版本**: v1.0
**建立日期**: 2026-03-04
**作者**: Stock Analytics Expert
**審核狀態**: Draft
**專案代碼**: STOCK-APP-001

---

## 文件摘要

本文檔定義 Stock App 便宜價分析系統的完整功能與技術需求。系統旨在提供台股、美股、ETF、債券的估值分析,透過多種估值模型計算合理買入價位,並提供視覺化圖表與投資建議。

---

## 目錄

1. [專案概述](#1-專案概述)
2. [功能需求](#2-功能需求)
3. [非功能需求](#3-非功能需求)
4. [數據架構](#4-數據架構)
5. [API 規格](#5-api-規格)
6. [UI/UX 規範](#6-uiux-規範)
7. [估值模型規格](#7-估值模型規格)
8. [安全需求](#8-安全需求)
9. [部署架構](#9-部署架構)
10. [術語表](#10-術語表)
11. [變更紀錄](#11-變更紀錄)

---

## 1. 專案概述

### 1.1 專案目標

建立一個股票估值分析平台,協助投資者判斷標的資產（個股、ETF、債券）的合理買入價位,減少追高風險。

### 1.2 核心價值主張

- **多維度估值**: 整合本益比、股價淨值比、殖利率、歷史價格區間四種估值方法
- **跨市場支援**: 涵蓋台股、美股、ETF、債券
- **視覺化呈現**: 以河流圖等圖表直觀展示估值區間
- **智能建議**: 基於多模型綜合判斷提供買入建議

### 1.3 目標用戶

- 個人投資者（價值投資導向）
- 財務顧問
- 量化分析師

### 1.4 成功指標

- 系統可查詢標的數量 > 5,000 支（台股）+ 主要美股
- 估值計算準確率 > 95%
- API 回應時間 < 2 秒（P95）
- 圖表渲染時間 < 1 秒

---

## 2. 功能需求

### 2.1 核心功能清單

| 功能編號 | 功能名稱 | 優先級 | 描述 |
|---------|---------|-------|------|
| F-001 | 標的查詢 | P0 | 支援股票代號、名稱搜尋 |
| F-002 | 本益比估值 | P0 | 計算 PER 便宜價/合理價/昂貴價 |
| F-003 | 股價淨值比估值 | P0 | 計算 PBR 便宜價/合理價/昂貴價 |
| F-004 | 殖利率估值 | P0 | 基於股息殖利率估算價格區間 |
| F-005 | 歷史價格區間估值 | P0 | 河流圖展示歷史價格分佈 |
| F-006 | 綜合買入建議 | P0 | 基於多模型輸出：便宜/合理/昂貴 |
| F-007 | 估值圖表視覺化 | P1 | 河流圖、雷達圖、價格區間圖 |
| F-008 | 歷史數據下載 | P1 | 下載原始數據與估值結果（CSV） |
| F-009 | 自選清單 | P2 | 儲存常用標的 |
| F-010 | 估值變化通知 | P3 | 當標的進入便宜區間時推送通知 |

### 2.2 功能詳細規格

#### F-001: 標的查詢

**使用者故事**:
身為投資者,我希望能夠透過股票代號或名稱快速查詢標的,以便進行估值分析。

**輸入**:
- 股票代號（例: 2330.TW, AAPL）
- 公司名稱（例: 台積電, Apple）

**輸出**:
- 標的基本資訊（名稱、代號、產業、市值、最新價格）
- 支援模糊搜尋

**驗收標準**:
- [x] 支援台股代號格式（例: 2330.TW）
- [x] 支援美股代號格式（例: AAPL）
- [x] 支援中文/英文名稱搜尋
- [x] 搜尋回應時間 < 1 秒
- [x] 顯示搜尋結果最多 20 筆

---

#### F-002: 本益比估值（PER Valuation）

**使用者故事**:
身為投資者,我希望看到基於本益比計算的便宜價、合理價、昂貴價,以便判斷當前價位是否合理。

**計算邏輯**:
```
便宜價 = EPS × 歷史本益比 25 百分位數
合理價 = EPS × 歷史本益比 50 百分位數（中位數）
昂貴價 = EPS × 歷史本益比 75 百分位數
```

**輸入**:
- 最新 EPS（每股盈餘,優先使用 TTM）
- 歷史本益比數據（過去 5 年）

**輸出**:
- 便宜價（元）
- 合理價（元）
- 昂貴價（元）
- 當前價格所在區間（便宜/合理/昂貴）
- 安全邊際百分比

**驗收標準**:
- [x] 計算結果精度至小數點後 2 位
- [x] 若 EPS 為負數或無數據,標註「不適用 PER 估值」
- [x] 顯示歷史本益比分佈圖
- [x] 標註數據來源與更新時間

---

#### F-003: 股價淨值比估值（PBR Valuation）

**使用者故事**:
身為投資者,我希望透過股價淨值比評估資產型股票的價值,特別是金融股。

**計算邏輯**:
```
便宜價 = BVPS × 歷史 PBR 25 百分位數
合理價 = BVPS × 歷史 PBR 50 百分位數
昂貴價 = BVPS × 歷史 PBR 75 百分位數
```

**輸入**:
- 最新 BVPS（每股淨值）
- 歷史 PBR 數據（過去 5 年）

**輸出**:
- 便宜價/合理價/昂貴價
- 當前 PBR 值
- 產業平均 PBR（參考值）

**驗收標準**:
- [x] 計算結果精度至小數點後 2 位
- [x] 若淨值為負數,標註「不適用 PBR 估值」
- [x] 顯示歷史 PBR 趨勢圖

---

#### F-004: 殖利率估值（Dividend Yield Valuation）

**使用者故事**:
身為存股族,我希望透過股息殖利率評估配息股的合理價位。

**計算邏輯**:
```
便宜價 = 年度股息 ÷ 高殖利率門檻（如 6%）
合理價 = 年度股息 ÷ 中位數殖利率（如 4%）
昂貴價 = 年度股息 ÷ 低殖利率門檻（如 2%）
```

**殖利率門檻取值**:
- 使用該標的歷史殖利率的 75 百分位數（便宜價門檻）
- 使用歷史殖利率的 50 百分位數（合理價門檻）
- 使用歷史殖利率的 25 百分位數（昂貴價門檻）

**輸入**:
- 最近一年股息總和（含現金股息、股票股利）
- 歷史殖利率數據（過去 5 年）

**輸出**:
- 便宜價/合理價/昂貴價
- 當前殖利率
- 近 5 年平均殖利率

**驗收標準**:
- [x] 若無配息紀錄,標註「不適用殖利率估值」
- [x] 顯示歷史殖利率曲線圖
- [x] 標註除息日與股息發放頻率

---

#### F-005: 歷史價格區間估值（河流圖）

**使用者故事**:
身為投資者,我希望透過視覺化圖表看到歷史價格的分佈區間,了解當前價位在歷史中的位置。

**計算邏輯**:
```
使用過去 5 年的日收盤價計算:
- 10 百分位數 → 極度便宜區
- 25 百分位數 → 便宜區
- 50 百分位數 → 合理區
- 75 百分位數 → 昂貴區
- 90 百分位數 → 極度昂貴區
```

**輸出**:
- 河流圖（X 軸: 時間, Y 軸: 價格, 填色顯示區間）
- 當前價格標註
- 百分位數數值表

**驗收標準**:
- [x] 圖表支援縮放與拖曳
- [x] 滑鼠懸停顯示該時間點的價格與百分位
- [x] 可調整歷史區間（1年/3年/5年/10年）

---

#### F-006: 綜合買入建議

**使用者故事**:
身為投資者,我希望系統能綜合多種估值方法給出一個明確的建議,避免單一指標誤判。

**判斷邏輯**:

1. **便宜（Strong Buy）**: 至少 3 種估值方法顯示「便宜」
2. **偏便宜（Buy）**: 至少 2 種估值方法顯示「便宜」
3. **合理（Hold）**: 大部分估值方法顯示「合理」
4. **偏貴（Avoid）**: 至少 2 種估值方法顯示「昂貴」
5. **昂貴（Strong Avoid）**: 至少 3 種估值方法顯示「昂貴」

**輸出**:
- 建議等級（便宜/偏便宜/合理/偏貴/昂貴）
- 信心分數（0-100）
- 各估值方法的判斷結果矩陣

**驗收標準**:
- [x] 至少需有 2 種估值方法有效才輸出建議
- [x] 顯示各方法的權重與判斷依據
- [x] 若數據不足,標註「資料不足,無法給出建議」

---

#### F-007: 估值圖表視覺化

**圖表類型**:

1. **河流圖（River Chart）**:
   - 顯示歷史價格區間
   - 漸層填色（綠色=便宜, 黃色=合理, 紅色=昂貴）

2. **雷達圖（Radar Chart）**:
   - 顯示四種估值方法的當前位置
   - 中心=便宜, 外圍=昂貴

3. **價格區間圖（Price Range Chart）**:
   - 橫條圖顯示各估值方法的價格區間
   - 標註當前價格位置

**驗收標準**:
- [x] 圖表使用 Chart.js 或 Recharts
- [x] 支援 RWD（手機、平板、桌面）
- [x] 圖表可匯出為 PNG

---

## 3. 非功能需求

### 3.1 效能需求

| 需求編號 | 指標 | 目標值 |
|---------|------|-------|
| NFR-001 | API 回應時間（P95） | < 2 秒 |
| NFR-002 | 圖表渲染時間 | < 1 秒 |
| NFR-003 | 資料庫查詢時間 | < 500 ms |
| NFR-004 | 併發使用者支援 | 100+ |
| NFR-005 | 數據更新頻率 | 每日盤後更新 |

### 3.2 可用性需求

- **正常運行時間**: 99% uptime（排除維護時段）
- **資料完整性**: 歷史數據保存至少 10 年
- **容錯機制**: 當外部 API 失效時,使用快取數據並標註

### 3.3 擴展性需求

- 系統架構支援水平擴展
- 資料庫設計支援 Sharding
- 快取層使用 Redis

### 3.4 相容性需求

- **瀏覽器**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **行動裝置**: iOS 14+, Android 10+
- **螢幕解析度**: 最小支援 375px（iPhone SE）

---

## 4. 數據架構

### 4.1 資料庫設計（MySQL）

#### Table: `stocks`
```sql
CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE COMMENT '股票代號（如 2330.TW）',
    name VARCHAR(100) NOT NULL COMMENT '公司名稱',
    name_en VARCHAR(100) COMMENT '英文名稱',
    market VARCHAR(20) NOT NULL COMMENT '市場（TWSE, NASDAQ, NYSE）',
    industry VARCHAR(50) COMMENT '產業分類',
    asset_type ENUM('STOCK', 'ETF', 'BOND') DEFAULT 'STOCK',
    currency VARCHAR(3) DEFAULT 'TWD' COMMENT '幣別',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_market (market)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='標的主檔';
```

#### Table: `price_history`
```sql
CREATE TABLE price_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(12, 2),
    high DECIMAL(12, 2),
    low DECIMAL(12, 2),
    close DECIMAL(12, 2) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(12, 2) COMMENT '還原股價',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY uk_stock_date (stock_id, date),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='歷史價格';
```

#### Table: `financial_metrics`
```sql
CREATE TABLE financial_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    report_date DATE NOT NULL COMMENT '財報期間（如 2024Q4）',
    eps DECIMAL(10, 4) COMMENT '每股盈餘',
    bvps DECIMAL(10, 4) COMMENT '每股淨值',
    revenue BIGINT COMMENT '營收',
    net_income BIGINT COMMENT '淨利',
    total_equity BIGINT COMMENT '股東權益',
    total_assets BIGINT COMMENT '總資產',
    pe_ratio DECIMAL(10, 2) COMMENT '本益比',
    pb_ratio DECIMAL(10, 2) COMMENT '股價淨值比',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY uk_stock_report (stock_id, report_date),
    INDEX idx_report_date (report_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='財務指標';
```

#### Table: `dividend_history`
```sql
CREATE TABLE dividend_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    ex_dividend_date DATE NOT NULL COMMENT '除息日',
    cash_dividend DECIMAL(10, 4) DEFAULT 0 COMMENT '現金股利',
    stock_dividend DECIMAL(10, 4) DEFAULT 0 COMMENT '股票股利',
    total_dividend DECIMAL(10, 4) COMMENT '合計股利',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    INDEX idx_ex_date (ex_dividend_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股息歷史';
```

#### Table: `valuation_cache`
```sql
CREATE TABLE valuation_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    valuation_date DATE NOT NULL,
    per_cheap DECIMAL(12, 2) COMMENT 'PER 便宜價',
    per_fair DECIMAL(12, 2) COMMENT 'PER 合理價',
    per_expensive DECIMAL(12, 2) COMMENT 'PER 昂貴價',
    pbr_cheap DECIMAL(12, 2),
    pbr_fair DECIMAL(12, 2),
    pbr_expensive DECIMAL(12, 2),
    yield_cheap DECIMAL(12, 2),
    yield_fair DECIMAL(12, 2),
    yield_expensive DECIMAL(12, 2),
    recommendation ENUM('STRONG_BUY', 'BUY', 'HOLD', 'AVOID', 'STRONG_AVOID'),
    confidence_score DECIMAL(5, 2) COMMENT '信心分數（0-100）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY uk_stock_valuation_date (stock_id, valuation_date),
    INDEX idx_valuation_date (valuation_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='估值快取';
```

### 4.2 數據來源

| 數據類型 | 資料源 | 更新頻率 |
|---------|-------|---------|
| 台股價格 | TWSE API / Yahoo Finance | 每日盤後 |
| 美股價格 | Yahoo Finance / Alpha Vantage | 每日盤後 |
| 台股財報 | 公開資訊觀測站 | 季度 |
| 美股財報 | Alpha Vantage / Financial Modeling Prep | 季度 |
| 股息資料 | TWSE / Yahoo Finance | 配息公告後 |

### 4.3 數據完整性檢查

- **價格數據**: 檢查是否有缺失日期,若有則標註
- **財報數據**: 驗證 EPS、BVPS 是否合理（不為極端值）
- **股息數據**: 驗證股息總和與配息率

---

## 5. API 規格

### 5.1 RESTful API 設計原則

- 使用 RESTful 架構
- 回應格式: JSON
- 使用 HTTP 狀態碼（200, 400, 404, 500）
- 使用 Swagger/OpenAPI 3.0 文件化

### 5.2 API 端點列表

#### 5.2.1 GET `/api/v1/stocks/search`

**描述**: 搜尋股票標的

**Query Parameters**:
```
q: string (必填) - 搜尋關鍵字（股票代號或名稱）
market: string (選填) - 市場篩選（TWSE, NASDAQ, NYSE）
limit: integer (選填) - 回傳筆數（預設 20）
```

**回應範例**:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "symbol": "2330.TW",
      "name": "台積電",
      "name_en": "TSMC",
      "market": "TWSE",
      "industry": "半導體",
      "asset_type": "STOCK",
      "current_price": 625.00,
      "currency": "TWD"
    }
  ],
  "meta": {
    "total": 1,
    "query": "2330"
  }
}
```

---

#### 5.2.2 GET `/api/v1/stocks/{symbol}/valuation`

**描述**: 取得標的估值分析

**Path Parameters**:
```
symbol: string (必填) - 股票代號（如 2330.TW）
```

**Query Parameters**:
```
methods: string (選填) - 估值方法（per,pbr,yield,history）預設全部
lookback_years: integer (選填) - 歷史回溯年數（預設 5 年）
```

**回應範例**:
```json
{
  "status": "success",
  "data": {
    "stock": {
      "symbol": "2330.TW",
      "name": "台積電",
      "current_price": 625.00,
      "price_date": "2026-03-03"
    },
    "valuation": {
      "per": {
        "cheap_price": 520.00,
        "fair_price": 600.00,
        "expensive_price": 700.00,
        "current_zone": "FAIR",
        "safety_margin": -4.17,
        "available": true,
        "current_per": 18.5,
        "historical_per_percentiles": {
          "p25": 15.0,
          "p50": 18.0,
          "p75": 22.0
        }
      },
      "pbr": {
        "cheap_price": 480.00,
        "fair_price": 580.00,
        "expensive_price": 720.00,
        "current_zone": "FAIR",
        "available": true,
        "current_pbr": 5.2
      },
      "dividend_yield": {
        "cheap_price": 500.00,
        "fair_price": 625.00,
        "expensive_price": 750.00,
        "current_zone": "FAIR",
        "available": true,
        "current_yield": 2.5,
        "annual_dividend": 15.0
      },
      "historical_price": {
        "p10": 450.00,
        "p25": 520.00,
        "p50": 600.00,
        "p75": 680.00,
        "p90": 750.00,
        "current_percentile": 52
      }
    },
    "recommendation": {
      "level": "HOLD",
      "confidence_score": 78,
      "reasoning": "3 種估值方法顯示合理,1 種顯示便宜",
      "summary_matrix": [
        {"method": "PER", "zone": "FAIR"},
        {"method": "PBR", "zone": "FAIR"},
        {"method": "Dividend Yield", "zone": "FAIR"},
        {"method": "Historical Price", "zone": "FAIR"}
      ]
    },
    "metadata": {
      "calculation_date": "2026-03-04",
      "data_sources": ["TWSE", "Yahoo Finance"],
      "last_financial_report": "2025Q4"
    }
  }
}
```

---

#### 5.2.3 GET `/api/v1/stocks/{symbol}/price-history`

**描述**: 取得歷史價格（用於河流圖）

**Path Parameters**:
```
symbol: string (必填) - 股票代號
```

**Query Parameters**:
```
start_date: string (選填) - 開始日期（YYYY-MM-DD）
end_date: string (選填) - 結束日期（YYYY-MM-DD）
interval: string (選填) - 資料間隔（daily, weekly, monthly）預設 daily
```

**回應範例**:
```json
{
  "status": "success",
  "data": {
    "symbol": "2330.TW",
    "prices": [
      {
        "date": "2026-03-03",
        "close": 625.00,
        "percentile": 52,
        "zone": "FAIR"
      },
      {
        "date": "2026-03-02",
        "close": 620.00,
        "percentile": 50,
        "zone": "FAIR"
      }
    ],
    "price_bands": {
      "p10": 450.00,
      "p25": 520.00,
      "p50": 600.00,
      "p75": 680.00,
      "p90": 750.00
    }
  }
}
```

---

#### 5.2.4 GET `/api/v1/stocks/{symbol}/financials`

**描述**: 取得財務數據

**回應範例**:
```json
{
  "status": "success",
  "data": {
    "symbol": "2330.TW",
    "financials": [
      {
        "report_date": "2025Q4",
        "eps": 10.5,
        "bvps": 120.0,
        "pe_ratio": 18.5,
        "pb_ratio": 5.2,
        "revenue": 625000000000,
        "net_income": 250000000000
      }
    ]
  }
}
```

---

#### 5.2.5 POST `/api/v1/watchlist`

**描述**: 新增自選股（需登入）

**Request Body**:
```json
{
  "symbol": "2330.TW"
}
```

**回應**:
```json
{
  "status": "success",
  "message": "已加入自選清單"
}
```

---

### 5.3 錯誤處理

**標準錯誤格式**:
```json
{
  "status": "error",
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "查無此股票代號",
    "details": {
      "symbol": "9999.TW"
    }
  }
}
```

**錯誤碼列表**:

| 錯誤碼 | HTTP Status | 說明 |
|-------|-------------|------|
| STOCK_NOT_FOUND | 404 | 股票代號不存在 |
| INVALID_SYMBOL | 400 | 股票代號格式錯誤 |
| INSUFFICIENT_DATA | 422 | 數據不足無法計算估值 |
| RATE_LIMIT_EXCEEDED | 429 | API 呼叫次數超過限制 |
| INTERNAL_ERROR | 500 | 伺服器內部錯誤 |

---

## 6. UI/UX 規範

### 6.1 設計原則

- **簡潔優先**: 避免資訊過載,分層展示
- **視覺引導**: 使用顏色編碼（綠=便宜, 黃=合理, 紅=昂貴）
- **回應式設計**: 支援手機、平板、桌面
- **無障礙**: 符合 WCAG 2.1 AA 標準

### 6.2 頁面架構

#### 6.2.1 首頁

**組成元素**:
- 搜尋欄（置中、大型輸入框）
- 熱門標的卡片（顯示當前建議等級）
- 快速連結（我的自選、最近查看）

---

#### 6.2.2 估值分析頁

**Layout**:
```
+----------------------------------+
| 標的資訊區                        |
| 台積電 (2330.TW) | 當前價: 625 元 |
+----------------------------------+
| 綜合建議卡片                      |
| ✓ 合理 (Hold) | 信心分數: 78     |
+----------------------------------+
| 估值方法 Tab                      |
| [本益比] [淨值比] [殖利率] [河流圖]|
+----------------------------------+
| 圖表區域                          |
| [視覺化圖表]                      |
+----------------------------------+
| 數據表格區域                      |
| 便宜價: 520 元                    |
| 合理價: 600 元                    |
| 昂貴價: 700 元                    |
+----------------------------------+
```

---

### 6.3 顏色規範

| 用途 | 顏色代碼 | 說明 |
|-----|---------|------|
| 便宜區 | #10B981 (綠色) | 建議買入 |
| 合理區 | #F59E0B (黃色) | 持有觀望 |
| 昂貴區 | #EF4444 (紅色) | 避免買入 |
| 主色調 | #3B82F6 (藍色) | 按鈕、連結 |
| 背景色 | #F9FAFB | 主背景 |
| 文字色 | #1F2937 | 主要文字 |

---

### 6.4 圖表規範

#### 河流圖（River Chart）

- X 軸: 時間（日期）
- Y 軸: 價格
- 填色區間:
  - P0-P25: 深綠色（極度便宜）
  - P25-P50: 淺綠色（便宜）
  - P50-P75: 淺黃色（合理）
  - P75-P90: 淺紅色（昂貴）
  - P90-P100: 深紅色（極度昂貴）
- 當前價格標註: 黑色虛線 + 標籤

---

### 6.5 互動設計

- 懸停提示: 顯示詳細數據
- 點擊圖例: 切換顯示/隱藏該數據系列
- 縮放功能: 支援滑鼠滾輪縮放圖表
- 響應式表格: 手機版自動轉為卡片式呈現

---

## 7. 估值模型規格

### 7.1 本益比估值（PER）

**適用標的**:
- 獲利穩定的成熟企業
- 不適用於虧損股、景氣循環股

**計算步驟**:

1. 取得最新 EPS（優先使用 TTM, Trailing Twelve Months）
2. 計算歷史 5 年的本益比數據
3. 剔除異常值（使用 IQR 方法）
4. 計算百分位數（P25, P50, P75）
5. 便宜價 = EPS × P25 PER
6. 合理價 = EPS × P50 PER
7. 昂貴價 = EPS × P75 PER

**公式**:
```
PER = 股價 / EPS
便宜價 = EPS × Percentile(Historical_PER, 25)
合理價 = EPS × Percentile(Historical_PER, 50)
昂貴價 = EPS × Percentile(Historical_PER, 75)
```

**安全邊際計算**:
```
安全邊際 (%) = [(便宜價 - 當前價格) / 當前價格] × 100
```

**範例**:
```
台積電 (2330.TW)
- 最新 EPS: 33.0 元（2025 TTM）
- 歷史 PER P25: 15.0
- 歷史 PER P50: 18.0
- 歷史 PER P75: 22.0

估值結果:
- 便宜價 = 33.0 × 15.0 = 495 元
- 合理價 = 33.0 × 18.0 = 594 元
- 昂貴價 = 33.0 × 22.0 = 726 元

當前價格 625 元 → 位於「合理偏貴」區間
安全邊際 = -20.8%（負值表示高於便宜價）
```

---

### 7.2 股價淨值比估值（PBR）

**適用標的**:
- 資產密集型產業（金融、營建、航運）
- 淨值為正的公司

**計算步驟**:

1. 取得最新 BVPS（每股淨值）
2. 計算歷史 5 年的 PBR 數據
3. 剔除異常值
4. 計算百分位數（P25, P50, P75）
5. 便宜價 = BVPS × P25 PBR
6. 合理價 = BVPS × P50 PBR
7. 昂貴價 = BVPS × P75 PBR

**公式**:
```
PBR = 股價 / BVPS
便宜價 = BVPS × Percentile(Historical_PBR, 25)
```

**範例**:
```
玉山金 (2884.TW)
- 最新 BVPS: 25.0 元
- 歷史 PBR P25: 1.1
- 歷史 PBR P50: 1.3
- 歷史 PBR P75: 1.6

估值結果:
- 便宜價 = 25.0 × 1.1 = 27.5 元
- 合理價 = 25.0 × 1.3 = 32.5 元
- 昂貴價 = 25.0 × 1.6 = 40.0 元
```

---

### 7.3 殖利率估值（Dividend Yield）

**適用標的**:
- 穩定配息的公司
- 金融股、傳產股、ETF

**計算步驟**:

1. 取得近一年股息總和
2. 計算歷史 5 年殖利率數據
3. 計算殖利率百分位數
4. 便宜價 = 年度股息 / P75 殖利率
5. 合理價 = 年度股息 / P50 殖利率
6. 昂貴價 = 年度股息 / P25 殖利率

**公式**:
```
殖利率 (%) = (年度股息 / 股價) × 100
便宜價 = 年度股息 / Percentile(Historical_Yield, 75)
```

**範例**:
```
中華電 (2412.TW)
- 年度股息: 5.0 元
- 歷史殖利率 P25: 4.0%
- 歷史殖利率 P50: 4.5%
- 歷史殖利率 P75: 5.5%

估值結果:
- 便宜價 = 5.0 / 0.055 = 90.9 元
- 合理價 = 5.0 / 0.045 = 111.1 元
- 昂貴價 = 5.0 / 0.040 = 125.0 元
```

---

### 7.4 歷史價格區間估值

**計算邏輯**:

1. 取得過去 N 年的日收盤價（預設 5 年）
2. 計算百分位數（P10, P25, P50, P75, P90）
3. 繪製河流圖

**價格區間定義**:

| 百分位區間 | 定義 | 顏色 |
|-----------|------|------|
| 0-10 | 極度便宜 | 深綠 #059669 |
| 10-25 | 便宜 | 綠色 #10B981 |
| 25-50 | 偏便宜 | 淺綠 #6EE7B7 |
| 50-75 | 偏貴 | 淺黃 #FCD34D |
| 75-90 | 昂貴 | 橙色 #FB923C |
| 90-100 | 極度昂貴 | 紅色 #EF4444 |

**範例輸出**:
```
台積電 (2330.TW) - 5 年歷史價格區間
P10:  450 元
P25:  520 元
P50:  600 元
P75:  680 元
P90:  750 元

當前價格: 625 元
當前百分位: 52% → 偏貴區間
```

---

### 7.5 綜合建議演算法

**評分機制**:

每種估值方法給予 0-100 分:
- 當前價格 < 便宜價: 100 分
- 當前價格介於便宜價與合理價: 75 分
- 當前價格介於合理價與昂貴價: 50 分
- 當前價格 > 昂貴價: 25 分

**權重設定**（可依標的類型調整）:

| 標的類型 | PER 權重 | PBR 權重 | 殖利率權重 | 歷史價格權重 |
|---------|---------|---------|-----------|------------|
| 成長股 | 40% | 20% | 10% | 30% |
| 價值股 | 25% | 30% | 25% | 20% |
| 高股息股 | 15% | 20% | 45% | 20% |
| ETF | 20% | 15% | 35% | 30% |

**最終評級**:

```
加權分數 = Σ (各方法分數 × 權重)

評級規則:
- 加權分數 >= 80: Strong Buy（便宜）
- 加權分數 >= 65: Buy（偏便宜）
- 加權分數 >= 45: Hold（合理）
- 加權分數 >= 30: Avoid（偏貴）
- 加權分數 < 30: Strong Avoid（昂貴）
```

**信心分數**:
```
信心分數 = (有效估值方法數 / 總估值方法數) × 100

例: 若 PER、PBR、殖利率均可計算,但歷史價格不足
信心分數 = (3/4) × 100 = 75
```

---

## 8. 安全需求

### 8.1 資料安全

- **傳輸加密**: 所有 API 使用 HTTPS（TLS 1.3）
- **SQL Injection 防護**: 使用 Prepared Statements
- **XSS 防護**: 前端使用 DOMPurify 清理輸入

### 8.2 API 存取控制

- **Rate Limiting**:
  - 未登入用戶: 每分鐘 20 次請求
  - 登入用戶: 每分鐘 100 次請求
- **API Key**: 外部系統整合需申請 API Key
- **CORS 設定**: 限制允許的來源網域

### 8.3 使用者驗證（未來功能）

- JWT Token 驗證
- OAuth 2.0 整合（Google, Facebook 登入）

### 8.4 數據隱私

- 不儲存個人金融資訊
- 自選清單數據加密儲存
- 符合 GDPR 與台灣個資法

---

## 9. 部署架構

### 9.1 系統架構圖

```
+-------------------+
|   Load Balancer   |
|     (Nginx)       |
+--------+----------+
         |
    +----v----+
    |  React  |  <-- 前端（打包為靜態檔）
    | Frontend|
    +----+----+
         |
    +----v----+
    | Node.js |  <-- 後端 API Server
    | Backend |
    +----+----+
         |
    +----v----+
    |  MySQL  |  <-- 資料庫
    | Database|
    +---------+
         |
    +----v----+
    |  Redis  |  <-- 快取層
    |  Cache  |
    +---------+
```

### 9.2 技術棧

| 層級 | 技術 | 版本 |
|-----|------|------|
| 前端 | React | 18+ |
| 前端路由 | React Router | 6+ |
| 狀態管理 | Redux Toolkit / Zustand | - |
| 圖表庫 | Recharts / Chart.js | - |
| UI 框架 | Tailwind CSS | 3+ |
| 後端 | Node.js + Express | Node 20+ |
| ORM | Sequelize / Prisma | - |
| 資料庫 | MySQL | 8.0+ |
| 快取 | Redis | 7+ |
| 容器化 | Docker + Docker Compose | - |
| API 文件 | Swagger (OpenAPI 3.0) | - |
| 測試 | Jest + React Testing Library | - |

---

### 9.3 Docker Compose 配置

**檔案**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - stock-app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      - NODE_ENV=production
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_USER=stockapp
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=stock_app
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - mysql
      - redis
    networks:
      - stock-app-network

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=stock_app
      - MYSQL_USER=stockapp
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - stock-app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - stock-app-network

volumes:
  mysql-data:

networks:
  stock-app-network:
    driver: bridge
```

---

### 9.4 一鍵啟動腳本

**檔案**: `start.sh`

```bash
#!/bin/bash

echo "========================================"
echo "  Stock App 便宜價分析系統啟動腳本    "
echo "========================================"

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 錯誤: Docker 未啟動,請先啟動 Docker"
    exit 1
fi

# 載入環境變數
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 檔案不存在,使用預設值"
    cp .env.example .env
fi

source .env

# 建置並啟動容器
echo "🚀 正在啟動服務..."
docker-compose up -d --build

# 等待資料庫就緒
echo "⏳ 等待資料庫啟動..."
sleep 10

# 執行資料庫遷移
echo "🔧 執行資料庫遷移..."
docker-compose exec backend npm run migrate

# 匯入初始數據（選填）
echo "📊 匯入初始數據..."
docker-compose exec backend npm run seed

echo ""
echo "✅ 啟動完成!"
echo ""
echo "前端網址: http://localhost:3000"
echo "後端 API: http://localhost:4000"
echo "Swagger 文件: http://localhost:4000/api-docs"
echo ""
echo "查看日誌: docker-compose logs -f"
echo "停止服務: docker-compose down"
echo ""
```

**檔案**: `stop.sh`

```bash
#!/bin/bash

echo "🛑 正在停止 Stock App 服務..."
docker-compose down

echo "✅ 服務已停止"
```

---

### 9.5 環境變數範例

**檔案**: `.env.example`

```env
# Database
MYSQL_ROOT_PASSWORD=your_root_password_here
DB_PASSWORD=your_db_password_here
DB_HOST=mysql
DB_PORT=3306
DB_NAME=stock_app
DB_USER=stockapp

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# API Keys (外部數據源)
YAHOO_FINANCE_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here

# JWT Secret (未來功能)
JWT_SECRET=your_jwt_secret_here

# Node Environment
NODE_ENV=production

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100
```

---

### 9.6 CI/CD 流程（建議）

**GitHub Actions 範例**:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd backend && npm ci
          cd ../frontend && npm ci
      - name: Run tests
        run: |
          cd backend && npm test
          cd ../frontend && npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: docker-compose build
      - name: Push to registry
        run: |
          # 推送至 Docker Hub 或私有 Registry
```

---

## 10. 術語表

| 術語 | 英文 | 說明 |
|-----|------|------|
| 便宜價 | Cheap Price | 根據估值模型計算的低估價位 |
| 合理價 | Fair Price | 根據估值模型計算的合理價位 |
| 昂貴價 | Expensive Price | 根據估值模型計算的高估價位 |
| 本益比 | P/E Ratio (PER) | 股價 ÷ 每股盈餘 |
| 股價淨值比 | P/B Ratio (PBR) | 股價 ÷ 每股淨值 |
| 殖利率 | Dividend Yield | (年度股息 ÷ 股價) × 100% |
| 每股盈餘 | Earnings Per Share (EPS) | 淨利 ÷ 流通股數 |
| 每股淨值 | Book Value Per Share (BVPS) | 股東權益 ÷ 流通股數 |
| TTM | Trailing Twelve Months | 過去 12 個月（滾動計算） |
| 河流圖 | River Chart | 顯示歷史價格百分位區間的視覺化圖表 |
| 安全邊際 | Margin of Safety | (便宜價 - 當前價格) ÷ 當前價格 |
| 百分位數 | Percentile | 統計學中的分位數,如 P25 表示 25% 百分位 |
| 回測 | Backtesting | 使用歷史數據驗證策略有效性 |
| 台股 | Taiwan Stock Exchange (TWSE) | 台灣證券交易所上市股票 |
| 美股 | US Stock | 美國股票市場（NASDAQ, NYSE 等） |

---

## 11. 變更紀錄

| 版本 | 日期 | 作者 | 變更內容 |
|-----|------|------|---------|
| v1.0 | 2026-03-04 | Stock Analytics Expert | 初版建立,包含完整功能需求與技術規格 |

---

## 附錄 A: 數據取得範例程式碼

### Python 範例: 取得台股價格（使用 yfinance）

```python
import yfinance as yf
import pandas as pd

def get_twse_stock_data(symbol: str, period: str = "5y") -> pd.DataFrame:
    """
    取得台股歷史價格

    Args:
        symbol: 股票代號（如 "2330.TW"）
        period: 期間（1y, 5y, 10y）

    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    df.reset_index(inplace=True)
    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

# 使用範例
data = get_twse_stock_data("2330.TW", period="5y")
print(data.head())
```

---

### Node.js 範例: 計算本益比估值

```javascript
const calculatePERValuation = (eps, historicalPERs) => {
  // 剔除異常值（IQR 方法）
  const sorted = historicalPERs.sort((a, b) => a - b);
  const q1 = sorted[Math.floor(sorted.length * 0.25)];
  const q3 = sorted[Math.floor(sorted.length * 0.75)];
  const iqr = q3 - q1;
  const lowerBound = q1 - 1.5 * iqr;
  const upperBound = q3 + 1.5 * iqr;

  const filtered = sorted.filter(per => per >= lowerBound && per <= upperBound);

  // 計算百分位數
  const p25 = filtered[Math.floor(filtered.length * 0.25)];
  const p50 = filtered[Math.floor(filtered.length * 0.50)];
  const p75 = filtered[Math.floor(filtered.length * 0.75)];

  return {
    cheap_price: (eps * p25).toFixed(2),
    fair_price: (eps * p50).toFixed(2),
    expensive_price: (eps * p75).toFixed(2),
    percentiles: { p25, p50, p75 }
  };
};

// 使用範例
const eps = 33.0;
const historicalPERs = [15.2, 16.5, 18.0, 19.2, 22.0, 14.8, 17.5, 20.1];
const valuation = calculatePERValuation(eps, historicalPERs);
console.log(valuation);
```

---

## 附錄 B: Swagger API 定義範例

```yaml
openapi: 3.0.0
info:
  title: Stock App 便宜價分析 API
  version: 1.0.0
  description: 提供股票估值分析與數據查詢服務

servers:
  - url: http://localhost:4000/api/v1
    description: Development server

paths:
  /stocks/search:
    get:
      summary: 搜尋股票標的
      tags:
        - Stocks
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
          description: 搜尋關鍵字（股票代號或名稱）
        - name: market
          in: query
          schema:
            type: string
            enum: [TWSE, NASDAQ, NYSE]
          description: 市場篩選
      responses:
        '200':
          description: 搜尋成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: success
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Stock'

  /stocks/{symbol}/valuation:
    get:
      summary: 取得標的估值分析
      tags:
        - Valuation
      parameters:
        - name: symbol
          in: path
          required: true
          schema:
            type: string
          description: 股票代號（如 2330.TW）
      responses:
        '200':
          description: 估值計算成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValuationResponse'

components:
  schemas:
    Stock:
      type: object
      properties:
        id:
          type: integer
        symbol:
          type: string
        name:
          type: string
        market:
          type: string
        current_price:
          type: number
          format: float

    ValuationResponse:
      type: object
      properties:
        status:
          type: string
        data:
          type: object
          properties:
            stock:
              $ref: '#/components/schemas/Stock'
            valuation:
              type: object
            recommendation:
              type: object
```

---

## 附錄 C: 測試案例範例

### 單元測試範例（Jest）

```javascript
// backend/tests/valuation.test.js

const { calculatePERValuation } = require('../services/valuation');

describe('PER Valuation Calculator', () => {
  test('應正確計算便宜價、合理價、昂貴價', () => {
    const eps = 10.0;
    const historicalPERs = [15, 18, 20, 22, 25];

    const result = calculatePERValuation(eps, historicalPERs);

    expect(result.cheap_price).toBe('150.00');
    expect(result.fair_price).toBe('200.00');
    expect(result.expensive_price).toBe('225.00');
  });

  test('當 EPS 為負數時應返回不適用', () => {
    const eps = -5.0;
    const historicalPERs = [15, 18, 20];

    const result = calculatePERValuation(eps, historicalPERs);

    expect(result.available).toBe(false);
    expect(result.reason).toBe('EPS 為負數,不適用 PER 估值');
  });
});
```

---

## 文件結束

**下一步行動**:
1. 審核本需求文檔
2. 確認技術棧與資源配置
3. 建立專案 Repository
4. 設定開發環境
5. 開始 Sprint Planning

**聯絡資訊**:
- 專案負責人: [待填]
- 技術負責人: [待填]
- 文件維護: Stock Analytics Expert

---

**文件版本控制**:
- 最新版本: v1.0
- 文件位置: `/0_ai_project/stock_app_requirements.md`
- 審核週期: 每月檢視更新

---
