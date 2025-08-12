## 1. Purpose

This PRD defines a minimal, pragmatic implementation to prevent network TLS/HTTPS interception appliances (corporate proxies, AV with root CA, on-path middleboxes) from reading sensitive payloads sent between browser clients and a FastAPI server (Python 3.13). The solution uses client-side AES-GCM encryption prior to transport over HTTPS and a hard-coded AES key embedded in JavaScript (as requested by the client).

This document describes scope, requirements, design, APIs, implementation notes, risks, testing, rollout, and recommended mitigations.

---

## 2. Scope

* **In scope:**

  * Client-side AES-GCM encryption of request payloads in the browser (JavaScript).
  * Server-side decryption using FastAPI (Python 3.13) with `cryptography` AESGCM.

* **Out of scope:**

  * Protection against fully compromised clients (malware, malicious browser extensions).
  * End-to-end multi-recipient sharing, key-management servers, or PKI.
  * Native apps or browser extensions to hide keys from page JS.

---

## 3. Goals & Success Criteria

**Goals**

* Ensure the notes content for both directly from/to client to/from web server ciphertext unknown to on-path HTTPS/TLS interceptors.
* Keep server changes minimal.

**Success criteria**

* Interceptor seeing HTTP bodies cannot decrypt payload without the AES key.

---

## 4. Threat Model & Assumptions

**Threats mitigated**

* Passive or active network TLS interception appliances that terminate TLS using a trusted CA present on client machines.

**Not mitigated / assumptions**

* If an attacker controls or compromises the browser environment (malicious extension, XSS, OS compromise), they can read the hard-coded key or plaintext before encryption. This solution assumes endpoints are not fully compromised.
* Hard-coding a symmetric key in JavaScript is insecure by design: we accept this as a tradeoff for simplicity.

---

## 5. Requirements

### Functional

1. Browser must encrypt sensitive request bodies (JSON or file chunks) using AES-GCM with a single shared key.
2. Server must accept encrypted payloads and decrypt them using the same key.
3. Also, notes content must encrypt for data from server to client(browser)

### Non-functional

1. Performance: encryption must not block UI for large payloads (use Web Worker for >5MB).
2. Compatibility: support modern browsers (Chrome, Firefox, Edge, Safari) with Web Crypto.
3. Maintainability: minimal code and clear comments; documented key rotation process.
