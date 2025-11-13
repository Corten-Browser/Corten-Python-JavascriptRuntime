# JavaScript Runtime Component: Comprehensive Software Specification

Modern browsers demand JavaScript engines that balance startup speed with peak performance while maintaining spec compliance and security. This specification provides implementation-ready guidance for building a production-grade JavaScript runtime within a modular browser architecture, synthesizing proven patterns from V8, SpiderMonkey, and JavaScriptCore.

## Architecture overview and design philosophy

**Core tenet: Multi-tier execution.** JavaScript runtimes must serve two masters: fast startup for short scripts and maximum throughput for long-running applications. Single-tier interpreters optimize startup but sacrifice performance. Pure JIT compilers achieve peak speed but impose unacceptable startup costs. The solution is tiered compilation where code begins in a fast interpreter, graduates to baseline JIT after modest execution, and finally reaches optimizing JIT for hot paths.

Modern engines implement 3-4 execution tiers. V8 runs Ignition (bytecode interpreter), Sparkplug (template JIT), Maglev (mid-tier optimizing JIT), and TurboFan (aggressive optimizer). SpiderMonkey uses Baseline Interpreter, Baseline Compiler, and WarpMonkey. JavaScriptCore employs LLInt, Baseline JIT, DFG, and FTL. Each tier collects profiling data that informs optimization decisions in higher tiers, creating a continuous feedback loop.

**Bytecode as lingua franca.** All modern engines compile to architecture-independent bytecode serving as persistent intermediate representation. Parser generates bytecode once, multiple execution tiers consume it. This decouples parsing from execution, enables bytecode caching across page loads, and simplifies tier transitions through shared representation.

**Register-based bytecode wins.** V8 and JavaScriptCore proved register-based bytecode superior to stack-based for JavaScript workloads. Register allocation eliminates redundant stack operations, accumulator register pattern reduces instruction count, and explicit operands simplify optimization. SpiderMonkey maintains stack-based bytecode but pays modest performance penalty.

## Component architecture and data flow

### Parser subsystem

**Lazy parsing with delazification.** Functions parse twice in modern engines—first pass (preparser) validates syntax without building complete AST or generating bytecode, consuming minimal memory. Second pass (full parser) triggers when function first executes, generating bytecode just-in-time. This lazy approach dramatically reduces startup time and memory for pages with megabytes of JavaScript where most functions never execute.

Parser accepts source text, performs lexical analysis producing token stream, and constructs Abstract Syntax Tree through recursive descent. Hand-written recursive descent parsers dominate over generated parsers because JavaScript's complex grammar with contextual keywords (await, yield, async) and automatic semicolon insertion demands custom logic. Parser validates syntax, detects early errors per spec, collects function metadata (parameter count, uses eval/with, contains super), and emits bytecode through BytecodeGenerator.

**Scope analysis.** Parser identifies lexical scopes, resolves variable references, determines which variables require heap allocation (captured by closures), and annotates AST with scope information. This analysis enables correct closure semantics and optimization opportunities (stack-allocate variables not captured by closures).

### Bytecode generation

BytecodeGenerator walks AST and emits compact register-based or stack-based bytecode depending on engine choice. For register-based engines, generator performs register allocation, assigns accumulator for expression temporaries, and produces bytecode instructions with explicit register operands. Typical instruction categories include literals (LoadConstant, LoadUndefined), variables (LoadGlobal, StoreLocal), operators (Add, Multiply), control flow (Jump, JumpIfTrue, Return), objects (CreateObject, LoadProperty, StoreProperty), and functions (CreateClosure, CallFunction).

**Bytecode optimization.** Even unoptimized bytecode benefits from simple optimizations: dead code elimination removes unreachable statements, constant folding evaluates constant expressions at compile time, and peephole optimization replaces instruction sequences with equivalent shorter forms. These optimizations impose minimal compilation cost while improving interpreter performance.

### Interpreter tier

Interpreter executes bytecode one instruction at a time with dispatch loop selecting handler for each opcode. Modern interpreters achieve performance through inline caching, accumulator register for expression results, and tight integration with runtime services. V8's Ignition interpreter uses TurboFan's CodeStubAssembler to generate efficient bytecode handlers as machine code, bridging interpreter and compiler worlds.

**Inline caching foundation.** Interpreter installs inline caches at every property access, function call, and type-sensitive operation. IC starts uninitialized, transitions to monomorphic after seeing one object shape, becomes polymorphic with multiple shapes (typically ≤4), and degrades to megamorphic for highly polymorphic sites. Monomorphic ICs provide near-compiled performance by caching shape and property offset, checking shape once, and accessing property directly without hash table lookup.

**Profiling instrumentation.** Interpreter collects execution counters (function invocations, loop iterations), type feedback (observed types at operations), inline cache states, and branch outcomes. This profiling data guides JIT compilation decisions—when to compile, what types to specialize for, which paths to optimize. Counter thresholds trigger tier transitions: Sparkplug after ~500 executions, Maglev after ~1000, TurboFan after ~100,000 in V8's model.

### Baseline JIT tier

Baseline JIT eliminates interpreter dispatch overhead while maintaining compatibility with interpreter. Template JIT approach translates bytecode to machine code through direct templates—for each bytecode instruction, emit corresponding machine code sequence. Sparkplug exemplifies this: linear walk of bytecode, emit fixed code template per instruction, preserve inline caches from interpreter, and use same runtime call stubs. Compilation completes 10x faster than optimizing JIT with 2-3x speedup over interpreter.

**OSR entry points.** On-Stack Replacement allows running code to transition between tiers without returning to caller. Long-running loops compile at iteration start, interpreter checks compiled code availability after each iteration, and upon detection reconstructs activation record in compiled code format and jumps to compiled loop body. This prevents fast-executing loops from being trapped in slow interpreter forever.

### Optimizing JIT tier

Optimizing JIT transforms bytecode and inline cache feedback into highly optimized machine code through speculative optimization. Unlike baseline JIT that preserves semantics of every bytecode, optimizer assumes types based on profiling, specializes code for common case, and inserts guards (type checks) with bailout to interpreter on violation.

**Sea-of-nodes intermediate representation.** TurboFan pioneered sea-of-nodes IR for JavaScript compilation: operations represented as nodes in directed graph, data dependencies as edges, no fixed evaluation order except what dependencies require. This relaxed representation enables aggressive code motion, combines redundancy elimination naturally, and simplifies optimization passes. Alternative CFG-based SSA IR (SpiderMonkey, JavaScriptCore DFG) maintains block structure with phi nodes at merge points, trading some optimization power for compilation speed.

**Critical optimizations.** Type specialization replaces generic operations with type-specific variants (integer addition instead of generic add). Escape analysis determines objects that never leave function, enabling scalar replacement (allocate fields as local variables instead of heap object). Inlining replaces function calls with callee body, eliminating call overhead and enabling interprocedural optimization. Loop-invariant code motion hoists invariant computations outside loops. Dead code elimination removes provably unused computations. Bounds check elimination removes array bounds checks when provably safe.

**Deoptimization infrastructure.** Speculative optimization requires bailout mechanism when assumptions violated. Each speculation point (type check, overflow check, watchpoint) can trigger deoptimization: capture live values, map optimized frame to interpreter frame layout, reconstruct interpreter state, continue execution in interpreter. Deoptimization sites collect exit profiling—frequently firing exits indicate bad speculation, triggering recompilation with refined assumptions or disabled optimizations. Exponential backoff (2^R where R=recompilation count) prevents recompilation thrashing.

## Memory management and garbage collection

**Generational hypothesis.** Most objects die young—programs allocate temporary objects that become garbage almost immediately while long-lived objects (globals, caches) survive indefinitely. Generational GC exploits this: young generation (nursery) uses fast copying collector running frequently, old generation uses mark-sweep with less frequent collection. Objects surviving 2-3 nursery collections promote to old generation.

### Young generation collector

**Semi-space copying algorithm.** Young generation divides into two equal semi-spaces (from-space and to-space). Allocation uses simple bump pointer in from-space (increment pointer, return previous value—extremely fast). When from-space full, **scavenger** traces live objects from roots (stack, registers, old-to-young remembered set), copies survivors to to-space, updates pointers, and swaps space roles. Cheney's algorithm processes to-space as queue: scan pointer follows allocation pointer, processing each copied object and copying its children.

Parallel scavenging divides heap regions among threads, each thread copies objects from assigned regions, atomic operations coordinate pointer updates. V8's parallel scavenger achieves 20-50% pause time reduction on multi-core systems. Semi-space overhead (50% of nursery wasted) acceptable because nursery stays small (1-16MB) and collection extremely fast (sub-millisecond for small nurseries).

### Old generation collector

**Tri-color marking.** Major GC uses mark-and-sweep with tri-color abstraction: white (unprocessed), gray (processed but children not scanned), black (fully processed). Mark phase begins with roots black, traced objects gray, scan gray set until empty promoting each to black. Sweep phase walks heap, adds unmarked regions to free-lists organized by size class, compacts fragmented pages selectively.

**Concurrent and incremental marking.** Stop-the-world marking pauses grow with heap size, unacceptable for large applications. Concurrent marking runs on background threads while JavaScript executes, using write barriers to track modifications. Dijkstra-style write barrier marks new targets when black object gains pointer to white object. Incremental marking divides work into small slices executed between JavaScript tasks, spreading pause over time. V8's Orinoco combines both: concurrent marking handles bulk work, incremental marking reduces final pause, parallel threads accelerate remaining phases.

**Write barriers for remembered sets.** When old object gains pointer to young object (rare—generational hypothesis), record in remembered set. Per-page bitmap implementation: bit N set means word at offset N may contain cross-generation pointer. Young GC scans remembered set as additional roots without traversing entire old generation. Write barrier executes on every pointer store: if (object_in_old_space && value_in_young_space) add_to_remembered_set(object_page, offset).

### Object representation

**Hidden classes (maps/shapes).** JavaScript objects are hash tables semantically but hash tables for every property access kills performance. Hidden classes solve this: objects with same properties in same order share hidden class descriptor. Hidden class stores property names mapped to offsets, prototype reference, instance size, and transitions (property additions). Objects store only hidden class pointer and property values array. Property access becomes: check object's hidden class, if matches cached hidden class, load from cached offset—one comparison, one load, no hashing.

Hidden class transitions form tree: root represents empty object, edges represent property additions, nodes represent object shapes. Adding property x then y creates different path than y then x—property order matters. Deleting properties transitions to slow dictionary mode (self-contained hash table, no further transitions). Performance best practice: initialize properties in consistent order, avoid deletion, create objects through constructors or classes.

**Tagged pointers and SMI.** V8 64-bit uses tag scheme: small integers (SMI) store 32-bit value in high half with low 32 bits zero, pointers set low bit enabling 8-byte alignment. Range covers -2^31 to 2^31-1, common case in JavaScript. Integer operations: add SMI values, check overflow, no heap allocation. Pointer operations: mask low bits to get address. SpiderMonkey uses NaN-boxing: IEEE-754 NaN representations (2^53 patterns) with only one needed for actual NaN, remaining encode other types and pointers in 64 bits.

**Pointer compression.** Modern V8 uses 32-bit compressed pointers (heap offsets from base) when heap fits in 4GB range. Decompress on load: base + offset. Compress on store: subtract base. Achieves 43% heap reduction on Gmail with <5% performance cost—memory pressure relief outweighs decompression overhead.

## ECMAScript standards compliance

**Target specification: ECMAScript 2024 (ES15) as baseline.** Includes ArrayBuffer resizing/transfer, RegExp /v flag with set operations, Promise.withResolvers(), Object.groupBy()/Map.groupBy(), Atomics.waitAsync(), String.prototype.isWellFormed()/toWellFormed(). **Stage 4 proposals are mandatory** as they will appear in ES2025: Iterator helpers, duplicate named capture groups in RegExp, Set methods (union, intersection, difference), Promise.try.

**Implementation priority order.** Phase 1 (core): variables (var/let/const), functions (declarations/expressions/arrows), objects/arrays, operators, control flow (if/loops/switch), scoping/closures. Phase 2 (essential modern): Promises, async/await, classes, destructuring, spread/rest, template literals, ES modules. Phase 3 (advanced): Proxies/Reflect, Symbols, WeakMap/WeakSet, generators/iterators, TypedArrays, SharedArrayBuffer. Phase 4 (internationalization): ECMA-402 Intl APIs (optional initially but required for complete compliance).

**Module systems.** ES modules are primary module system with static structure enabling tree-shaking, asynchronous loading, live bindings (exports update when original changes), and strict mode by default. Module loading pipeline: parse (create module record), link (resolve imports/create environment), evaluate (execute module code). Support top-level await—module evaluation returns Promise, dependent modules wait for completion. CommonJS support (require/module.exports) may be necessary for Node.js compatibility but not required for browser-only runtime.

## Browser integration and Web APIs

### Integration architecture

JavaScript runtime exists within larger browser architecture, communicating with HTML parser, DOM, CSSOM, and render engine through bindings layer. Each browsing context has JavaScript realm containing global object (Window for browsers, WorkerGlobalScope for workers), environment settings object tracking origin/base URL/CSP, and associated event loop.

**HTML parser coordination.** Default `<script>` elements without defer/async are parser-blocking: parser stops when encountering script, fetches (if external), executes, then resumes parsing. Blocking prevents document.write() from executing after parsing completes. Script execution can call document.write(), modifying input stream. Parser-blocking doesn't necessarily mean render-blocking—scripts in body only block rendering of subsequent content. Async scripts execute when available (no ordering guarantees), defer scripts execute after parsing (in order), module scripts behave like defer by default.

**DOM manipulation triggering.** JavaScript modifying DOM queues style recalculation, layout (reflow), and paint operations. Browser batches these operations, executing at next rendering opportunity. Reading layout properties (offsetWidth, getBoundingClientRect(), scrollTop) forces synchronous layout if pending changes exist—"layout thrashing." Avoid interleaving reads and writes; batch all reads before all writes.

### Bindings layer

**Web IDL as specification language.** Browser APIs described in Web IDL define interfaces, operations, attributes, types, and JavaScript binding behavior. IDL compiler generates C++ binding code connecting JavaScript values to native implementations. Type conversions handle mapping JavaScript numbers to C++ integers (with clamping/range enforcement via extended attributes), JavaScript objects to dictionaries, callback functions to function pointers, and exceptions in both directions.

**V8 bindings architecture (Chromium/Blink).** V8 FunctionTemplates and ObjectTemplates establish JavaScript wrapper objects connected to C++ DOM objects. Generated binding code handles: security checks (same-origin policy), type conversions (JS values to C++ types), calling native implementations, wrapping return values, and exception propagation. Fast paths using V8 interceptors and FastCalls reduce overhead for performance-critical operations. Isolated worlds enable extension content scripts to execute in separate JavaScript context sharing DOM but not global variables.

**Memory management across boundary.** JavaScript GC doesn't directly see C++ objects. Wrapper objects hold persistent handles to C++ implementations, C++ objects hold weak handles to wrappers. When wrapper becomes unreachable, GC invokes finalizer releasing C++ object. Reference cycles spanning JavaScript-C++ boundary require careful handling—weak references in appropriate direction prevent leaks.

### Web APIs implementation

Core Web APIs implemented through bindings include: DOM manipulation (createElement, appendChild, getElementById), CSSOM (getComputedStyle, element.style), Events (addEventListener, Event construction), Timers (setTimeout, setInterval, requestAnimationFrame, requestIdleCallback), Fetch API (fetch, Request, Response, Headers), Storage (localStorage, sessionStorage, IndexedDB), Console API (console.log/warn/error), Web Workers, Service Workers, WebSockets, WebRTC. Each API requires IDL definition, C++ implementation, test coverage, and security review.

## Event loop specification

**Event loop as orchestration mechanism.** Each agent (main thread or worker) has associated event loop managing task execution, microtask processing, and rendering. Event loop continuously: selects oldest task from task queue, executes task, performs microtask checkpoint (process all microtasks), updates rendering if rendering opportunity exists, and loops.

### Task queues (macrotasks)

Multiple task queues exist with different task sources: DOM manipulation source, user interaction source (click/keyboard events), networking source (fetch callbacks), timer source (setTimeout/setInterval), history traversal source. Browser has flexibility selecting which queue to service—higher priority tasks (user input) typically processed before lower priority (timers). Task structure contains steps (algorithm to run), source (which task source), document (associated document), and script evaluation environment.

**Timer implementation.** setTimeout(callback, delay) queues task to timer task source after minimum delay milliseconds. Actual execution may occur later if event loop busy. Timer callbacks execute as separate tasks, not synchronously. setInterval queues recurring tasks. Timers clamped to 4ms minimum after 5 nested levels preventing CPU thrashing.

### Microtask queue

Microtasks have higher priority than tasks—**all microtasks process after current task and before next task**. Microtask sources: Promise reactions (then/catch/finally callbacks), queueMicrotask() API, MutationObserver callbacks. Microtask checkpoint algorithm: set checkpoint flag, while microtask queue not empty, dequeue and run microtask (each microtask may queue additional microtasks—all eventually process), clear checkpoint flag.

**Critical semantic: microtasks run to completion.** If microtask queues another microtask, it processes in same checkpoint. Infinite microtask loop starves task queue and rendering—validation checks detect this. Promise chains execute rapidly through microtasks without yielding to event loop between steps.

### Promise and async/await implementation

**Promise internal structure.** Promise object contains [[PromiseState]] (pending/fulfilled/rejected), [[PromiseResult]] (resolution value), [[PromiseFulfillReactions]] (list of handlers), and [[PromiseRejectReactions]] (list of handlers). Each reaction contains handler function, capabilities (resolve/reject functions for chain Promise), and type. Promise.prototype.then() creates new Promise, attaches reaction to current Promise, returns new Promise. When Promise fulfills, each reaction queues microtask calling handler with result.

**Async function transformation.** Async functions return Promise immediately and execute synchronously until first await. Await expression: evaluate awaited value, if not Promise coerce with Promise.resolve(), suspend function creating continuation, queue microtask for promise resolution, return Promise to caller. When awaited promise resolves, microtask resumes function execution. Optimization: resolved promises can resume synchronously without extra microtick (V8 achieved 3-microtick to 1-microtick reduction for common case).

### Rendering steps

When rendering opportunity exists (typically 60 FPS = every 16.67ms), browser performs rendering update: runs requestAnimationFrame callbacks, processes resize observations and intersection observations, updates DOM rendering (recalculate styles, layout, paint, composite layers), and fires animation events. **requestAnimationFrame callbacks execute before rendering**, making this ideal API for visual updates. Each callback receives high-resolution timestamp. Browser may skip rendering if no visual changes or tab hidden.

**requestIdleCallback execution.** During idle periods after rendering (task queues empty, next frame not due), browser may run idle callbacks. Callback receives deadline object with timeRemaining() method indicating available time. Timeout option ensures eventual execution. Not supported in Safari—requires polyfill or feature detection.

## Module system implementation

### ES modules

**Module records structure.** Each module represented by Source Text Module Record containing environment (ModuleEnvironment with bindings), namespace (Module Namespace exotic object), requestedModules (import specifiers), importEntries (imported bindings), localExportEntries (local declarations exported), indirectExportEntries (re-exported imports), starExportEntries (export * declarations), and status (unlinked/linking/linked/evaluating/evaluated/errored).

**Module loading algorithm.** Three phases: Parse phase creates module record from source text, validates syntax, resolves static import/export declarations, and builds module graph recursively. Link phase resolves all imports, creates module environment, instantiates all bindings (including indirect exports), detects cycles (allowed—creates TDZ for bindings not yet initialized), and transitions status to linked. Evaluate phase executes module code, runs synchronously unless top-level await present, memoizes result (module evaluates once regardless of import count), and transitions to evaluated.

**Live bindings semantics.** ES module exports are live bindings—importing module sees current value of exported variable, including mutations. Implementation: imported bindings reference same storage location as export source. Contrast with CommonJS where require() returns current value of module.exports copied at import time.

**Top-level await handling.** Modules may use await at top level, making evaluation asynchronous. Module evaluation returns Promise, dependent modules wait for Promise resolution before their evaluation begins. Enables async initialization (fetching config, dynamic imports). Implementation complexity: module evaluation becomes async operation, require coordination across module graph.

### CommonJS (optional for Node.js compatibility)

Module wrapper function wraps CommonJS module:
```javascript
(function(exports, require, module, __filename, __dirname) {
  // Module code with require() calls and module.exports assignments
})
```

Require function synchronously loads module, checks require.cache for cached module, executes wrapper function if not cached, returns module.exports object. Circular dependencies supported—require returns partially constructed module.exports (whatever exported so far). Module system maintains cache preventing duplicate execution.

## Security sandbox architecture

### Process isolation

Modern browsers use multi-process architecture: privileged browser process (UI, privileged APIs, IPC broker), sandboxed renderer processes (execute web content), GPU process (graphics), network process (network requests), storage process (persistent data). Renderers sandboxed via OS mechanisms (restricted syscalls on Linux via seccomp-bpf, sandbox on Windows, Seatbelt on macOS).

**Site Isolation.** Chrome's Site Isolation places each site (scheme + eTLD+1) in separate renderer process, preventing cross-site memory access via Spectre attacks. Out-of-process iframes (OOPIF) place cross-origin iframes in different processes than parent. postMessage works across process boundaries through IPC. Process-per-site overhead significant (memory cost) but security benefit essential.

### Content Security Policy

CSP provides defense-in-depth against XSS by restricting resource loading. script-src directive controls JavaScript sources: 'self' allows same origin, 'unsafe-inline' allows inline scripts (avoid), 'unsafe-eval' allows eval/Function constructor (avoid), 'nonce-{random}' allows scripts with matching nonce attribute, 'strict-dynamic' enables trust propagation for dynamically loaded scripts. 'wasm-unsafe-eval' specifically controls WebAssembly compilation.

**Best practice CSP:**
```
Content-Security-Policy: default-src 'self'; 
  script-src 'nonce-{random}' 'strict-dynamic'; 
  object-src 'none'; 
  base-uri 'none';
```

### Same-Origin Policy enforcement

Origin defined as scheme + host + port tuple. Same-origin policy prevents scripts from origin A accessing resources from origin B. Enforcement points: DOM access (script cannot access cross-origin document/iframes), XMLHttpRequest/Fetch (cross-origin requests require CORS), cookies (cross-origin JavaScript cannot read), storage APIs (localStorage/IndexedDB isolated by origin). Exceptions: embedding resources (images/scripts/stylesheets) allowed but reading content denied, postMessage enables cross-origin communication with explicit consent.

## Web Workers implementation

**Execution context isolation.** Workers run on separate threads (OS threads) with separate JavaScript heap, global object (WorkerGlobalScope not Window), and event loop. No shared memory except SharedArrayBuffer, no DOM access (no window/document objects), no synchronous API to main thread. This isolation provides safe parallelism—workers cannot corrupt main thread state.

### Message passing

**Structured clone algorithm.** postMessage serializes message using structured clone: deep copy supporting most JavaScript types (primitives, Objects, Arrays, Maps, Sets, Dates, RegExp, ArrayBuffers, typed arrays), but excluding functions, DOM nodes, Error objects with stacks. Implementation: traverse object graph, serialize each value, reconstruct in target context. Performance cost proportional to message size—avoid posting large objects frequently.

**Transferable objects.** Zero-copy transfer for specific types: ArrayBuffer, MessagePort, ImageBitmap, OffscreenCanvas. Transfer neutered original reference (becomes detached/unusable), ownership moves to target context. Usage: `worker.postMessage(data, [transferableArray])`. Massive performance improvement for large binary data—no serialization, just ownership transfer.

### SharedArrayBuffer and Atomics

SharedArrayBuffer enables true shared memory between threads. Threads share same linear memory backing store, can read/write simultaneously. **Atomic operations required** for thread-safe access: Atomics.load()/store() for reads/writes, Atomics.add()/sub()/and()/or()/xor() for read-modify-write, Atomics.compareExchange() for CAS, Atomics.wait()/notify() for thread coordination (futex-like primitives).

**Security requirements for SharedArrayBuffer.** Initially disabled due to Spectre attacks (enabled high-resolution timers via SharedArrayBuffer-based counters). Re-enabled with cross-origin isolation requirements: COOP: same-origin header isolates document from cross-origin window interactions, COEP: require-corp header requires CORS or CORP for all subresources. Combined, these prevent cross-origin data from entering process, mitigating Spectre.

## Service Workers architecture

**Service worker as programmable proxy.** Service workers intercept network requests from pages within scope, enabling offline functionality, caching strategies, and background sync. Separate registration from script execution—navigator.serviceWorker.register() registers worker at scope, browser manages lifecycle. Service worker runs in separate thread, does not share state with pages, communicates via postMessage.

### Lifecycle management

Service worker lifecycle: **installing** (install event fired, perform setup like cache population), **waiting** (new version waiting for old version to finish), **activating** (activate event fired, cleanup old caches), **activated** (ready to control pages), **redundant** (replaced by newer version or failed). New versions do not activate until old version controls zero pages (unless skipWaiting() called). clients.claim() immediately takes control of uncontrolled pages.

### Fetch event interception

Service worker intercepts fetch events for all requests within scope:
```javascript
self.addEventListener('fetch', event => {
  event.respondWith(
    // Return Response (from cache, network, or generated)
  );
});
```

**respondWith() accepts Response promise.** Worker can: serve from cache, fetch from network, generate synthetic response, return 404, redirect. Complex strategies: cache-first (try cache, fallback to network), network-first, stale-while-revalidate (serve cache, fetch in background). Cache API provides storage interface with CRUD operations on Request/Response pairs.

**Security model.** Service workers require HTTPS (except localhost), scoped by origin and path, cannot intercept cross-origin requests without CORS, maximum scope is script location (preventing script from controlling parent paths). Update checks occur every 24 hours (byte-for-byte comparison), forcing re-download and installation if changed.

## WebAssembly integration

**Compilation and instantiation.** WebAssembly modules are binary format (.wasm files) compiled from languages like C/C++/Rust. JavaScript loads and instantiates modules: WebAssembly.instantiateStreaming(fetch('module.wasm'), importObject) streams compilation during download. Returns { module, instance } where module is compiled code, instance is executable with imports bound.

### JavaScript-WebAssembly interop

**Import object structure.** WASM modules declare imports (functions, memory, tables, globals) satisfied by import object:
```javascript
const importObject = {
  env: {
    memory: new WebAssembly.Memory({ initial: 256, maximum: 512 }),
    consoleLog: (arg) => console.log(arg),
    // ... other imports
  }
};
```

**Linear memory model.** WebAssembly.Memory creates ArrayBuffer-backed linear address space. WASM code accesses via load/store instructions, JavaScript accesses as typed arrays. Memory isolated from JavaScript heap. Out-of-bounds access traps to exception, cannot corrupt other memory. Memory.grow() expands memory by page (64KB), detaches old buffer.

**Type conversions.** WASM numeric types (i32, i64, f32, f64) convert to JavaScript Number (except i64 to BigInt). externref enables passing JavaScript objects to WASM (opaque references). funcref in tables enable indirect calls. No complex type conversions—WASM has no strings/objects, only numbers.

**Integration with optimizing JIT.** TurboFan can inline calls between JavaScript and WASM, optimize across boundary, eliminate conversion overhead for hot paths. WASM itself compiles to optimized machine code via Liftoff (baseline) and TurboFan tiers similar to JavaScript.

## Testing and validation methodology

### Test262 conformance suite

**Test structure and coverage.** Test262 contains 50,000+ tests covering ECMA-262 (language), ECMA-402 (Internationalization), and ECMA-404 (JSON). Tests organized by feature: test/language/ (syntax and semantics), test/built-ins/ (built-in objects), test/annexB/ (legacy features), test/intl402/ (Intl API). Each test file contains YAML frontmatter with metadata: description, esid (spec section), features (required features), flags (onlyStrict, async, module), includes (harness files), negative (expected error).

**Execution requirements.** Test runner must: create fresh ECMAScript realm per test, load harness files (assert.js for assertion utilities, sta.js for standard test API), execute test in both strict and non-strict modes unless flags specify otherwise, handle async tests (requires $DONE callback), support module tests (type: module), capture expected errors (negative frontmatter), and report pass/fail with details.

**Progressive integration strategy.** Start with core language subset: test/language/expressions/ (100-1000 tests), achieving basic functionality. Expand to built-ins: test/built-ins/Object/, test/built-ins/Array/ (5,000-10,000 tests). Add advanced features incrementally: closures, prototypes, classes, async/await, modules. Finally tackle internationalization: test/intl402/ if implementing ECMA-402. Track progress continuously—pass rate should never decrease.

### Chrome DevTools Protocol integration

**Protocol architecture.** CDP enables remote debugging via WebSocket on --remote-debugging-port=9222. JSON-RPC messages control debugger, inspect runtime, profile performance. Protocol organized into domains: Debugger (breakpoints/stepping/pausing), Runtime (evaluation/object inspection), Profiler (CPU profiling/coverage), HeapProfiler (memory analysis), Console (log capture).

**Essential Debugger domain commands.** Debugger.enable() initializes debugging, Debugger.setBreakpoint/setBreakpointByUrl() sets breakpoints, Debugger.pause/resume() controls execution, Debugger.stepOver/stepInto/stepOut() single-step execution, Debugger.evaluateOnCallFrame() evaluates expressions in specific stack frame. Key events: Debugger.scriptParsed (new script loaded, provides scriptId), Debugger.paused (execution stopped at breakpoint/exception/step), Debugger.resumed (continued).

**Profiler domain for performance.** Profiler.enable/start() begins CPU profiling, collecting samples at interval (default 100μs), Profiler.stop() returns Profile with call tree (nodes with callFrame/hitCount/children). Profiler.startPreciseCoverage/takePreciseCoverage() enables code coverage (which functions/lines executed).

**Implementation pathway.** Phase 1: WebSocket server, Debugger.enable, breakpoint setting, pause/resume, scriptParsed events. Phase 2: Stepping commands, expression evaluation, object inspection. Phase 3: CPU profiling, memory snapshots. Debugging support dramatically accelerates engine development—invest early.

### Differential and fuzz testing

**Cross-engine comparison.** Run identical tests on V8, SpiderMonkey, and JavaScriptCore, comparing outputs. Disagreement indicates bug in one or more engines, or ambiguous spec. Focus on observable behavior (returned values, thrown exceptions, console output), not internal details. Helps identify spec interpretation issues.

**Grammar-based fuzzing.** Generate random but syntactically valid JavaScript programs using grammar rules. Coverage-guided fuzzing uses code coverage to guide generation toward unexplored paths. Tools: libFuzzer with custom JavaScript grammar mutator, AFL with JS input corpus. Continuous fuzzing dedicates machines to generate/execute millions of programs, detecting crashes, assertion failures, hangs, memory leaks.

**Regression prevention.** Every fixed bug requires test case added to suite, ensuring bug never recurs. Test suites grow organically from hundreds to tens of thousands of tests. Automated CI runs full suite on every commit, blocking merges that decrease pass rate.

## Performance optimization techniques

### Speculative optimization

**Type specialization from feedback.** Optimizing JIT assumes types based on inline cache observations, generating specialized code for common case. Function processing only integers compiles to integer operations (no type checks, no heap allocation). Guards inserted: CheckInt32(value), bailing out to interpreter if assumption violated. **Economics of speculation:** benefit from specialized code must exceed cost of failed speculation multiplied by failure rate. Measurements show bailout costs 1000-10000× normal instruction, requiring 99.9%+ success rate for profitability.

**Escape analysis and scalar replacement.** Determines whether object escapes function (returned, stored in heap, passed to another function). Non-escaping objects need not allocate on heap—allocate fields as local variables (scalar replacement). Eliminates allocation overhead, GC pressure, enables further optimization on fields. Example: new Point(x, y) not escaping becomes two local variables.

**Inlining for interprocedural optimization.** Replace function call with callee body: eliminates call overhead, enables optimization across former boundary, particularly powerful with specialization (inline monomorphic call sites, specialize inlined code to receiver type). Heuristics limit inlining: function size (small functions inline more readily), call frequency (hot calls worth inlining), call depth (avoid excessive inlining), polymorphism degree (polymorphic sites less profitable).

**Loop optimizations.** Loop-invariant code motion hoists computations outside loops, bounds check elimination removes array bounds checks when induction variable analysis proves safety, loop unrolling duplicates body reducing loop overhead, vectorization uses SIMD instructions for data-parallel operations.

### Inline caching mechanics

**Monomorphic fast path.** Property access compiles to: load object's hidden class, compare with cached hidden class, if equal load from cached offset, else call miss handler. Miss handler: lookup property through full mechanism, record observation in IC, patch IC to cache new shape. Initially uninitialized, becomes monomorphic after first observation, polymorphic after seeing multiple shapes (typically ≤4), megamorphic after many shapes (disables further caching—too many shapes).

**Polymorphic inline cache structure.** Cache array of (shape, offset) pairs with linear search: compare object shape against each cached shape, on match load from corresponding offset. Typically 4-way polymorphic before megamorphic transition. Lookup overhead higher than monomorphic (multiple comparisons) but vastly better than hash table.

**Integration with optimizing JIT.** TurboFan reads IC state, inlines IC checks directly into optimized code. Monomorphic IC with Shape S becomes: CheckShape(object, S), LoadByOffset(object, offset)—two instructions, no call. Polymorphic IC becomes switch on shape. Megamorphic IC falls back to C++ call. Type feedback guides optimization opportunities.

### Watchpoints for constant assumptions

Watchpoint: assertion that condition remains true with invalidation callback. Use cases: property never changed (Math.pow still native implementation), structure never transitions (object shape stable), prototype chain never modified. Enables optimization: inline constant property values, eliminate prototype chain walks, specialize on stable shapes. First violation fires watchpoint, deoptimizes all dependent code. Conservative—only set watchpoints for truly stable conditions.

## Implementation roadmap

**Month 1: Foundation.** Recursive descent parser for ES5 core, AST to bytecode compiler, register-based bytecode format (~50 instructions), bytecode interpreter with dispatch loop, basic runtime (object/array/function implementations), simple mark-and-sweep GC, Test262 core subset (variables, functions, objects, arrays)—target 1000 passing tests.

**Month 2: Essential features.** Complete ES6 core: arrow functions, classes, destructuring, spread/rest, template literals, Promise implementation with microtask queue, event loop foundation, let/const with TDZ, proper closure semantics, expand Test262 coverage to 5000 tests.

**Month 3-4: Module system and async.** ES module loader (parse/link/evaluate), async/await transformation, complete Promise semantics, generator implementation, expand built-ins (Map, Set, WeakMap, WeakSet, Symbol), Test262 coverage to 10,000 tests, generational GC (young generation scavenger, old generation mark-sweep).

**Month 5-6: Browser integration.** Bindings architecture (Web IDL compiler, wrapper generation), core Web APIs (DOM, Events, Timers, Fetch), HTML integration (script execution model, defer/async), Web Workers (threading, message passing), CSSOM integration, requestAnimationFrame, rendering coordination.

**Month 7-9: Optimization.** Inline caching in interpreter, hidden classes (shapes/maps), tagged pointers (SMI optimization), baseline JIT (template JIT for common bytecodes), profiling instrumentation (counters, type feedback), optimizing JIT foundation (IR construction, type specialization), deoptimization infrastructure.

**Month 10-12: Advanced features.** Complete optimizing JIT (escape analysis, inlining, loop opts), concurrent GC (background marking, parallel scavenging), WebAssembly integration (module loading, JS-WASM interop), Service Workers (lifecycle, fetch interception, Cache API), Chrome DevTools Protocol (basic debugging support), comprehensive Test262 coverage (30,000+ tests).

This specification provides autonomous implementation guidance grounded in proven architectures while remaining flexible for innovation. Start simple, test continuously, optimize incrementally, and prioritize correctness over performance. Building a production JavaScript engine is multi-year endeavor requiring deep expertise in language design, compiler optimization, garbage collection, and web platform integration—but the modular architecture described here provides clear path forward.