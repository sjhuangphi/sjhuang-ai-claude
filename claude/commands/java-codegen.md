---
name: java-codegen
description: "Java backend code standards and conventions for WPS projects. Use this skill whenever reading, modifying, or generating Java code under /Users/chris-wsd/Tcg/Project/ — including wps-core-module, wps-console-module, wps-3rd-handler-module (V3 Spring Boot), wps-v1-module (V1 WebLogic JAX-RS), and wps-console-v1-module (V1 Console WAR). Applies project-specific patterns for controllers, services, repositories, caches, DTOs, entities, mappers, and exception handling."
---

# Java Code Generation - WPS Project Standards

Generate code that matches the existing codebase structure, style, and architecture.
Before generating, identify which project is being targeted (V3 Spring Boot, V1 WebLogic, or V1 Console).

## Core Principles

1. **Readability first**: Code should be self-documenting; avoid unnecessary abstractions
2. **No over-engineering**: Only implement what is requested; avoid adding speculative features, extra error handling for impossible cases, or premature abstractions
3. **Performance-aware**: Use Virtual Threads (V3), double-layer cache (Caffeine + Redis), and stream operations appropriately
4. **Match existing patterns**: Follow the conventions in `references/conventions.md` exactly

## Project Identification

Determine the target project from context:

| Project | Tech Stack | Base Package |
|---------|-----------|--------------|
| wps-core-module | Java 21, Spring Boot 3.x | `com.tcg.spring.wps.core` |
| wps-console-module | Java 21, Spring Boot 3.x | `com.tcg.spring.wps.console` |
| wps-3rd-handler-module | Java 21, Spring Boot 3.x | `com.tcg.spring.wps.handler3rd` |
| wps-v1-module | Java 8, WebLogic, JAX-RS | `com.tcg.gateway` |
| wps-console-v1-module | Java 8, Spring MVC, WAR, javax.* | `com.tcg.wps.console` |

## Code Generation Process

### Step 1: Understand the requirement
- Identify the target project and layer (Controller / Service / Repository / Cache / Model / TO)
- Clarify if this is a new feature or modification to existing code
- If the project is ambiguous, ask the user

### Step 2: Apply conventions
Load `references/conventions.md` for detailed code patterns. Key rules at a glance:
- Constructor injection with `@RequiredArgsConstructor` + `final` fields (V3)
- `@Slf4j` for logging in Service classes
- Service interface + `Impl` class in `impl/` or `v2/impl/` sub-package
- Repository interface named `I[Entity]Repo`
- Cache class named `[Domain]Cache` under `cache/` package
- TO classes (not DTO) under `to/` package, named `[Action][Entity]TO`
- Error codes: `String` constants in `StatusCode` interface, `lowercase_snake_case`
- Throw `BaseException(StatusCode.XXX, description)` for business errors

### Step 3: Generate code
- Output complete, compilable class files
- Include all necessary imports
- Add `@Schema` annotations to TO fields for Swagger documentation (V3 only)
- Do NOT set `allowableValues` in `@Schema` when the field type is already an enum — Swagger infers the values automatically
- Use `var` for local variables when type is obvious
- Use streams and Optional functionally (no `.get()` without check)

### Step 4: Verify quality checklist
- No field-level `@Autowired`
- No `@Data` on entities (use `@Getter` + `@Setter` separately)
- No `java.util.Date` or `Calendar` (use `LocalDateTime`, `Instant`, `ZonedDateTime`)
- No Hibernate second-level cache in V3 (use Service-layer cache)
- No `@ColumnDefault` on entity fields — production sets `ddl-auto: none`, Hibernate never runs DDL; default values must be defined in SQL migration scripts
- No `javax.persistence` in V3 (use `jakarta.persistence`); wps-console-v1-module still uses `javax.*`
- Error codes in `lowercase_snake_case` or `dot.notation`, not UPPER_CASE
- No `// noinspection` or `@SuppressWarnings` to mask IDE/compiler warnings — fix the root cause instead
- No `@Transient` on TO/DTO fields — it's a JPA annotation, only meaningful on Entity fields
- URL paths use kebab-case, not camelCase (`/facebook-event`, not `/facebookEvent`)
- `@Transactional` only when rollback is needed; never place Kafka sends inside `@Transactional`
- Boolean fields in TOs use primitive `boolean` unless null is intentionally required

## Quick Reference: Annotations by Layer

### V3 (Spring Boot)
- **Controller**: `@RestController`, `@RequestMapping`, `@Slf4j`, `@Validated`, `@Tag`
- **Service**: `@Service`, `@Slf4j`, `@RequiredArgsConstructor`, `@Transactional` (when needed)
- **Cache**: `@Component`, `@Slf4j`, `@RequiredArgsConstructor`, `@Cacheable`, `@CacheEvict`
- **Repository**: extends `JpaRepository` (Entity, Id), interface prefixed with `I`
- **Entity**: `@Entity`, `@Table`, `@Getter`, `@Setter`, `@SequenceGenerator`
- **TO**: `@Getter`, `@Setter`, validation annotations, `@Schema`

### V1 (WebLogic/JAX-RS)
- **Resource**: `@Path`, `@RequestScoped`, `@Api`
- **Service**: CDI beans, field `@Inject` for dependencies
- **Entity**: `@Entity`, `@Table`, `@Cacheable` (Hibernate), manual getter/setter

## Reference Files

- `references/conventions.md` — Detailed code patterns with complete examples for each layer
