# instagram-android-api

> Reverse-engineered Instagram Android API — v417.0.0.54.77  
> Full header generation · Attestation token emulation · 90+ endpoints · Bloks parser

---

## 🎁 Free Giveaway — Instagram SSL Unpinning (Frida)

Releasing this free to the community. Weeks of RE work — confirmed working on Instagram v417.

### Why standard scripts don't work

Instagram doesn't use OkHttp for its core traffic. It runs a custom C++ networking stack called **MNS (Mobile Networking Stack)** built on **mbedTLS**. Every generic TrustManager / OkHttp unpinning script you find online is useless against it.

### Confirmed call chain (live Frida backtrace)

```
TigonMNSServiceHolder.runEVLoop   (Java)
  → FUN_00373118   TCP event loop
    → FUN_00372b70   connection handler
      → FUN_0038bf6c   MNSTLSContext state machine
        → FUN_00530e20   TLS read/write loop
          → FUN_00542a54   mbedTLS handshake wrapper   ← hooked
            → FUN_004af89c   mbedtls_ssl_handshake_step  ← hooked
```

**Root cause:** `MBEDTLS_ERR_SSL_CONN_EOF (0xffffd900)` — Instagram's server closes the connection when it detects a non-matching TLS fingerprint. This is **server-side JA3/JA4 rejection**, not a local cert pin.

### 5-layer bypass (`frida/bypassSSL.js`)

| Layer | Target | Strategy |
|---|---|---|
| 1 | `FUN_00542a54` handshake wrapper | Intercept failure → force `state = HANDSHAKE_OVER (0x1b)` |
| 2 | `FUN_006d6850` TLS error propagator | Hook + swallow error dispatch |
| 3 | `FUN_004af89c` `mbedtls_ssl_handshake_step` | Force return `0` + state `0x1b` on any error |
| 4 | `FUN_00485120` `MNSTLSContext_MbedCreate` | Patch `authmode=2` → `VERIFY_NONE` at context creation |
| 5 | Java `CertificateVerifier` classes | Blanket bypass via reflection |

**Requirements:**
- The script targets offsets inside `libstartup.so` from Instagram **v417.0.0.54.77** specifically.
- Use the **provided `libstartup.so`** included in this repo — do not extract it from a different APK version or the offsets will be wrong and the hooks will crash.

**Run it:**
```bash
frida -U -f com.instagram.android -l frida/bypassSSL.js --no-pause
```

> Have better offsets for a newer APK? Working on JA3 spoofing?  
> **Open an issue — happy to collaborate.**

---

## 🚀 The Full Service

The SSL bypass gets you visibility into the traffic. Actually working with it is a different problem entirely.

I've built a production-ready Instagram automation service on top of a fully reverse-engineered private API client. Here's what you get access to:

### Authentication & Security

- Full login flow — password, phone OTP, 2FA (TOTP + SMS), checkpoint recovery
- **Attestation tokens emulated in software** — `x-meta-zca` (Zero Code Attestation) and `x-meta-usdid` (Unique Stable Device ID) are cryptographically signed EC tokens that prove to Instagram's servers you're running genuine hardware. Without these, every request gets flagged.
- Android KeyStore registration flow — two-step key upload that ties your signing key to a fake device identity
- Session persistence — auto re-login, `www-claim` rotation, `x-mid` tracking

### Device Fingerprinting & Headers

Every request sends **48 headers** that must be correct down to the exact value — Bloks version ID, capabilities flags, pigeon session format, bandwidth estimates, nav chain timestamps. One wrong field = detection.

The service generates a complete, realistic Android device fingerprint and keeps all 48 headers consistent and rotating correctly across the session lifetime.

### Endpoint Coverage (90+)

| Category | What's available |
|---|---|
| **Growth** | Follow, unfollow, remove follower, block, mute/unmute stories |
| **Engagement** | Like, comment, story like, mark seen, reactions |
| **Feed** | Timeline, user feed, reels tray, clips discover, injected reels |
| **Direct** | Full inbox, send text / photo / reel / voice / media share, pending requests |
| **Stories** | Fetch stories, highlights tray, reel reactions |
| **Search** | User search, place search, explore sections, recent searches |
| **Account** | Profile info, bio update, profile picture, notification settings, contact points |
| **Content** | Story upload, scheduled content, music search, GraphQL queries |
| **Analytics** | Pigeon telemetry, scores bootstrap, creator info, banyan signals |

### Bloks Response Handling

Instagram wraps all responses in a lispy DSL. The service parses it automatically — success payloads, error types (`invalid_user`, `bad_password`, `checkpoint`, `two_factor`), and flags are all extracted cleanly.

---

## 📄 API Interface Preview

`api.py` in this repo contains the **full public interface** of the client — all 90+ method signatures with type hints and docstrings, no implementation.

Browse it to see exactly what you're buying before you commit.

```python
client = InstagramClient(device=device)

client.login(username, password)
client.friendship_create(user_id)
client.direct_send_text(recipient_users, text)
client.feed_timeline()
client.clips_discover()
client.search_account_serp(query)
# ... 90+ more
```

---

## 💬 Get Access

**This is a private service — the code is not public.**

Contact me on Telegram to talk about what you're building, pricing, and access:

> **[@YOUR_HANDLE](https://t.me/YOUR_HANDLE)**

---

## Disclaimer

Security research and educational purposes only. Not affiliated with Meta / Instagram. Use responsibly.
