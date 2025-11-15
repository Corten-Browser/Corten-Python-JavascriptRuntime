# ES2024 Wave B - Implementation Plan

**Date:** 2025-11-15
**Status:** Ready for Execution
**Wave:** Wave B (Advanced Features - MEDIUM PRIORITY)
**Version:** 0.1.0

---

## Executive Summary

Wave B focuses on **advanced ES2024 features** to increase compliance from ~80-90% to ~95%+ coverage.

**Target:**
- **8 components** with **~60 requirements**
- **Estimated Test262 Coverage:** +10,000 tests
- **Estimated Effort:** 130-160 hours
- **Parallel Execution:** 7 concurrent agents (max from config)

---

## Wave B Components Overview

| # | Component | Requirements | Estimated Effort | Priority | Test262 Tests |
|---|-----------|--------------|------------------|----------|---------------|
| 1 | regexp_advanced_features | 10 | 25-30h | HIGH | ~800 |
| 2 | class_static_blocks | 4 | 10-12h | MEDIUM | ~150 |
| 3 | error_extensions | 5 | 10-12h | MEDIUM | ~80 |
| 4 | dataview_complete | 8 | 12-15h | MEDIUM | ~150 |
| 5 | weakref_finalization | 6 | 15-20h | MEDIUM | ~100 |
| 6 | json_extensions | 5 | 8-10h | LOW | ~100 |
| 7 | function_edge_cases | 8 | 10-15h | MEDIUM | ~200 |
| 8 | strict_mode_complete | 14 | 15-20h | HIGH | ~1,000 |
| **TOTAL** | **8** | **60** | **130-160h** | - | **~2,580** |

**Plus indirect Test262 coverage:** ~7,500 additional tests
**Total estimated Test262 impact:** ~10,000 tests

---

## Component 1: regexp_advanced_features

**Requirements:** 10 (FR-ES24-B-001 to FR-ES24-B-010)
**Estimated Effort:** 25-30 hours
**Priority:** HIGH (ES2024 RegExp completeness)
**Test262 Tests:** ~800 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-001 | Named capture groups | `(?<name>...)` syntax | ≥15 |
| FR-ES24-B-002 | Unicode property escapes | `\p{...}` and `\P{...}` | ≥20 |
| FR-ES24-B-003 | Lookbehind assertions | `(?<=...)` and `(?<!...)` | ≥15 |
| FR-ES24-B-004 | dotAll flag (s) | `.` matches newlines | ≥10 |
| FR-ES24-B-005 | Indices flag (d) | Match indices in results | ≥12 |
| FR-ES24-B-006 | Set notation in /v flag | Advanced set operations | ≥18 |
| FR-ES24-B-007 | String properties in /v | Unicode property syntax | ≥15 |
| FR-ES24-B-008 | RegExp.prototype.flags | Getter for all flags | ≥8 |
| FR-ES24-B-009 | Unicode mode (/u) edge cases | Surrogate pairs, properties | ≥12 |
| FR-ES24-B-010 | RegExp.prototype[@@match/@@matchAll] | Correct symbol method behavior | ≥10 |

**Total Tests:** ≥135 tests

**Dependencies:**
- parser (RegExp AST extensions)
- shared_types (RegExpNode updates)
- object_runtime (RegExp prototype methods)

**Performance Targets:**
- Pattern compilation: <5ms for complex patterns
- Match execution: <1ms for typical inputs
- Unicode property lookup: O(log n)

---

## Component 2: class_static_blocks

**Requirements:** 4 (FR-ES24-B-011 to FR-ES24-B-014)
**Estimated Effort:** 10-12 hours
**Priority:** MEDIUM (ES2022 class enhancement)
**Test262 Tests:** ~150 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-011 | Static initialization blocks | `static { ... }` syntax | ≥15 |
| FR-ES24-B-012 | Static block execution order | Runs after static fields | ≥10 |
| FR-ES24-B-013 | Static block this binding | `this` refers to class constructor | ≥8 |
| FR-ES24-B-014 | Static block private access | Can access private static fields | ≥12 |

**Total Tests:** ≥45 tests

**Dependencies:**
- parser (static block syntax)
- private_class_features (private static access)
- interpreter (static block execution)

**Performance Targets:**
- Static block execution: <1ms per block
- Initialization overhead: <10% of class creation time

**Note:** Partial implementation may exist in private_class_features - verify and extend.

---

## Component 3: error_extensions

**Requirements:** 5 (FR-ES24-B-015 to FR-ES24-B-019)
**Estimated Effort:** 10-12 hours
**Priority:** MEDIUM (ES2021 error improvements)
**Test262 Tests:** ~80 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-015 | AggregateError | Error for multiple failures | ≥12 |
| FR-ES24-B-016 | AggregateError.errors property | Array of aggregated errors | ≥8 |
| FR-ES24-B-017 | Error.prototype.stack | Stack trace property | ≥10 |
| FR-ES24-B-018 | Stack trace formatting | Human-readable stack traces | ≥8 |
| FR-ES24-B-019 | Error subclass stack traces | Stack traces for all Error types | ≥7 |

**Total Tests:** ≥45 tests

**Dependencies:**
- value_system (AggregateError type)
- interpreter (stack trace generation)
- object_runtime (Error prototype)

**Performance Targets:**
- AggregateError creation: <1ms
- Stack trace generation: <2ms
- Stack trace formatting: <5ms

---

## Component 4: dataview_complete

**Requirements:** 8 (FR-ES24-B-020 to FR-ES24-B-027)
**Estimated Effort:** 12-15 hours
**Priority:** MEDIUM (Binary data handling)
**Test262 Tests:** ~150 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-020 | DataView constructor | Create view on ArrayBuffer | ≥10 |
| FR-ES24-B-021 | DataView get methods | getInt8, getUint8, ..., getFloat64 | ≥30 |
| FR-ES24-B-022 | DataView set methods | setInt8, setUint8, ..., setFloat64 | ≥30 |
| FR-ES24-B-023 | DataView endianness | Little-endian and big-endian support | ≥15 |
| FR-ES24-B-024 | DataView boundary checks | Throw on out-of-bounds access | ≥10 |
| FR-ES24-B-025 | DataView with offset/length | Partial buffer views | ≥12 |
| FR-ES24-B-026 | DataView detached buffer | Throw on detached buffer access | ≥8 |
| FR-ES24-B-027 | DataView properties | buffer, byteOffset, byteLength | ≥10 |

**Total Tests:** ≥125 tests

**Dependencies:**
- typed_arrays (ArrayBuffer, detached buffer handling)
- memory_gc (buffer allocation)
- value_system (DataView type)

**Performance Targets:**
- DataView creation: <1µs
- Get/set operations: <10ns per operation
- Boundary checking: No performance penalty

---

## Component 5: weakref_finalization

**Requirements:** 6 (FR-ES24-B-028 to FR-ES24-B-033)
**Estimated Effort:** 15-20 hours
**Priority:** MEDIUM (ES2021 advanced memory management)
**Test262 Tests:** ~100 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-028 | WeakRef constructor | Create weak reference to object | ≥10 |
| FR-ES24-B-029 | WeakRef.prototype.deref() | Dereference weak ref (or undefined) | ≥12 |
| FR-ES24-B-030 | WeakRef GC behavior | Object collected when no strong refs | ≥10 |
| FR-ES24-B-031 | FinalizationRegistry constructor | Create finalization registry | ≥10 |
| FR-ES24-B-032 | FinalizationRegistry.register() | Register cleanup callback | ≥15 |
| FR-ES24-B-033 | FinalizationRegistry cleanup | Callback invoked on GC | ≥12 |

**Total Tests:** ≥69 tests

**Dependencies:**
- memory_gc (GC integration, weak references)
- event_loop (cleanup callback scheduling)
- value_system (WeakRef, FinalizationRegistry types)

**Performance Targets:**
- WeakRef creation: <1µs
- Deref operation: <10ns
- Registry registration: <1µs
- Cleanup callback latency: <10ms after GC

**Implementation Notes:**
- Requires integration with memory_gc's GC cycle
- Cleanup callbacks run as microtasks
- Must not prevent GC of registered objects

---

## Component 6: json_extensions

**Requirements:** 5 (FR-ES24-B-034 to FR-ES24-B-038)
**Estimated Effort:** 8-10 hours
**Priority:** LOW (JSON API improvements)
**Test262 Tests:** ~100 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-034 | JSON.parse reviver improvements | Reviver function enhancements | ≥12 |
| FR-ES24-B-035 | JSON.stringify replacer improvements | Replacer function enhancements | ≥12 |
| FR-ES24-B-036 | Well-formed JSON.stringify | Proper Unicode surrogate handling | ≥10 |
| FR-ES24-B-037 | JSON.stringify space parameter | Proper indentation handling | ≥8 |
| FR-ES24-B-038 | JSON edge cases | Circular reference detection, etc. | ≥10 |

**Total Tests:** ≥52 tests

**Dependencies:**
- object_runtime (JSON object)
- value_system (type conversions)

**Performance Targets:**
- JSON.parse: <1ms per KB
- JSON.stringify: <2ms per KB
- Circular detection: O(n) time complexity

---

## Component 7: function_edge_cases

**Requirements:** 8 (FR-ES24-B-039 to FR-ES24-B-046)
**Estimated Effort:** 10-15 hours
**Priority:** MEDIUM (Function API completeness)
**Test262 Tests:** ~200 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-039 | Function.prototype.name edge cases | Name inference for all function types | ≥15 |
| FR-ES24-B-040 | Function.prototype.toString() | Source code revelation | ≥12 |
| FR-ES24-B-041 | Function.prototype.bind() edge cases | Bound function behavior | ≥10 |
| FR-ES24-B-042 | Function.prototype.call/apply edge cases | Proper this binding and arguments | ≥12 |
| FR-ES24-B-043 | Function length property | Correct parameter count | ≥10 |
| FR-ES24-B-044 | Arrow function this binding | Lexical this in all contexts | ≥12 |
| FR-ES24-B-045 | Function constructor edge cases | Dynamic function creation | ≥10 |
| FR-ES24-B-046 | Generator function edge cases | Generator name, toString, etc. | ≥10 |

**Total Tests:** ≥91 tests

**Dependencies:**
- object_runtime (Function prototype)
- interpreter (function execution)
- parser (function name inference)

**Performance Targets:**
- Name inference: <1µs
- toString: <10µs
- Bind operation: <1µs

---

## Component 8: strict_mode_complete

**Requirements:** 14 (FR-ES24-B-047 to FR-ES24-B-060)
**Estimated Effort:** 15-20 hours
**Priority:** HIGH (Spec compliance)
**Test262 Tests:** ~1,000 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-B-047 | "use strict" directive | Proper detection and propagation | ≥15 |
| FR-ES24-B-048 | Strict mode assignment errors | Throw on assignment to undeclared | ≥12 |
| FR-ES24-B-049 | Strict mode deletion errors | Throw on delete of unqualified identifier | ≥10 |
| FR-ES24-B-050 | Strict mode duplicate parameters | Throw on duplicate formal parameters | ≥10 |
| FR-ES24-B-051 | Strict mode octal literals | Throw on octal literals (0777) | ≥8 |
| FR-ES24-B-052 | Strict mode eval/arguments | Restrictions on eval and arguments | ≥15 |
| FR-ES24-B-053 | Strict mode this binding | undefined this in function calls | ≥12 |
| FR-ES24-B-054 | Strict mode with statement | Throw on 'with' statement | ≥8 |
| FR-ES24-B-055 | Strict mode reserved words | Future reserved words restrictions | ≥10 |
| FR-ES24-B-056 | Strict mode caller/callee | Throw on arguments.caller/callee | ≥10 |
| FR-ES24-B-057 | Strict mode assignment to readonly | Throw on assignment to readonly props | ≥12 |
| FR-ES24-B-058 | Strict mode function declarations | Function declarations in blocks | ≥10 |
| FR-ES24-B-059 | Strict mode scope propagation | Propagate to nested functions | ≥10 |
| FR-ES24-B-060 | Strict mode edge cases | All remaining strict mode semantics | ≥15 |

**Total Tests:** ≥157 tests

**Dependencies:**
- parser (strict mode detection)
- interpreter (strict mode enforcement)
- object_runtime (strict mode errors)

**Performance Targets:**
- Strict mode checking: <1% performance overhead
- Error throwing: <1µs

**Implementation Notes:**
- Requires parser changes to track strict mode context
- Interpreter must check strict mode at runtime for certain operations
- Many violations are parse-time errors

---

## Dependencies Between Wave B Components

```
graph TD
    regexp_advanced_features --> parser
    regexp_advanced_features --> object_runtime

    class_static_blocks --> parser
    class_static_blocks --> private_class_features

    error_extensions --> value_system
    error_extensions --> interpreter

    dataview_complete --> typed_arrays
    dataview_complete --> memory_gc

    weakref_finalization --> memory_gc
    weakref_finalization --> event_loop

    json_extensions --> object_runtime

    function_edge_cases --> object_runtime
    function_edge_cases --> parser

    strict_mode_complete --> parser
    strict_mode_complete --> interpreter
```

**Build Order (Topological Sort):**

**Wave 1 (No Wave B dependencies, can start immediately):**
1. regexp_advanced_features
2. error_extensions
3. dataview_complete
4. json_extensions
5. function_edge_cases
6. strict_mode_complete
7. weakref_finalization

**Wave 2 (After Wave 1):**
8. class_static_blocks (depends on private_class_features which was Wave A)

**All components can start in parallel** since they depend only on existing infrastructure from Waves A or earlier phases.

---

## Execution Strategy

### Phase 1: Contract Generation (Parallel)
**Duration:** 2-3 hours
**Approach:** Generate all 8 component contracts simultaneously

```bash
# Generate contracts for all Wave B components
contracts/regexp_advanced_features.yaml
contracts/class_static_blocks.yaml
contracts/error_extensions.yaml
contracts/dataview_complete.yaml
contracts/weakref_finalization.yaml
contracts/json_extensions.yaml
contracts/function_edge_cases.yaml
contracts/strict_mode_complete.yaml
```

### Phase 2: Parallel Implementation
**Duration:** 25-30 hours (longest agent: regexp_advanced_features)
**Max Concurrent Agents:** 7 (from orchestration config)

**Batch 1 (Launch immediately - 7 agents):**
1. regexp_advanced_features (25-30h)
2. strict_mode_complete (15-20h)
3. weakref_finalization (15-20h)
4. dataview_complete (12-15h)
5. function_edge_cases (10-15h)
6. class_static_blocks (10-12h)
7. error_extensions (10-12h)

**Batch 2 (Launch when slot opens - 1 agent):**
8. json_extensions (8-10h)

**Execution Timeline:**
- Batch 1: All 7 agents start simultaneously
- As agents complete, json_extensions launches
- Total elapsed time: ~25-30 hours (duration of longest agent)

### Phase 3: Quality Verification
**Duration:** 3-4 hours

For each component:
1. Run 12-check verification (v0.5.0)
   - Tests pass (100% pass rate)
   - Imports resolve
   - No stubs
   - No TODOs
   - Documentation complete
   - No work markers
   - Test coverage ≥80%
   - Manifest complete
   - Defensive programming
   - Semantic correctness
   - Contract compliance
   - Test quality
2. Verify TDD compliance (git history analysis)
3. Check contract compliance
4. Run defensive pattern checker
5. Run semantic verifier

### Phase 4: Integration Testing
**Duration:** 2-3 hours

1. Run cross-component integration tests
2. Verify no regressions in Wave A components
3. Run Test262 conformance suite for Wave B categories
4. Generate compliance report

---

## Success Criteria

### Functional
- ✅ All 60 Wave B requirements implemented
- ✅ All components pass 12-check verification
- ✅ 100% test pass rate (component tests)
- ✅ 100% integration test pass rate
- ✅ Test262 pass rate increases by ~10,000 tests

### Quality
- ✅ All components ≥80% test coverage
- ✅ TDD methodology followed (Red-Green-Refactor)
- ✅ Contract-first development
- ✅ No critical quality gate failures
- ✅ Defensive programming patterns verified
- ✅ Semantic correctness verified

### Performance
- ✅ No performance regressions
- ✅ Wave B features optimized where applicable
- ✅ Maintain Phase 4 optimization infrastructure

---

## Test262 Integration

### Expected Test262 Improvement

**Current (after Wave A):** ~40,000-45,000 / 50,000 passing (80-90%)
**After Wave B:** ~47,000-48,000 / 50,000 passing (94-96%)
**Target:** >48,000 / 50,000 passing (>96%)

### Test Categories Covered by Wave B

- **built-ins/RegExp/** (~800 tests)
- **language/expressions/class/static-init/** (~150 tests)
- **built-ins/AggregateError/** (~80 tests)
- **built-ins/DataView/** (~150 tests)
- **built-ins/WeakRef/** (~100 tests)
- **built-ins/JSON/** (~100 tests)
- **built-ins/Function/prototype/** (~200 tests)
- **language/directive-prologue/** (strict mode: ~1,000 tests)

**Total Direct Coverage:** ~2,580 Test262 tests
**Indirect Coverage:** ~7,500 tests (strict mode edge cases, function behavior)

---

## Risk Mitigation

### Risk 1: RegExp Complexity
**Mitigation:**
- Allocate extra time (25-30 hours)
- Use existing parser infrastructure
- Leverage Unicode libraries for property escapes

### Risk 2: WeakRef/FinalizationRegistry GC Integration
**Mitigation:**
- Work closely with memory_gc component
- Implement thorough testing with GC simulation
- Use event loop for cleanup callback scheduling

### Risk 3: Strict Mode Pervasiveness
**Mitigation:**
- Systematic approach: parser changes first, then interpreter
- Test262 suite provides comprehensive edge case coverage
- Incremental implementation with verification at each step

### Risk 4: DataView Endianness Complexity
**Mitigation:**
- Use proven endianness handling from existing TypedArray work
- Platform-independent byte manipulation
- Comprehensive boundary checking tests

---

## Deliverables

### Code
- 8 new ES2024 components
- ~60 requirements implemented
- Estimated 500-600 new tests
- Test262 harness integration updates

### Documentation
- 8 component contracts (YAML)
- 8 component README files
- ES2024 Wave B completion report
- Test262 conformance report update

### Quality
- All components pass 12-check verification
- ≥80% test coverage per component
- 100% integration test pass rate
- >94% Test262 pass rate (target >96%)

---

## Timeline Estimate

**Wave B Total Effort:** 130-160 hours

**With Parallel Execution (7 concurrent agents):**
- Contract Generation: 2-3 hours
- Batch 1 Implementation: 25-30 hours (longest agent: regexp_advanced_features)
- Batch 2 Implementation: 8-10 hours (json_extensions, overlaps with Batch 1)
- Quality Verification: 3-4 hours
- Integration Testing: 2-3 hours

**Total Elapsed Time:** 32-40 hours (~1.3-1.7 days of continuous execution)

**With 8-hour workdays:** ~4-5 business days

---

## Post-Wave B Assessment

After Wave B completion, assess whether to proceed with Waves C-D:

**Wave C (Intl API - ECMA-402):**
- 60-80 hours effort
- ~5,000 Test262 tests (intl402/)
- Can be deprioritized if not required

**Wave D (Edge Cases & Polish):**
- 30-40 hours effort
- Remaining Test262 tests
- Final compliance push to >98%

**Decision Criteria:**
- Wave B Test262 results
- Project timeline constraints
- User requirements prioritization
- Intl API necessity for target use cases

---

## Component Size Estimates

| Component | Estimated Files | Estimated LOC | Estimated Tokens |
|-----------|----------------|---------------|------------------|
| regexp_advanced_features | 8-10 | 2,000-2,500 | 20,000-25,000 |
| class_static_blocks | 4-5 | 800-1,000 | 8,000-10,000 |
| error_extensions | 4-5 | 800-1,000 | 8,000-10,000 |
| dataview_complete | 5-6 | 1,200-1,500 | 12,000-15,000 |
| weakref_finalization | 6-7 | 1,500-1,800 | 15,000-18,000 |
| json_extensions | 4-5 | 600-800 | 6,000-8,000 |
| function_edge_cases | 5-6 | 1,000-1,200 | 10,000-12,000 |
| strict_mode_complete | 6-8 | 1,500-2,000 | 15,000-20,000 |

**All components well within token budget limits** (< 70,000 optimal tokens).

---

## Next Steps - Immediate Actions

1. ✅ Review and approve Wave B implementation plan
2. ⏭️ Generate all 8 Wave B contracts (Phase 1)
3. ⏭️ Launch 7 parallel implementation agents (Phase 2 - Batch 1)
4. ⏭️ Launch final agent when slot opens (Phase 2 - Batch 2)
5. ⏭️ Run 12-check verification on all components (Phase 3)
6. ⏭️ Run integration tests (Phase 4)
7. ⏭️ Generate Wave B completion report
8. ⏭️ Run Test262 suite and assess Wave C/D priority

---

**Plan Status:** ✅ Ready for Execution
**Execution Mode:** Parallel agents (max 7 concurrent)
**Expected Outcome:** ~94-96% ES2024 compliance after Wave B
**Estimated Compliance Before Wave B:** ~80-90%
**Estimated Compliance After Wave B:** ~94-96%
**Remaining Work:** Waves C-D for 98-100% ES2024 compliance

**Next Step:** Generate contracts for all 8 Wave B components, then launch parallel implementation agents.

---

**Version:** 0.1.0
**Date:** 2025-11-15
**Ready for Orchestration:** ✅ YES
