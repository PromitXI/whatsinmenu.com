"""
Deterministic pseudo-random generator, mirrored exactly in JS inside the webapp
(see webapp/index.html) so that "today's menu" always matches between:
  - the Python script that runs on the daily schedule (sends WhatsApp / posts Instagram)
  - the webapp the wife opens in her browser

Both sides seed from the same date string (YYYY-MM-DD, Asia/Kolkata) so they
always agree on the same day's pick without needing to talk to each other.
"""

MASK32 = 0xFFFFFFFF


def to_int32(x):
    x &= MASK32
    if x >= 0x80000000:
        x -= 0x100000000
    return x


def to_uint32(x):
    return x & MASK32


def imul(a, b):
    return to_int32((to_uint32(a) * to_uint32(b)) & MASK32)


def urshift(x, n):
    return to_uint32(x) >> n


def hash_seed(s: str) -> int:
    """djb2-style string hash, 32-bit wraparound, matches the JS version."""
    h = 5381
    for ch in s:
        shifted = to_int32((to_uint32(h) << 5) & MASK32)
        h = to_int32(shifted + h + ord(ch))
    return h


def mulberry32(seed: int):
    """Returns a no-arg function that yields the next float in [0, 1)."""
    state = {"a": to_int32(seed)}

    def next_val():
        state["a"] = to_int32(state["a"] + 0x6D2B79F5)
        a = state["a"]
        t = imul(a ^ urshift(a, 15), 1 | a)
        t = to_int32(t)
        total = t + imul(t ^ urshift(t, 7), 61 | t)
        t2 = to_int32(total) ^ t
        result_u = to_uint32(t2 ^ urshift(t2, 14))
        return result_u / 4294967296

    return next_val


def rng_for_date(date_str: str):
    """date_str like '2026-08-19'."""
    return mulberry32(hash_seed(date_str))


def fisher_yates(rng, arr):
    """Deterministic shuffle driven by the given rng() stream. Same algorithm
    must be mirrored in the webapp's JS so both sides draw identical combos."""
    a = list(arr)
    n = len(a)
    for i in range(n - 1, 0, -1):
        j = int(rng() * (i + 1))
        a[i], a[j] = a[j], a[i]
    return a
