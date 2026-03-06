/**
 * Instagram SSL Bypass v5 — mbedTLS confirmed path
 * 
 * CONFIRMED CALL CHAIN (from backtrace):
 *   TigonMNSServiceHolder.runEVLoop (Java)
 *     → FUN_00373118  +0x373118  (TCP event loop)
 *       → FUN_00372b70  +0x372b70  (connection handler)  
 *         → FUN_0038bf6c  +0x38bf6c  (MNSTLSContext state machine)
 *           → FUN_00530e20  +0x430ed8  (TLS read/write loop)
 *             → FUN_00542a54  +0x442ac8  (mbedTLS handshake wrapper)
 *               → FUN_004af89c            (mbedtls_ssl_handshake_step)
 *
 * ERROR: MBEDTLS_ERR_SSL_CONN_EOF (0xffffd900)
 *   = Server closed the connection during handshake.
 *   = Our proxy's TLS fingerprint was rejected by Instagram's server.
 *   = This is NOT a local cert pin — it's server-side TLS fingerprint detection.
 *
 * BYPASS STRATEGY:
 *   The wrapper FUN_00542a54 receives the result of mbedtls_ssl_handshake_step.
 *   It checks for state == 0x1b (HANDSHAKE_OVER) to signal success.
 *   On EOF, the state machine at FUN_00530e20 calls FUN_006d6850 (error handler).
 *   
 *   Target: FUN_00542a54 at +0x442a54
 *   - param_1 = MNS wrapper object
 *   - param_1+0x210 = mbedtls_ssl_context*
 *   - param_1+0x218 = mbedtls_ssl_context.state (int)
 *   - param_1+0x408 = last error code
 *   
 *   Force: when handshake_step returns EOF, fake the state as HANDSHAKE_OVER (0x1b)
 *   so the wrapper returns success (0) instead of calling the error path.
 *
 *   ALSO: hook the error dispatch in FUN_00530e20 to swallow the error branch.
 *                     This file contains the public interface of InstagramClient.
 *                     Implementation is available to buyers — contact @TrmaCHABA on Telegram.

 */





"use strict";

const GHIDRA_BASE = 0x100000;
const O = (addr, base) => base.add(addr - GHIDRA_BASE);

function waitForModule(names, cb) {
  for (const n of names) {
    const m = Process.findModuleByName(n);
    if (m) { cb(m); return; }
  }
  const id = setInterval(() => {
    for (const n of names) {
      const m = Process.findModuleByName(n);
      if (m) { clearInterval(id); cb(m); return; }
    }
  }, 100);
}

waitForModule(['libstartup.so', 'libmain.so'], mod => {
  const base = mod.base;
  console.log(`[+] base: ${base}`);

  // ── LAYER 1: Replace mbedTLS handshake wrapper FUN_00542a54 ──────────────
  // Ghidra: 0x542a54 → offset: 0x442a54
  //
  // Original logic:
  //   if ctx+0x210 == null → error FFFF8F00
  //   loop: call mbedtls_ssl_handshake_step(ctx+0x210)
  //     if state == 0x1b → return 0 (success)
  //     if ret == -0x6900 → return 2 (WANT_READ)
  //     if ret == -0x6880 → return 3 (WANT_WRITE)
  //     else → log error, return 1 (failure)
  //
  // Bypass: intercept, and if the inner loop would fail, force state=0x1b
  // so it exits the loop and returns 0 (success).
  //
  // We do this by hooking onEnter to save ctx, and hooking onLeave:
  // if return value == 1 (failure), force it to 0 and fix the state.

  try {
    const wrapperAddr = O(0x542a54, base);
    Interceptor.attach(wrapperAddr, {
      onEnter(args) {
        this.param1 = args[0]; // MNS object
        this.param2 = args[1]; // error output ptr
      },
      onLeave(ret) {
        const result = ret.toInt32();
        if (result === 1) {
          // Failure path — check what error was set
          try {
            const errCode = this.param1.add(0x408).readU32();
            console.log(`[INTERCEPT] handshake_wrapper failed, errCode=0x${errCode.toString(16)}`);

            // Force state to HANDSHAKE_OVER (0x1b = 27)
            // state is at param1+0x218 (inside mbedtls_ssl_context at param1+0x210)
            const sslCtxPtr = this.param1.add(0x210).readPointer();
            if (!sslCtxPtr.isNull()) {
              // mbedtls_ssl_context.state is at offset 0x8 from the ssl_context start
              // Ghidra offset 0x218 - 0x210 = 0x8
              const stateOffset = 0x8; // within ssl_context
              const currentState = sslCtxPtr.add(stateOffset).readU32();
              console.log(`[INTERCEPT] ssl state=${currentState}, forcing to 0x1b (HANDSHAKE_OVER)`);
              sslCtxPtr.add(stateOffset).writeU32(0x1b);
              // Clear error code
              this.param1.add(0x408).writeU32(0);
            }
            // Force return value to 0 (success)
            ret.replace(ptr(0));
            console.log(`[BYPASS] handshake_wrapper → forced success`);
          } catch(e) {
            console.log(`[!] patch error: ${e.message}`);
          }
        }
      }
    });
    console.log(`[+] handshake_wrapper hooked @ ${O(0x542a54, base)}`);
  } catch(e) {
    console.log(`[!] handshake_wrapper: ${e.message}`);
  }

  // ── LAYER 2: Hook error dispatch in TLS event loop FUN_00530e20 ───────────
  // Ghidra: 0x530e20 → offset: 0x430e20
  // At the point where iVar5 (handshake result) goes to error branch,
  // it calls FUN_006d6850 (error propagator).
  // Hook FUN_006d6850 to swallow errors.
  try {
    const errPropagator = O(0x6d6850, base);
    Interceptor.attach(errPropagator, {
      onEnter(args) {
        console.log(`[INTERCEPT] FUN_006d6850 (TLS error propagator) called — swallowing`);
        // We can't easily prevent the call, but we can note it.
        // Layer 1 should prevent us from ever reaching here.
      }
    });
    console.log(`[+] TLS error propagator hooked @ ${O(0x6d6850, base)}`);
  } catch(e) {
    console.log(`[!] error propagator: ${e.message}`);
  }

  // ── LAYER 3: Hook the state check directly in the wrapper ─────────────────
  // FUN_00542a54 checks: if (state == 0x1b) → success
  // We patch the MEMORY of the running ssl_context after each step
  // so the loop condition triggers.
  // Approach: hook FUN_004af89c (mbedtls_ssl_handshake_step) and force return 0
  // when it would return an error, AND set state = 0x1b.
  // 
  // We don't have the decompile of 004af89c but we know:
  //   - called as: iVar1 = FUN_004af89c(param_1 + 0x210)
  //   - param_1+0x210 = mbedtls_ssl_context*
  //   - returns 0 = step done (keep looping), -0x6900 = WANT_READ, error = negative
  //   - state field within ssl_context at offset 0x8 (confirmed above)
  try {
    const handshakeStep = O(0x4af89c, base);
    Interceptor.attach(handshakeStep, {
      onEnter(args) {
        this.sslCtx = args[0]; // mbedtls_ssl_context*
      },
      onLeave(ret) {
        const r = ret.toInt32();
        // Any negative error that isn't WANT_READ/WANT_WRITE → force HANDSHAKE_OVER
        if (r !== 0 && r !== -0x6900 && r !== -0x6880) {
          try {
            const state = this.sslCtx.add(0x8).readU32();
            console.log(`[INTERCEPT] handshake_step error=0x${(r>>>0).toString(16)} state=${state} → forcing OVER`);
            this.sslCtx.add(0x8).writeU32(0x1b);
            ret.replace(ptr(0)); // pretend step succeeded
            console.log(`[BYPASS] handshake_step → forced 0`);
          } catch(e) {
            console.log(`[!] step patch: ${e.message}`);
          }
        }
      }
    });
    console.log(`[+] mbedtls_ssl_handshake_step hooked @ ${O(0x4af89c, base)}`);
  } catch(e) {
    console.log(`[!] handshake_step: ${e.message}`);
  }

  // ── LAYER 4: MNSTLSContext_MbedCreate — patch authmode at creation ─────── 
  // Ghidra: 0x48512c → 0x38512c
  // After ctx is created, find and zero the authmode field in mbedtls_ssl_config.
  // The conf dump showed no value=2 in first 0x80 bytes — scan wider.
  try {
    Interceptor.attach(O(0x48512c, base), {
      onLeave(ret) {
        try {
          // The MNS TLS context object, not the raw mbedtls_ssl_context.
          // mbedtls_ssl_config is embedded in it. Scan for authmode=2
          // in first 0x400 bytes of the object.
          const obj = ret;
          if (obj.isNull()) return;
          let found = 0;
          for (let off = 0; off < 0x800; off += 4) {
            try {
              const v = obj.add(off).readU32();
              if (v === 2) {
                // Candidate authmode field
                obj.add(off).writeU32(0); // MBEDTLS_SSL_VERIFY_NONE
                console.log(`[PATCH] MNSTLSContext+0x${off.toString(16)} = 2 → 0 (VERIFY_NONE)`);
                found++;
              }
            } catch(e2) { break; }
          }
          console.log(`[+] MNSTLSContext_MbedCreate: patched ${found} authmode candidates`);
        } catch(e) {
          console.log(`[!] MNSTLSContext patch: ${e.message}`);
        }
      }
    });
    console.log(`[+] MNSTLSContext_MbedCreate hooked`);
  } catch(e) {
    console.log(`[!] MNSTLSContext_MbedCreate: ${e.message}`);
  }

  // ── LAYER 5: Java CertificateVerifier (from previous session) ─────────────
  Java.perform(() => {
    const targets = [
      'com.facebook.mobilenetwork.internal.certificateverifier.CertificateVerifier',
      'com.facebook.mobilenetwork.internal.certificateverifier.DefaultCertificateVerifier',
      'com.facebook.mobilenetwork.internal.certificateverifier.MNSCertificateVerifier',
    ];
    for (const cls of targets) {
      try {
        const C = Java.use(cls);
        const methods = C.class.getDeclaredMethods();
        methods.forEach(m => {
          const name = m.getName();
          try {
            const overloads = C[name].overloads;
            overloads.forEach(ol => {
              ol.implementation = function() {
                console.log(`[JAVA BYPASS] ${cls}.${name}() → bypassed`);
                const ret = ol.returnType.className;
                if (ret === 'boolean' || ret === 'java.lang.Boolean') return true;
                if (ret === 'int' || ret === 'java.lang.Integer') return 0;
                if (ret === 'void') return;
                return null;
              };
            });
            console.log(`[+] Java hooked: ${cls}.${name}`);
          } catch(e2) {}
        });
      } catch(e) {}
    }
  });

  console.log('\n[*] Bypass v5 armed — 5 layers targeting confirmed mbedTLS path\n');
});

