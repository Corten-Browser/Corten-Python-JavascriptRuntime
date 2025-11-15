# Component: timers

**Version:** 0.3.0  
**Type:** core  
**Dependencies:** event_loop (timer queue integration)

## Contract
READ: `/home/user/Corten-JavascriptRuntime/contracts/timers.yaml`

## Requirements
FR-P3-081 to FR-P3-090 from `docs/phase3-requirements.md`

## Implement
1. **setTimeout(callback, delay, ...args)** - Schedule callback
2. **clearTimeout(id)** - Cancel timeout
3. **setInterval(callback, delay, ...args)** - Repeat callback
4. **clearInterval(id)** - Stop interval
5. **Timer queue** (priority queue by expiration time)
6. **Event loop integration** (check/execute timers each iteration)
7. **Nested timeout clamping** (≥4ms after 5 levels)
8. **Timer ID generation** (incrementing or random)

## Files
- `src/timers.py`, `src/timer_queue.py`, `src/timer_integration.py`
- Tests: ≥35 unit, ≥10 integration

## Success: setTimeout/setInterval work, clearTimeout/clearInterval work, nesting clamps correctly, ≥85% coverage
