# ES2024 Wave C - Implementation Plan

**Date:** 2025-11-15
**Status:** Ready for Execution
**Wave:** Wave C (Internationalization API - ECMA-402)
**Version:** 0.1.0

---

## Executive Summary

Wave C focuses on **complete ECMA-402 Internationalization API** to provide locale-aware formatting and language-sensitive operations.

**Target:**
- **9 components** with **~75 requirements**
- **Estimated Test262 Coverage:** +5,000 tests (intl402/)
- **Estimated Effort:** 90-110 hours
- **Parallel Execution:** 7 concurrent agents (max from config)

**Priority:** LOW (can be deprioritized if internationalization not required)
**Impact:** Achieves >98% ES2024 compliance

---

## Wave C Components Overview

| # | Component | Requirements | Estimated Effort | Priority | Test262 Tests |
|---|-----------|--------------|------------------|----------|---------------|
| 1 | intl_collator | 8 | 12-15h | MEDIUM | ~600 |
| 2 | intl_datetimeformat | 12 | 18-22h | HIGH | ~1,500 |
| 3 | intl_numberformat | 10 | 15-18h | HIGH | ~1,200 |
| 4 | intl_pluralrules | 6 | 8-10h | MEDIUM | ~400 |
| 5 | intl_relativetimeformat | 6 | 8-10h | MEDIUM | ~300 |
| 6 | intl_listformat | 5 | 6-8h | LOW | ~250 |
| 7 | intl_displaynames | 7 | 10-12h | LOW | ~350 |
| 8 | intl_locale | 11 | 12-15h | MEDIUM | ~500 |
| 9 | intl_segmenter | 10 | 10-12h | MEDIUM | ~400 |
| **TOTAL** | **9** | **75** | **99-122h** | - | **~5,500** |

---

## Component 1: intl_collator

**Requirements:** 8 (FR-ES24-C-001 to FR-ES24-C-008)
**Estimated Effort:** 12-15 hours
**Priority:** MEDIUM (locale-sensitive string comparison)
**Test262 Tests:** ~600 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-001 | Intl.Collator constructor | Create collator with options | ≥10 |
| FR-ES24-C-002 | Locale resolution | Resolve requested vs available locales | ≥8 |
| FR-ES24-C-003 | compare() method | Compare strings with locale rules | ≥12 |
| FR-ES24-C-004 | Sensitivity option | base, accent, case, variant | ≥10 |
| FR-ES24-C-005 | Numeric collation | Enable numeric sorting (1 < 2 < 10) | ≥8 |
| FR-ES24-C-006 | Case first option | Upper/lower case precedence | ≥8 |
| FR-ES24-C-007 | Ignore punctuation | Ignore punctuation in comparison | ≥6 |
| FR-ES24-C-008 | resolvedOptions() | Return resolved configuration | ≥8 |

**Total Tests:** ≥70 tests

**Dependencies:**
- Unicode CLDR data (locale data)
- ICU library (recommended) or pure JavaScript implementation

**Performance Targets:**
- Collator construction: <5ms
- String comparison: <100µs per comparison
- Locale resolution: <1ms

**Implementation Strategy:**
- Use ICU4C bindings if available (fastest)
- Fallback to JavaScript implementation using Unicode collation algorithm
- Support BCP 47 locale identifiers
- Cache collators for performance

---

## Component 2: intl_datetimeformat

**Requirements:** 12 (FR-ES24-C-009 to FR-ES24-C-020)
**Estimated Effort:** 18-22 hours
**Priority:** HIGH (date/time formatting essential for most apps)
**Test262 Tests:** ~1,500 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-009 | Intl.DateTimeFormat constructor | Create formatter with options | ≥12 |
| FR-ES24-C-010 | format() method | Format Date to localized string | ≥15 |
| FR-ES24-C-011 | formatToParts() method | Format with part descriptors | ≥12 |
| FR-ES24-C-012 | formatRange() method | Format date range | ≥10 |
| FR-ES24-C-013 | formatRangeToParts() method | Format range with parts | ≥10 |
| FR-ES24-C-014 | Date/time style options | full, long, medium, short | ≥12 |
| FR-ES24-C-015 | Component options | year, month, day, hour, minute, second | ≥15 |
| FR-ES24-C-016 | Time zone support | IANA time zone database | ≥12 |
| FR-ES24-C-017 | Calendar support | gregory, buddhist, chinese, etc. | ≥10 |
| FR-ES24-C-018 | Hour cycle | h11, h12, h23, h24 | ≥8 |
| FR-ES24-C-019 | dayPeriod option | narrow, short, long | ≥6 |
| FR-ES24-C-020 | resolvedOptions() | Return resolved configuration | ≥8 |

**Total Tests:** ≥130 tests

**Dependencies:**
- Unicode CLDR date/time patterns
- IANA time zone database
- ICU library (recommended)

**Performance Targets:**
- Formatter construction: <10ms
- Date formatting: <1ms per format
- Date range formatting: <2ms

**Implementation Strategy:**
- Use ICU4C for date/time formatting
- Support all CLDR calendars
- Implement time zone conversion
- Cache formatters per locale/options

---

## Component 3: intl_numberformat

**Requirements:** 10 (FR-ES24-C-021 to FR-ES24-C-030)
**Estimated Effort:** 15-18 hours
**Priority:** HIGH (number formatting essential)
**Test262 Tests:** ~1,200 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-021 | Intl.NumberFormat constructor | Create formatter with options | ≥10 |
| FR-ES24-C-022 | format() method | Format number to localized string | ≥15 |
| FR-ES24-C-023 | formatToParts() method | Format with part descriptors | ≥12 |
| FR-ES24-C-024 | formatRange() method | Format number range | ≥8 |
| FR-ES24-C-025 | formatRangeToParts() method | Format range with parts | ≥8 |
| FR-ES24-C-026 | Style option | decimal, percent, currency, unit | ≥12 |
| FR-ES24-C-027 | Currency formatting | ISO 4217 currency codes | ≥15 |
| FR-ES24-C-028 | Unit formatting | length, area, volume, etc. | ≥12 |
| FR-ES24-C-029 | Notation option | standard, scientific, engineering, compact | ≥10 |
| FR-ES24-C-030 | resolvedOptions() | Return resolved configuration | ≥8 |

**Total Tests:** ≥110 tests

**Dependencies:**
- Unicode CLDR number patterns
- Currency/unit data
- ICU library (recommended)

**Performance Targets:**
- Formatter construction: <5ms
- Number formatting: <500µs per format
- Currency formatting: <1ms

---

## Component 4: intl_pluralrules

**Requirements:** 6 (FR-ES24-C-031 to FR-ES24-C-036)
**Estimated Effort:** 8-10 hours
**Priority:** MEDIUM (plural form selection)
**Test262 Tests:** ~400 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-031 | Intl.PluralRules constructor | Create plural rules selector | ≥8 |
| FR-ES24-C-032 | select() method | Select plural category | ≥12 |
| FR-ES24-C-033 | selectRange() method | Select range plural category | ≥8 |
| FR-ES24-C-034 | Type option | cardinal, ordinal | ≥10 |
| FR-ES24-C-035 | Plural categories | zero, one, two, few, many, other | ≥12 |
| FR-ES24-C-036 | resolvedOptions() | Return resolved configuration | ≥6 |

**Total Tests:** ≥56 tests

**Dependencies:**
- Unicode CLDR plural rules
- ICU library (recommended)

**Performance Targets:**
- Constructor: <2ms
- select() operation: <100µs

---

## Component 5: intl_relativetimeformat

**Requirements:** 6 (FR-ES24-C-037 to FR-ES24-C-042)
**Estimated Effort:** 8-10 hours
**Priority:** MEDIUM (relative time strings)
**Test262 Tests:** ~300 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-037 | Intl.RelativeTimeFormat constructor | Create formatter | ≥8 |
| FR-ES24-C-038 | format() method | Format relative time | ≥12 |
| FR-ES24-C-039 | formatToParts() method | Format with parts | ≥10 |
| FR-ES24-C-040 | Style option | long, short, narrow | ≥10 |
| FR-ES24-C-041 | Numeric option | always, auto | ≥8 |
| FR-ES24-C-042 | resolvedOptions() | Return resolved configuration | ≥6 |

**Total Tests:** ≥54 tests

**Dependencies:**
- Unicode CLDR relative time patterns

**Performance Targets:**
- Formatter construction: <3ms
- Formatting: <500µs

---

## Component 6: intl_listformat

**Requirements:** 5 (FR-ES24-C-043 to FR-ES24-C-047)
**Estimated Effort:** 6-8 hours
**Priority:** LOW (list formatting)
**Test262 Tests:** ~250 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-043 | Intl.ListFormat constructor | Create list formatter | ≥8 |
| FR-ES24-C-044 | format() method | Format list to string | ≥12 |
| FR-ES24-C-045 | formatToParts() method | Format with parts | ≥10 |
| FR-ES24-C-046 | Type option | conjunction, disjunction, unit | ≥12 |
| FR-ES24-C-047 | resolvedOptions() | Return resolved configuration | ≥6 |

**Total Tests:** ≥48 tests

**Dependencies:**
- Unicode CLDR list patterns

**Performance Targets:**
- Formatter construction: <2ms
- List formatting: <1ms for 10 items

---

## Component 7: intl_displaynames

**Requirements:** 7 (FR-ES24-C-048 to FR-ES24-C-054)
**Estimated Effort:** 10-12 hours
**Priority:** LOW (display names for codes)
**Test262 Tests:** ~350 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-048 | Intl.DisplayNames constructor | Create display names formatter | ≥8 |
| FR-ES24-C-049 | of() method | Get display name for code | ≥15 |
| FR-ES24-C-050 | Language display names | Language codes to names | ≥10 |
| FR-ES24-C-051 | Region display names | Region codes to names | ≥10 |
| FR-ES24-C-052 | Script display names | Script codes to names | ≥8 |
| FR-ES24-C-053 | Currency display names | Currency codes to names | ≥10 |
| FR-ES24-C-054 | resolvedOptions() | Return resolved configuration | ≥6 |

**Total Tests:** ≥67 tests

**Dependencies:**
- Unicode CLDR display names

**Performance Targets:**
- Constructor: <3ms
- of() operation: <200µs

---

## Component 8: intl_locale

**Requirements:** 11 (FR-ES24-C-055 to FR-ES24-C-065)
**Estimated Effort:** 12-15 hours
**Priority:** MEDIUM (locale manipulation)
**Test262 Tests:** ~500 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-055 | Intl.Locale constructor | Create locale object | ≥10 |
| FR-ES24-C-056 | Locale parsing | Parse BCP 47 locale strings | ≥15 |
| FR-ES24-C-057 | Language subtag | baseName, language | ≥8 |
| FR-ES24-C-058 | Script subtag | script property | ≥8 |
| FR-ES24-C-059 | Region subtag | region property | ≥8 |
| FR-ES24-C-060 | Locale extensions | Unicode extension handling | ≥12 |
| FR-ES24-C-061 | Calendar extension | calendar property | ≥8 |
| FR-ES24-C-062 | Numbering system | numberingSystem property | ≥8 |
| FR-ES24-C-063 | maximize() method | Add likely subtags | ≥8 |
| FR-ES24-C-064 | minimize() method | Remove likely subtags | ≥8 |
| FR-ES24-C-065 | toString() method | Serialize to BCP 47 | ≥8 |

**Total Tests:** ≥101 tests

**Dependencies:**
- Unicode CLDR likely subtags
- BCP 47 parser

**Performance Targets:**
- Constructor: <1ms
- Parsing: <500µs
- maximize/minimize: <2ms

---

## Component 9: intl_segmenter

**Requirements:** 10 (FR-ES24-C-066 to FR-ES24-C-075)
**Estimated Effort:** 10-12 hours
**Priority:** MEDIUM (text segmentation)
**Test262 Tests:** ~400 tests

### Functional Requirements

| ID | Requirement | Description | Tests |
|----|-------------|-------------|-------|
| FR-ES24-C-066 | Intl.Segmenter constructor | Create segmenter | ≥8 |
| FR-ES24-C-067 | segment() method | Segment string into iterator | ≥12 |
| FR-ES24-C-068 | Grapheme segmentation | Character boundaries | ≥12 |
| FR-ES24-C-069 | Word segmentation | Word boundaries | ≥15 |
| FR-ES24-C-070 | Sentence segmentation | Sentence boundaries | ≥15 |
| FR-ES24-C-071 | Segment object | segment, index, input, isWordLike | ≥10 |
| FR-ES24-C-072 | containing() method | Find segment at position | ≥10 |
| FR-ES24-C-073 | Iterator protocol | Iterate over segments | ≥10 |
| FR-ES24-C-074 | Locale-sensitive segmentation | Different rules per locale | ≥12 |
| FR-ES24-C-075 | resolvedOptions() | Return resolved configuration | ≥6 |

**Total Tests:** ≥110 tests

**Dependencies:**
- Unicode text segmentation algorithm (UAX #29)
- ICU library (recommended)

**Performance Targets:**
- Constructor: <3ms
- Segmentation: <5ms for 1KB text
- Iterator creation: <500µs

---

## Dependencies Between Wave C Components

```
graph TD
    intl_locale[intl_locale] --> intl_collator
    intl_locale --> intl_datetimeformat
    intl_locale --> intl_numberformat
    intl_locale --> intl_pluralrules
    intl_locale --> intl_relativetimeformat
    intl_locale --> intl_listformat
    intl_locale --> intl_displaynames
    intl_locale --> intl_segmenter

    unicode_cldr[Unicode CLDR Data] --> ALL
    icu_library[ICU Library] --> ALL
```

**Build Order (Topological Sort):**

**Foundation (Must build first):**
1. intl_locale (required by all others)

**Wave 1 (Can build in parallel after intl_locale):**
2. intl_collator
3. intl_datetimeformat
4. intl_numberformat
5. intl_pluralrules
6. intl_relativetimeformat
7. intl_listformat
8. intl_displaynames
9. intl_segmenter

**All 8 components after intl_locale can be built in parallel** (7 concurrent max).

---

## External Dependencies

### Unicode CLDR Data

All components require Unicode CLDR (Common Locale Data Repository) data:

- **Locale data files:** ~50MB for all locales
- **Recommended subset:** Top 20-30 locales (~5-10MB)
- **Minimum:** en-US, en-GB, es, fr, de, ja, zh (~2MB)

**Data Categories:**
- Date/time patterns
- Number patterns
- Currency symbols
- Plural rules
- Collation rules
- Display names
- Segmentation rules

**Implementation Options:**
1. **Full CLDR:** All locales (50MB+)
2. **Subset:** Common locales (5-10MB)
3. **Minimal:** en-US only (500KB)
4. **On-demand:** Load locales as needed

### ICU Library Integration

**Recommended:** Use ICU (International Components for Unicode)

**Options:**
1. **ICU4C binding:** Fastest, native performance
   - Requires C extension
   - ~10-20MB library
   - Best performance

2. **Pure JavaScript:** No native dependencies
   - Larger bundle size
   - Slower performance
   - Easier deployment

3. **Hybrid:** ICU for complex operations, JS for simple

**For this implementation:** Start with pure JavaScript, add ICU optimization later

---

## Execution Strategy

### Phase 1: Foundation Setup (2-3 hours)

**Before component work:**

1. **Set up CLDR data infrastructure**
   ```bash
   # Download CLDR data subset
   mkdir -p shared-libs/cldr-data
   # Extract essential locale data
   ```

2. **Create shared utilities**
   - Locale parsing utilities
   - BCP 47 validation
   - CLDR data loader
   - Common formatting helpers

3. **Generate all 9 contracts** (parallel)

### Phase 2: Build intl_locale First (12-15 hours)

**Sequential (foundation for all others):**
- Launch intl_locale agent
- Wait for completion
- Verify locale manipulation works
- All other components depend on this

### Phase 3: Parallel Implementation (18-22 hours)

**Batch 1 (Launch immediately after intl_locale - 7 agents):**
1. intl_datetimeformat (18-22h) - longest
2. intl_numberformat (15-18h)
3. intl_collator (12-15h)
4. intl_displaynames (10-12h)
5. intl_segmenter (10-12h)
6. intl_pluralrules (8-10h)
7. intl_relativetimeformat (8-10h)

**Batch 2 (Launch when slot opens - 1 agent):**
8. intl_listformat (6-8h)

### Phase 4: Quality Verification (3-4 hours)

For each component:
1. Run 12-check verification
2. Verify locale data loading
3. Check CLDR compliance
4. Run Test262 intl402 tests
5. Performance verification

### Phase 5: Integration Testing (2-3 hours)

1. Cross-component integration
2. Locale fallback testing
3. CLDR data consistency
4. Memory usage testing

---

## Success Criteria

### Functional
- ✅ All 75 Wave C requirements implemented
- ✅ All components pass 12-check verification
- ✅ 100% test pass rate (component tests)
- ✅ 100% integration test pass rate
- ✅ Test262 intl402 pass rate >90% (~5,000 tests)

### Quality
- ✅ All components ≥80% test coverage
- ✅ TDD methodology followed
- ✅ Contract-first development
- ✅ CLDR data properly integrated
- ✅ Locale fallback working correctly

### Performance
- ✅ Formatter construction: <10ms
- ✅ Formatting operations: <2ms typical
- ✅ Locale resolution: <1ms
- ✅ Memory usage: <50MB for CLDR data subset

---

## Test262 Integration

### Expected Test262 Improvement

**Current (after Wave B):** ~47,000-48,000 / 50,000 passing (94-96%)
**After Wave C:** ~50,000-52,000 / 55,000 passing (>95%)

Note: Test262 has ~5,000 additional intl402 tests not in the 50,000 estimate.

### Test Categories Covered by Wave C

- **intl402/Collator/** (~600 tests)
- **intl402/DateTimeFormat/** (~1,500 tests)
- **intl402/NumberFormat/** (~1,200 tests)
- **intl402/PluralRules/** (~400 tests)
- **intl402/RelativeTimeFormat/** (~300 tests)
- **intl402/ListFormat/** (~250 tests)
- **intl402/DisplayNames/** (~350 tests)
- **intl402/Locale/** (~500 tests)
- **intl402/Segmenter/** (~400 tests)

**Total:** ~5,500 Test262 tests directly verified

---

## Timeline Estimate

**Wave C Total Effort:** 99-122 hours

**With Parallel Execution (7 concurrent agents):**
- Foundation setup: 2-3 hours
- intl_locale (sequential): 12-15 hours
- Batch 1 Implementation: 18-22 hours (longest: intl_datetimeformat)
- Batch 2 Implementation: 6-8 hours (overlaps with Batch 1)
- Quality Verification: 3-4 hours
- Integration Testing: 2-3 hours

**Total Elapsed Time:** 43-55 hours (~2 days of continuous execution)

**With 8-hour workdays:** ~6-7 business days

---

## Risk Mitigation

### Risk 1: CLDR Data Complexity
**Mitigation:**
- Start with minimal locale set (en-US)
- Expand locales incrementally
- Use CLDR JSON format (easier to parse)
- Cache parsed data in memory

### Risk 2: ICU Library Dependency
**Mitigation:**
- Implement pure JavaScript fallback
- Use ICU as optional enhancement
- Test both paths
- Document ICU installation

### Risk 3: Test262 Coverage
**Mitigation:**
- Set up Test262 harness early
- Run intl402 tests continuously
- Fix failures incrementally
- Document known limitations

### Risk 4: Performance with Pure JavaScript
**Mitigation:**
- Optimize hot paths
- Cache formatters aggressively
- Use lazy initialization
- Profile and optimize

### Risk 5: Locale Data Size
**Mitigation:**
- Support multiple deployment sizes
- Allow locale data to be loaded on-demand
- Compress locale data
- Provide build tool to select locales

---

## Deliverables

### Code
- 9 new Intl components
- ~75 requirements implemented
- Estimated 600-700 new tests
- CLDR data integration
- Test262 intl402 harness

### Documentation
- 9 component contracts (YAML)
- 9 component README files
- CLDR data usage guide
- Locale support matrix
- ES2024 Wave C completion report
- Test262 conformance report

### Quality
- All components pass 12-check verification
- ≥80% test coverage per component
- 100% integration test pass rate
- >90% Test262 intl402 pass rate

---

## Component Size Estimates

| Component | Estimated Files | Estimated LOC | Estimated Tokens |
|-----------|----------------|---------------|------------------|
| intl_locale | 6-8 | 1,500-2,000 | 15,000-20,000 |
| intl_collator | 5-6 | 1,200-1,500 | 12,000-15,000 |
| intl_datetimeformat | 8-10 | 2,500-3,000 | 25,000-30,000 |
| intl_numberformat | 7-9 | 2,000-2,500 | 20,000-25,000 |
| intl_pluralrules | 4-5 | 800-1,000 | 8,000-10,000 |
| intl_relativetimeformat | 4-5 | 800-1,000 | 8,000-10,000 |
| intl_listformat | 3-4 | 600-800 | 6,000-8,000 |
| intl_displaynames | 5-6 | 1,000-1,200 | 10,000-12,000 |
| intl_segmenter | 6-7 | 1,200-1,500 | 12,000-15,000 |

**All components well within token budget limits** (< 70,000 optimal tokens).

---

## Locale Support Strategy

### Phase 1: Minimal (en-US only)
- Get functionality working
- Pass Test262 basic tests
- ~500KB CLDR data

### Phase 2: Common Locales
- Add top 20 locales by usage
- en-*, es-*, fr-*, de-*, ja-JP, zh-CN, ar-*, etc.
- ~5-10MB CLDR data

### Phase 3: Comprehensive
- Add all CLDR locales
- ~50MB CLDR data
- On-demand loading

**For Wave C implementation:** Start with Phase 1, design for Phase 2+

---

## Next Steps - Immediate Actions

1. ✅ Review and approve Wave C implementation plan
2. ⏭️ Set up CLDR data infrastructure
3. ⏭️ Generate all 9 Wave C contracts
4. ⏭️ Launch intl_locale agent (sequential)
5. ⏭️ Wait for intl_locale completion
6. ⏭️ Launch 7 parallel agents for remaining components
7. ⏭️ Launch final agent when slot opens
8. ⏭️ Run 12-check verification on all components
9. ⏭️ Run integration tests
10. ⏭️ Run Test262 intl402 suite
11. ⏭️ Generate Wave C completion report

---

**Plan Status:** ✅ Ready for Execution
**Execution Mode:** Sequential (intl_locale) then Parallel (7 concurrent)
**Expected Outcome:** >98% ES2024 compliance after Wave C
**Estimated Compliance Before Wave C:** ~94-96%
**Estimated Compliance After Wave C:** >98%

**Next Step:** Set up CLDR data infrastructure and generate contracts for all 9 Wave C components.

---

**Version:** 0.1.0
**Date:** 2025-11-15
**Ready for Orchestration:** ✅ YES
