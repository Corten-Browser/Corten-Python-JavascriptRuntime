# Component: proxies_reflect

**Version:** 0.3.0  
**Type:** core  
**Dependencies:** object_runtime (trap dispatch)

## Contract
READ: `/home/user/Corten-JavascriptRuntime/contracts/proxies_reflect.yaml`

## Requirements
FR-P3-021 to FR-P3-035 from `docs/phase3-requirements.md`

## Implement
1. **Proxy constructor** (target, handler)
2. **13 traps** (get, set, has, deleteProperty, getOwnPropertyDescriptor, defineProperty, ownKeys, getPrototypeOf, setPrototypeOf, isExtensible, preventExtensions, apply, construct)
3. **Proxy invariants enforcement** (TypeError on violation)
4. **Revocable proxies** (Proxy.revocable)
5. **Reflect API** (13 methods mirroring traps)
6. **Proxy-aware operations** (property access, deletion, etc.)

## Files
- `src/proxy.py`, `src/proxy_traps.py`, `src/proxy_invariants.py`
- `src/reflect.py`, `src/revocable_proxy.py`
- Tests: ≥120 unit (5+ per trap), ≥20 integration

## Success: All 13 traps work, invariants enforced, Reflect mirrors Proxy, ≥85% coverage
