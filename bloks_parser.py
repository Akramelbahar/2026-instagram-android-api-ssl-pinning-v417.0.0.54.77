"""
https://github.com/Akramelbahar/2026-instagram-android-api-ssl-pinning-v417.0.0.54.77

Bloks Response Parser — Unified extractor for Instagram Bloks API responses.

Extracts all useful data from the `action` lispy string returned by bloks endpoints.
One function per endpoint. Easy to add more.

How it works:
  The bloks response wraps real data inside a lispy expression in `layout.bloks_payload.action`.
  Two cases:
    SUCCESS → JSON payload inside (dsg (fom <id> <n> "<json>") ...)
    ERROR   → No JSON blob. Error title/message in (fom 13799 40 "title" 35 "msg" ...)
              Error type from event strings like "login_wrong_username_error_dialog_shown"
              Flags from (f4i (dkc keys) (dkc vals)) like has_identification_error=true

  This parser handles both uniformly.

Usage:
    from bloks_parser import parse_login
    raw = client.login("user", "pass")
    r = parse_login(raw)
    print(r.status)        # "ok" | "fail"
    print(r.error_type)    # None | "invalid_user" | "bad_password" | "checkpoint" | "two_factor" | ...
    print(r.user)          # dict or None
    print(r.token)         # Bearer IGT:2:... or None
"""

"""

This file contains the public interface of InstagramClient.
Implementation is available to buyers — contact @TrmaCHABA on Telegram.
"""

from __future__ import annotations
import json, re, base64, logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Core — generic bloks action extractors
# ═══════════════════════════════════════════════════════════════════════════════

def get_action(raw: dict) -> str:
    """Pull the action string from a raw bloks response."""
    return raw.get("layout", {}).get("bloks_payload", {}).get("action", "")


def extract_json_blobs(action: str) -> list[dict]:
    """
    Extract all JSON objects embedded as string arguments in the action.
    Pattern: "{\\"key\\":\\"value\\"...}" inside (fom ...) or (dsg ...)
    """
    blobs = []
    i = 0
    while i < len(action):
        if action[i] == '"' and i + 2 < len(action) and action[i+1] == '{' and action[i+2] == '\\':
            j = i + 1
            while j < len(action):
                if action[j] == '"':
                    bs = 0
                    k = j - 1
                    while k > i and action[k] == '\\':
                        bs += 1
                        k -= 1
                    if bs % 2 == 0:
                        raw_str = action[i+1:j]
                        try:
                            s = json.loads('"' + raw_str + '"')
                            obj = _deep_parse(s)
                            if isinstance(obj, dict):
                                blobs.append(obj)
                        except (json.JSONDecodeError, ValueError):
                            pass
                        i = j + 1
                        break
                j += 1
            else:
                i += 1
        else:
            i += 1
    return blobs


def _deep_parse(val: Any) -> Any:
    """Recursively try to parse string values as JSON."""
    if isinstance(val, str):
        s = val.strip()
        if s and s[0] in ('{', '['):
            try:
                return _deep_parse(json.loads(s))
            except (json.JSONDecodeError, ValueError):
                pass
        return val
    if isinstance(val, dict):
        return {k: _deep_parse(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_deep_parse(v) for v in val]
    return val


def extract_kv_maps(action: str) -> list[dict]:
    """
    Extract (f4i (dkc keys...) (dkc values...)) key-value maps.
    Carries flags like should_dismiss_loading, has_identification_error.
    """
    maps = []
    for m in re.finditer(r'\(f4i \(dkc ([^)]+)\) \(dkc ([^)]+)\)\)', action):
        keys = re.findall(r'"([^"]*)"', m.group(1))
        all_vals = re.findall(r'"[^"]*"|true|false|null|\d+', m.group(2))
        parsed_vals = []
        for v in all_vals:
            if v == 'true': parsed_vals.append(True)
            elif v == 'false': parsed_vals.append(False)
            elif v == 'null': parsed_vals.append(None)
            elif v.startswith('"'): parsed_vals.append(v.strip('"'))
            else:
                try: parsed_vals.append(int(v))
                except: parsed_vals.append(v)
        if keys and parsed_vals and len(keys) == len(parsed_vals):
            maps.append(dict(zip(keys, parsed_vals)))
    return maps


def extract_debug_events(action: str) -> list[tuple[str, str]]:
    """Extract (dey "tag" "message") debug events."""
    return re.findall(r'\(dey "([^"]+)" "([^"]+)"\)', action)


def _unescape(s: str) -> str:
    """Decode \\uXXXX sequences left over in action strings."""
    return s.encode().decode('unicode_escape') if '\\u' in s else s


def extract_error_dialog(action: str) -> dict | None:
    """
    Extract error dialog from (fom 13799 40 "title" 35 "message" ...).
    Returns {"title": ..., "message": ..., "buttons": [...]} or None.
    """
    m = re.search(r'\(fom 13799 40 "([^"]*)" 35 "([^"]*)"', action)
    if not m:
        return None
    dialog = {"title": _unescape(m.group(1)), "message": _unescape(m.group(2)), "buttons": []}
    # Extract button labels: (fom 13800 36 "label" ...)
    for btn in re.finditer(r'\(fom 13800 36 "([^"]*)"', action[m.start():]):
        label = btn.group(1)
        if label and not label.startswith('#FF'):
            dialog["buttons"].append(_unescape(label))
    return dialog


def extract_event_steps(action: str) -> list[str]:
    """Extract all login event step names from the action string."""
    return sorted(set(re.findall(r'"(login_[a-z_]+(?:_shown)?)"', action)))


def extract_error_info(action: str) -> str | None:
    """Extract error_info value from (fgq ... (f6m 6 "error_info" "value"))."""
    m = re.search(r'"error_info" "([^"]+)"', action)
    return m.group(1) if m else None


# ═══════════════════════════════════════════════════════════════════════════════
# Error type mapping — maps event step names to clean error types
# ═══════════════════════════════════════════════════════════════════════════════

_ERROR_MAP = {
    "login_wrong_username_error_dialog_shown": "invalid_user",
    "login_wrong_password_error_dialog_shown": "bad_password",
    "login_checkpoint_error_dialog_shown":     "checkpoint",
    "login_two_factor_error_dialog_shown":     "two_factor",
    "login_rate_limit_error_dialog_shown":     "rate_limit",
    "login_sentry_block_error_dialog_shown":   "sentry_block",
    "login_spam_error_dialog_shown":           "spam",
    "login_consent_error_dialog_shown":        "consent_required",
    "login_feedback_required_dialog_shown":    "feedback_required",
    "login_generic_error_dialog_shown":        "generic_error",
    "login_compromised_error_dialog_shown":    "compromised",
    "login_inactive_error_dialog_shown":       "inactive_account",
}

def _detect_error_type(events: list[str], action: str) -> str | None:
    """Detect error type from event step names or action content."""
    # Check event steps against known map
    for event in events:
        if event in _ERROR_MAP:
            return _ERROR_MAP[event]
    
    # Fallback: keyword detection in event names
    for event in events:
        if "wrong_username" in event: return "invalid_user"
        if "wrong_password" in event: return "bad_password"
        if "checkpoint" in event:     return "checkpoint"
        if "two_factor" in event:     return "two_factor"
        if "rate_limit" in event:     return "rate_limit"
        if "sentry" in event:         return "sentry_block"
        if "spam" in event:           return "spam"
        if "consent" in event:        return "consent_required"
        if "feedback" in event:       return "feedback_required"
        if "compromised" in event:    return "compromised"
        if "inactive" in event:       return "inactive_account"
    
    # Fallback: check dey debug messages
    if "[trait:error_generic]" in action:
        return "generic_error"
    if "login_failed" in action and "login_success" not in action:
        return "unknown_error"
    
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Login endpoint parser
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LoginResult:
    """Clean result from login response parsing."""
    # Core status
    status: str = "unknown"             # "ok" | "fail" | "error"
    error_type: Optional[str] = None    # "invalid_user" | "bad_password" | "checkpoint" | "two_factor" | "rate_limit" | "sentry_block" | "spam" | "consent_required" | "feedback_required" | "generic_error" | ...
    error_title: Optional[str] = None   # Dialog title (e.g. "Compte introuvable")
    error_message: Optional[str] = None # Dialog body or API message
    error_info: Optional[str] = None    # Internal error tag (e.g. "generic_error_dialog")
    error_buttons: list = field(default_factory=list)  # Dialog button labels
    
    # User info (on success)
    user_id: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_private: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_business: Optional[bool] = None
    profile_pic_url: Optional[str] = None
    fbid: Optional[int] = None
    
    # Session (on success)
    token: Optional[str] = None         # Bearer IGT:2:...
    session_id: Optional[str] = None
    www_claim: Optional[str] = None
    rur: Optional[str] = None
    mid: Optional[str] = None
    
    # Encryption keys
    enc_key_id: Optional[str] = None
    enc_pub_key: Optional[str] = None
    
    # Checkpoint / 2FA (on challenge)
    checkpoint_url: Optional[str] = None
    two_factor_id: Optional[str] = None
    two_factor_info: Optional[dict] = None
    challenge_context: Optional[dict] = None
    
    # Flags
    has_identification_error: bool = False
    should_dismiss_loading: bool = False
    exact_profile_identified: Optional[bool] = None
    
    # Flow info
    flow_name: Optional[str] = None
    credential_type: Optional[str] = None
    event_steps: list = field(default_factory=list)
    
    # Raw data
    raw_login_response: Optional[dict] = None
    raw_headers: Optional[dict] = None
    raw_blobs: list = field(default_factory=list)


def parse_login(raw: dict) -> LoginResult:
    """
    Parse a raw bloks login response into a clean LoginResult.
    Handles: success, invalid_user, bad_password, checkpoint, 2FA, rate_limit, etc.
    """
    r = LoginResult()
    r.status = raw.get("status", "unknown")
    
    action = get_action(raw)
    if not action:
        r.status = "error"
        r.error_message = "No action in response"
        return r
    
    # ── Extract JSON blobs (success case) ───────────────────────────────
    blobs = extract_json_blobs(action)
    r.raw_blobs = blobs
    
    # ── Find the main login blob ────────────────────────────────────────
    login_blob = None
    for b in blobs:
        if "login_response" in b:
            login_blob = b
            break
    
    if login_blob:
        lr = login_blob.get("login_response", {})
        if isinstance(lr, str):
            try: lr = json.loads(lr)
            except: pass
        r.raw_login_response = lr if isinstance(lr, dict) else None
        
        if isinstance(lr, dict):
            r.status = lr.get("status", r.status)
            r.error_type = lr.get("error_type")
            r.error_message = lr.get("message")
            r.credential_type = lr.get("credential_type")
            
            # Success: logged_in_user
            user = lr.get("logged_in_user", {})
            if user:
                r.user_id = str(user.get("pk", user.get("pk_id", "")))
                r.username = user.get("username")
                r.full_name = user.get("full_name")
                r.phone_number = user.get("phone_number")
                r.is_private = user.get("is_private")
                r.is_verified = user.get("is_verified")
                r.is_business = user.get("is_business")
                r.profile_pic_url = user.get("profile_pic_url")
                r.fbid = user.get("fbid_v2")
            
            # Two-factor
            tfi = lr.get("two_factor_info")
            if tfi:
                r.error_type = r.error_type or "two_factor"
                r.two_factor_info = tfi
                r.two_factor_id = tfi.get("two_factor_identifier") or lr.get("two_factor_identifier")
            
            # Checkpoint
            r.checkpoint_url = lr.get("checkpoint_url")
            if lr.get("challenge"):
                r.challenge_context = lr["challenge"]
                r.error_type = r.error_type or "checkpoint"
        
        # Headers
        hdrs = login_blob.get("headers", {})
        if isinstance(hdrs, str):
            try: hdrs = json.loads(hdrs)
            except: hdrs = {}
        r.raw_headers = hdrs if isinstance(hdrs, dict) else None
        
        if isinstance(hdrs, dict):
            auth = hdrs.get("IG-Set-Authorization", "")
            if auth:
                r.token = auth
                try:
                    b64part = auth.split("IGT:2:")[1] if "IGT:2:" in auth else ""
                    if b64part:
                        decoded = json.loads(base64.b64decode(b64part + "=="))
                        r.session_id = decoded.get("sessionid")
                        r.user_id = r.user_id or str(decoded.get("ds_user_id", ""))
                except Exception:
                    pass
            
            r.enc_key_id = str(hdrs.get("IG-Set-Password-Encryption-Key-Id", "")) or None
            enc_b64 = hdrs.get("IG-Set-Password-Encryption-Pub-Key", "")
            if enc_b64:
                try: r.enc_pub_key = base64.b64decode(enc_b64).decode()
                except: r.enc_pub_key = enc_b64
            
            r.www_claim = hdrs.get("x-ig-set-www-claim")
            uid = hdrs.get("ig-set-ig-u-ds-user-id")
            if uid:
                r.user_id = r.user_id or str(uid)
            r.rur = hdrs.get("ig-set-ig-u-rur")
        
        r.exact_profile_identified = login_blob.get("exact_profile_identified")
    
    # ── Error dialog (error case — no JSON blob) ────────────────────────
    dialog = extract_error_dialog(action)
    if dialog:
        r.error_title = dialog["title"]
        r.error_message = r.error_message or dialog["message"]
        r.error_buttons = dialog["buttons"]
    
    # ── Error info tag ──────────────────────────────────────────────────
    r.error_info = extract_error_info(action)
    
    # ── Event steps ─────────────────────────────────────────────────────
    r.event_steps = extract_event_steps(action)
    
    # ── KV maps (flags) ─────────────────────────────────────────────────
    for kv in extract_kv_maps(action):
        if "has_identification_error" in kv:
            r.has_identification_error = bool(kv["has_identification_error"])
        if "should_dismiss_loading" in kv:
            r.should_dismiss_loading = bool(kv["should_dismiss_loading"])
    
    # ── Debug events → flow name ────────────────────────────────────────
    for tag, msg in extract_debug_events(action):
        r.flow_name = tag
    
    # ── Error type detection ────────────────────────────────────────────
    if not r.error_type and r.has_identification_error:
        r.error_type = _detect_error_type(r.event_steps, action)
    
    # ── Final status normalization ──────────────────────────────────────
    if r.error_type or r.has_identification_error or r.error_title:
        r.status = "fail"
    elif r.token and r.user_id:
        r.status = "ok"
    
    return r


# ═══════════════════════════════════════════════════════════════════════════════
# Add more endpoint parsers below — same pattern:
#
#   @dataclass
#   class SomeResult:
#       ...
#
#   def parse_some_endpoint(raw: dict) -> SomeResult:
#       action = get_action(raw)
#       blobs = extract_json_blobs(action)
#       ...build result from blobs + kv_maps + error_dialog + event_steps...
#
# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# Quick test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    files = sys.argv[1:] or ["file.json"]
    for path in files:
        sep = "=" * 60
        print(f"\n{sep}\n  Parsing: {path}\n{sep}")
        try:
            with open(path) as f:
                raw = json.load(f)
        except FileNotFoundError:
            logger.error("File not found: %s", path)
            continue
        
        r = parse_login(raw)
        
        print(f"  status           : {r.status}")
        print(f"  error_type       : {r.error_type}")
        print(f"  error_title      : {r.error_title}")
        print(f"  error_message    : {r.error_message}")
        print(f"  error_info       : {r.error_info}")
        print(f"  error_buttons    : {r.error_buttons}")
        print(f"  user_id          : {r.user_id}")
        print(f"  username         : {r.username}")
        print(f"  full_name        : {r.full_name}")
        print(f"  phone_number     : {r.phone_number}")
        print(f"  is_private       : {r.is_private}")
        print(f"  is_verified      : {r.is_verified}")
        print(f"  is_business      : {r.is_business}")
        print(f"  token            : {r.token[:50] + '...' if r.token else None}")
        print(f"  session_id       : {r.session_id}")
        print(f"  www_claim        : {r.www_claim}")
        print(f"  rur              : {r.rur}")
        print(f"  enc_key_id       : {r.enc_key_id}")
        print(f"  exact_profile    : {r.exact_profile_identified}")
        print(f"  has_id_error     : {r.has_identification_error}")
        print(f"  flow_name        : {r.flow_name}")
        print(f"  credential_type  : {r.credential_type}")
        print(f"  event_steps      : {r.event_steps}")
        print(f"  checkpoint_url   : {r.checkpoint_url}")
        print(f"  two_factor_id    : {r.two_factor_id}")
        print(f"  blobs found      : {len(r.raw_blobs)}")
