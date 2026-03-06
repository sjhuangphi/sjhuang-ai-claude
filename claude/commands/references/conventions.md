# WPS Java 專案程式碼慣例參考

## 目錄結構

### V3 Package 結構
```
com.tcg.spring.wps.[module]/
├── controller/          # REST 控制器
├── service/             # Service 介面
│   ├── impl/            # Service 實作 (或 v2/impl/)
│   └── v2/impl/         # v2 版本實作
├── repository/          # JPA Repository
├── model/               # JPA Entity
├── to/                  # Transfer Objects (輸入 DTO)
│   └── [domain]/        # 按領域分組的 TO
├── cache/               # 快取元件
├── config/              # Spring 配置
├── constant/            # 常數介面
├── mapper/              # MapStruct 對映器
├── client/              # 外部服務 Feign Client
└── utils/               # 工具類別
```

### V1 Package 結構
```
com.tcg.gateway/
├── controller/          # JAX-RS Resource
├── service/
│   └── function/        # 策略模式實作
├── persistence/         # Repository
├── model/               # Entity
├── to/                  # Transfer Objects
└── common/
    ├── constants/
    ├── exception/
    └── utils/
```

---

## Controller 層

### V3 Controller
```java
@Tag(name = "Domain", description = "Domain Management")
@Slf4j
@Validated
@RestController
@RequestMapping(value = "/v2/domain", produces = MediaType.APPLICATION_JSON_VALUE)
public class DomainController {

    private final DomainService domainService;

    public DomainController(DomainService domainService) {
        this.domainService = domainService;
    }

    @Operation(summary = "Get domains by merchant")
    @GetMapping
    public BaseResponseGeneric<List<Domain>> getDomains(
            @RequestHeader(Headers.MERCHANT) String merchantCode) {
        return new BaseResponseGeneric<>(domainService.getDomainsByMerchant(merchantCode));
    }

    @Operation(summary = "Create domain")
    @PostMapping
    public BaseResponse createDomain(
            @RequestHeader(Headers.MERCHANT) String merchantCode,
            @RequestBody @Valid DomainCreateTO request) {
        domainService.addDomain(merchantCode, request);
        return new BaseResponse(true);
    }
}
```

規則：
- 新 API 路徑加 `/v2/` 前綴
- 路徑使用 kebab-case（`-` 分隔），不用 camelCase：`/facebook-event` 而非 `/facebookEvent`
- 用 `@RequestHeader(Headers.MERCHANT)` 取商戶代碼
- 回應用 `BaseResponseGeneric<T>` 或 `BaseResponse`
- `@Validated` 加在 class 層級，`@Valid` 加在 `@RequestBody` 參數

### V1 Resource
```java
@Path("/domain")
@RequestScoped
@Api(value = "/domain", description = "Domain Functions")
public class DomainResource {

    @Inject
    private FunctionsFactory functionsFactory;

    @GET
    @Produces({MediaType.APPLICATION_JSON})
    @ApiOperation(value = "Get Domains")
    public Response getDomains(@HeaderParam(HeaderNames.MERCHANT) String merchant) {
        JsonResponseT<List<Domain>> response = new JsonResponseT<>(true);
        response.setValue(functionsFactory.getFunction(DomainFunctions.class)
                                         .getDomains(merchant));
        return Response.ok(response).build();
    }
}
```

---

## Service 層

### V3 Service 介面
```java
public interface DomainService {
    List<Domain> getDomainsByMerchant(String merchantCode);
    void addDomain(String merchantCode, DomainCreateTO request);
    void deleteDomain(DomainDeleteTO request);
}
```

### V3 Service 實作
```java
@Slf4j
@Service
@RequiredArgsConstructor
public class DomainServiceImpl implements DomainService {

    private static final int ACTIVE_STATUS = 1;  // 類別常數放 class 頂部

    private final IDomainRepo iDomainRepo;
    private final DomainCache domainCache;
    private final AdminService adminService;

    @Override
    public List<Domain> getDomainsByMerchant(String merchantCode) {
        return iDomainRepo.findByMerchant(merchantCode);
    }

    @Override
    @Transactional
    public void addDomain(String merchantCode, DomainCreateTO request) {
        String operator = adminService.getOperatorNameOrSystem();

        var domain = new Domain();
        domain.setMerchantCode(merchantCode);
        domain.setDomainName(request.getDomainName());
        domain.setStatus(ACTIVE_STATUS);
        domain.setCreateOperator(operator);

        iDomainRepo.save(domain);
        domainCache.evictCaches(merchantCode);

        log.info("domain created: merchantCode={}, domain={}", merchantCode, request.getDomainName());
    }
}
```

規則：
- `@RequiredArgsConstructor` + `final` 欄位取代 `@Autowired`
- `@Slf4j` 提供 `log` 變數
- 類別常數（`private static final`）放在欄位宣告之前
- Transaction 只在需要資料庫寫入且有 rollback 需求時加 `@Transactional`
- 若整個 Service 都不需要 Transaction，加 `@Transactional(propagation = Propagation.NOT_SUPPORTED)`
- 單純查詢或不需要 rollback 的更新方法**不要加** `@Transactional`，避免不必要的事務開銷

### `@Transactional` 禁止情境

**1. 無 rollback 需求的方法不加**
```java
// Bad: 只是呼叫 RPC 更新，無需 rollback
@Transactional
@Override
public void updateCloakingEnabled(String merchantCode, Integer linkId, Boolean enabled) {
    ...
}

// Good: 移除 @Transactional
@Override
public void updateCloakingEnabled(String merchantCode, Integer linkId, Boolean enabled) {
    ...
}
```

**2. `@Transactional` 方法內不能發送 Kafka**
> DB 事務尚未提交，Kafka 訊息卻先送出；若事務回滾，Kafka 訊息無法撤回，造成資料不一致。
> 應改用 `@TransactionalEventListener` 在事務提交後觸發。
```java
// Bad: 事務還沒提交就發 Kafka
@Transactional
public void save(Entity entity) {
    repo.save(entity);
    kafkaProducer.send(event);  // 危險！
}

// Good: 透過 Spring Event 在事務提交後發送
@Transactional
public void save(Entity entity) {
    repo.save(entity);
    applicationEventPublisher.publishEvent(new EntitySavedEvent(entity));
}

@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void onEntitySaved(EntitySavedEvent event) {
    kafkaProducer.send(event);
}
```

**3. 分批處理方法不可套整體事務**
```java
// Bad: @Transactional 包住整個分批迴圈，等於一個超大事務
@Transactional
public void patchConfigs() {
    var page = 1;
    while (...) {
        processBatch(...);  // 分批失去意義
    }
}

// Good: 事務只包在單批處理方法
public void patchConfigs() {
    var page = 1;
    while (...) {
        processBatch(...);
    }
}

@Transactional
protected void processBatch(List<Entity> batch) {
    ...
}
```

### Service 命名
- 介面: `DomainService`
- 實作: `DomainServiceImpl`（在 `service/impl/` 或 `service/v2/impl/`）

---

## Repository 層

### V3 Repository 介面
```java
public interface IGwDomainRepo extends JpaRepository<GwDomain, Integer> {

    List<GwDomain> findByMerchantCode(String merchantCode);

    Optional<GwDomain> findByMerchantCodeAndDomainName(String merchantCode, String domainName);

    @Query("SELECT d FROM GwDomain d WHERE d.merchantCode = ?1 AND d.status = 1")
    List<GwDomain> findActiveDomains(String merchantCode);
}
```

規則：
- 介面名稱 `I[Entity]Repo`，以大寫 `I` 開頭
- 繼承 `JpaRepository<Entity, IdType>`
- 簡單查詢用 Spring Data 命名慣例方法
- 複雜查詢用 `@Query` + JPQL（V3 用 `jakarta.persistence`）
- 占位符用 `?1`, `?2` 或 `:paramName`
- **只需要特定欄位時，使用投影（projection），勿撈完整 Entity**

```java
// Bad: 只需要 ID，卻撈出整個 Entity
List<GwRegisterField> fields = iRegisterFieldRepo.findByMerchantCode(merchantCode);
fields.stream().map(GwRegisterField::getFieldId).collect(Collectors.toList());

// Good: 直接投影只取 ID
@Query("SELECT r.fieldId FROM GwRegisterField r WHERE r.merchantCode = ?1")
List<Long> findFieldIdsByMerchantCode(String merchantCode);
```

### QueryDSL 自訂查詢（複雜情境）
```java
@Repository
@RequiredArgsConstructor
public class DomainRepo {

    private final JPAQueryFactory queryFactory;

    public List<GwDomain> findByFilters(String merchantCode, Integer status, String keyword) {
        var domain = QGwDomain.gwDomain;

        var predicate = domain.merchantCode.eq(merchantCode)
            .and(status != null ? domain.status.eq(status) : null)
            .and(StringUtils.isNotBlank(keyword) ? domain.domainName.containsIgnoreCase(keyword) : null);

        return queryFactory.selectFrom(domain)
            .where(predicate)
            .orderBy(domain.createTime.desc())
            .fetch();
    }
}
```

---

## Cache 層

### V3 Cache 元件
```java
@Slf4j
@Component
@RequiredArgsConstructor
public class DomainCache {

    private final IGwDomainRepo iGwDomainRepo;
    private final CachingService cachingService;

    @Cacheable(cacheNames = CacheConstant.DOMAIN, key = "#merchantCode")
    public List<GwDomain> getByMerchant(String merchantCode) {
        return iGwDomainRepo.findByMerchantCode(merchantCode);
    }

    @CacheEvict(cacheNames = CacheConstant.DOMAIN, allEntries = true)
    public void evictAllCaches() {
    }

    public void evictCaches(String merchantCode) {
        log.info("clean domain cache by merchant: {}", merchantCode);
        cachingService.evictCacheByKeyPrefix(CacheConstant.DOMAIN, merchantCode);
    }
}
```

規則：
- Cache 類別名稱：`[Domain]Cache`
- `@Cacheable` 的 `cacheNames` 用 `CacheConstant` 介面中的常數
- 提供按商戶清除（精準）和全量清除兩種方法
- Cache 本身不做業務邏輯，只負責查詢和快取管理

### CacheConstant 新增常數
```java
public interface CacheConstant {
    // 在此新增
    String DOMAIN = "domain";
    String PARAMETERS = "parameters";
}
```

快取名稱格式：`小寫 kebab-case`（例：`domain-route`, `register-field-map`）

---

## Entity (Model) 層

### V3 Entity
```java
@Entity
@Getter
@Setter
@Table(name = "GW_DOMAIN")
@SequenceGenerator(name = "SEQ_GW_DOMAIN", sequenceName = "SEQ_GW_DOMAIN", allocationSize = 1)
public class GwDomain extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "SEQ_GW_DOMAIN")
    @Column(name = "DOMAIN_ID")
    private Integer domainId;

    @Column(name = "MERCHANT_CODE")
    private String merchantCode;

    @Column(name = "DOMAIN_NAME")
    private String domainName;

    @Column(name = "STATUS")
    private Integer status;

    @Column(name = "CREATE_OPERATOR")
    private String createOperator;

    @Column(name = "UPDATE_OPERATOR")
    private String updateOperator;
}
```

規則：
- Entity 名稱通常加 `Gw` 前綴（例：`GwDomain`, `GwParameter`）
- 使用 `@Getter` + `@Setter`，不用 `@Data`（避免 `equals`/`hashCode` 問題）
- Oracle Sequence：`@SequenceGenerator` + `allocationSize = 1`
- Column 名稱用全大寫 `SNAKE_CASE`
- 繼承 `BaseEntity`（含 `createTime`, `updateTime` 等共用欄位）
- V3 用 `jakarta.persistence.*`，不用 `javax.persistence.*`

### V1 Entity
```java
@Entity
@Table(name = "GW_DOMAIN")
@Cacheable  // V1 允許 Hibernate 二級快取
public class GwDomain extends WpsBaseEntity {

    @Id
    @Column(name = "DOMAIN_ID")
    private Integer domainId;

    @Column(name = "DOMAIN_NAME")
    private String domainName;

    // V1 手寫 getter/setter
    public Integer getDomainId() { return domainId; }
    public void setDomainId(Integer domainId) { this.domainId = domainId; }
    public String getDomainName() { return domainName; }
    public void setDomainName(String domainName) { this.domainName = domainName; }
}
```

---

## TO (Transfer Object) 層

### 輸入 TO（請求物件）
```java
@Getter
@Setter
public class DomainCreateTO {

    @NotNull
    @Schema(description = "商戶代碼", example = "merchant001")
    private String merchantCode;

    @NotBlank
    @Pattern(regexp = "^(?!www\\.)(?!https?://).*")
    @Schema(description = "根域名", example = "example.com")
    private String rootDomain;

    @NotNull
    @Range(min = 0, max = 1)
    @Schema(description = "狀態: Off=0, On=1", example = "1")
    private Integer status;

    @Schema(description = "備註")
    private String remark;
}
```

規則：
- 命名後綴：`TO`（不用 DTO、VO、Request）
- 放在 `to/` 套件下，按領域分子資料夾（例：`to/domain/DomainCreateTO.java`）
- 只用 `@Getter` + `@Setter`，不用 `@Data`
- V3 必加 `@Schema` 描述欄位（Swagger 文件）
- 驗證 annotation：`@NotNull`, `@NotBlank`, `@Valid`, `@Pattern`, `@Range`
- 不使用 `@Transient`：TO 不是 JPA Entity，此 annotation 在此無效
- 布林欄位**預設用原始型 `boolean`**，不用包裝型 `Boolean`；`boolean` + `@NotNull` 是語義矛盾
```java
// Bad
@NotNull
private Boolean enabled;   // 三態語義，@NotNull 多餘

// Good
private boolean enabled;   // 二態，明確不允許 null
```

### 分頁查詢 TO
```java
@Getter
@Setter
public class DomainQueryTO extends SpringPageDecodeTO {

    @Schema(description = "商戶代碼")
    private String merchantCode;

    @Schema(description = "域名關鍵字")
    private String keyword;

    @Schema(description = "狀態")
    private Integer status;
}
```

---

## Exception 處理

### 拋出業務例外
```java
// 使用 StatusCode 常數 + 說明訊息
throw new BaseException(StatusCode.DOMAIN_NOT_FOUND, "domain not found: " + domainName);

// 特定例外類別（已存在時使用）
throw new SysIsBusyException("concurrent update conflict");
```

### StatusCode 定義
```java
public interface StatusCode extends CoreStatusCode {

    // 命名格式：lowercase_snake_case
    String DOMAIN_NOT_FOUND = "domain_not_found";
    String DOMAIN_ALREADY_EXISTS = "domain_already_exists";
    String INVALID_DOMAIN_FORMAT = "invalid_domain_format";

    // 部分舊有使用 dot.notation（維持相容性，新增請用 underscore）
    String LOGIN_IP_RESTRICTED = "login.ip.restricted";
}
```

---

## 常數定義

### 快取常數（CacheConstant.java）
```java
public interface CacheConstant {
    String DOMAIN = "domain";
    String DOMAIN_ROUTE = "domain-route";
}
```

### Redis 快取常數（RedisCacheConstant.java）
```java
public interface RedisCacheConstant {
    String LOGIN_ATTEMPTS = "login-attempts";
    String REGISTER_ATTEMPTS = "register-attempts";
}
```

### Enum 常數
```java
public enum DomainType {
    MAIN_DOMAIN(0, "主域名"),
    APP_ANDROID_APK(1, "Android APK"),
    AGENT_DOMAIN(2, "代理線路");

    private final int code;
    private final String description;

    DomainType(int code, String description) {
        this.code = code;
        this.description = description;
    }

    public int getCode() { return code; }
    public String getDescription() { return description; }
}
```

---

## 常用寫法模式

### Optional 函數式鏈
```java
// 正確
return userRepo.findById(userId)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown");

// 避免
Optional<User> opt = userRepo.findById(userId);
if (opt.isPresent()) {
    return opt.get().getAddress().getCity();
}
return "Unknown";
```

### Stream 操作
```java
// 收集為 Map（用 Function.identity()）
Map<String, GwDomain> domainMap = domains.stream()
    .collect(Collectors.toMap(GwDomain::getDomainName, Function.identity()));

// 分組
Map<String, List<GwDomain>> byMerchant = domains.stream()
    .collect(Collectors.groupingBy(GwDomain::getMerchantCode));

// 過濾 + 轉換
List<String> activeNames = domains.stream()
    .filter(d -> d.getStatus() == 1)
    .map(GwDomain::getDomainName)
    .collect(Collectors.toList());
```

### var 關鍵字使用（V3/Java 10+）
```java
// 可用：型別從右側可明顯推斷
var domains = iDomainRepo.findByMerchantCode(merchantCode);
var predicate = domain.merchantCode.eq(merchantCode);

// 不建議：右側不明顯或基本型別
var count = 0;  // 直接寫 int count = 0;
```

### 日期時間
```java
// 正確（Java 8+ 新型別）
LocalDateTime now = LocalDateTime.now();
Instant instant = Instant.now();
ZonedDateTime zonedNow = ZonedDateTime.now(ZoneId.of("Asia/Taipei"));

// 避免（舊型別）
Date date = new Date();
Calendar cal = Calendar.getInstance();
```

### 非同步處理（V3）
```java
@Service
@RequiredArgsConstructor
public class NotificationService {

    @Async
    public void sendNotificationAsync(String merchantCode, String message) {
        // Virtual Thread 執行，不阻塞主執行緒
        log.info("sending notification: merchantCode={}", merchantCode);
        // ... 實際發送邏輯
    }
}
```

### 分頁查詢
```java
public Page<GwDomain> queryDomains(DomainQueryTO query) {
    Pageable pageable = PageRequest.of(
        query.getPage(),
        query.getSize(),
        Sort.by(Sort.Direction.DESC, "createTime")
    );
    return iDomainRepo.findByFilters(query.getMerchantCode(), query.getStatus(), pageable);
}
```

### 驗證邏輯前置（Fail-Fast）

驗證必須在業務邏輯**執行前**統一完成，不可在迴圈中途拋錯，避免產生中間態。

```java
// Bad: 迴圈跑到一半才驗證，部分資料已被處理
public void updateMappings(List<EventMappingTO> toUpdate) {
    for (var item : toUpdate) {
        if (item.getEventName() == null) {
            throw new BaseException(StatusCode.INVALID_PARAMETER, "eventName required");
        }
        repo.save(mapper.toEntity(item));
    }
}

// Good: 先統一驗證，再執行業務邏輯
public void updateMappings(List<EventMappingTO> toUpdate) {
    validateMappings(toUpdate);  // 前置驗證，全部通過才繼續
    for (var item : toUpdate) {
        repo.save(mapper.toEntity(item));
    }
}

private void validateMappings(List<EventMappingTO> items) {
    for (var item : items) {
        if (item.getEventName() == null) {
            throw new BaseException(StatusCode.INVALID_PARAMETER, "eventName required");
        }
    }
}
```

### Stream 複雜轉換 vs 直接迭代

Map 反轉、多層 grouping 等複雜轉換，直接迭代比 Stream 更高效且可讀：

```java
// Bad: 兩次遍歷 + 臨時物件開銷
Map<String, List<String>> domainMerchants = merchantDomains.entrySet().stream()
    .flatMap(e -> e.getValue().stream()
        .map(domain -> Map.entry(domain, e.getKey())))
    .collect(Collectors.groupingBy(
        Map.Entry::getKey,
        Collectors.mapping(Map.Entry::getValue, Collectors.toList())
    ));

// Good: 單次迭代，直接 computeIfAbsent
Map<String, List<String>> domainMerchants = new HashMap<>();
merchantDomains.forEach((merchant, domains) ->
    domains.forEach(domain ->
        domainMerchants.computeIfAbsent(domain, k -> new ArrayList<>()).add(merchant)
    )
);
```

### 可重用格式常數

執行緒安全且不可變的物件（如 `DateTimeFormatter`）應提取為 `static final` 常數，不要在方法內重複建立：

```java
// Bad: 每次呼叫都建立新物件
public String formatTime(LocalDateTime ldt) {
    return ldt.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
}

// Good: static final 常數
private static final DateTimeFormatter DATE_TIME_FMT =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

public String formatTime(LocalDateTime ldt) {
    return ldt.format(DATE_TIME_FMT);
}
```

---

## Lombok 使用規則

| Annotation | 使用場景 |
|------------|---------|
| `@Getter` | Entity、TO、VO 類別 |
| `@Setter` | Entity、TO 類別 |
| `@Slf4j` | Service、Controller 等需要 logging |
| `@RequiredArgsConstructor` | Service、Controller（搭配 `final` 欄位） |
| `@Builder` | 複雜物件建構（謹慎使用） |

不使用：
- `@Data`（包含 `@ToString`、`@EqualsAndHashCode`，Entity 可能造成問題）
- `@AllArgsConstructor`、`@NoArgsConstructor`（Entity 除外）

---

## Import 順序

V3 標準 import 群組（依序）：
1. `java.*`
2. `jakarta.*`（不是 `javax.*`）
3. `org.springframework.*`
4. `lombok.*`
5. `com.tcg.spring.*`（專案內部）
6. 其他第三方（`org.apache.*`, `com.google.*` 等）

常用工具類：
- `org.apache.commons.lang3.StringUtils`（字串處理）
- `org.apache.commons.collections4.CollectionUtils`（集合處理）
- `com.google.common.collect.*`（Guava）

---

## 命名慣例總覽

| 類型 | 格式 | 範例 |
|------|------|------|
| 類別名 | PascalCase | `DomainServiceImpl` |
| 方法名 | camelCase | `getDomainsByMerchant` |
| 變數名 | camelCase | `merchantCode` |
| 常數名 | UPPER_SNAKE_CASE | `ACTIVE_STATUS = 1` |
| 錯誤碼 | lowercase_snake_case | `domain_not_found` |
| 快取名 | lowercase-kebab-case | `domain-route` |
| DB 表名 | UPPER_SNAKE_CASE | `GW_DOMAIN` |
| DB 欄名 | UPPER_SNAKE_CASE | `MERCHANT_CODE` |
