"""Cost and queueing models for design (a) at production scale, and the FHE
reference numbers from the literature.

All assumptions are named constants so they can be audited. These reproduce the
ballpark figures in the plan; they are order-of-magnitude engineering estimates,
not quotes.
"""
from __future__ import annotations

import math

# ---- shared assumptions -----------------------------------------------------
GPU_HR_TRAIN = 2.50     # $/GPU-hour amortized for a training-class run
GPU_HR_SERVE = 0.83     # $/GPU-hour for steady serving (~$20/GPU/day)
GPU_TFLOPS = 400.0      # sustained TFLOP/s (realistic, not peak)
USERS = 1000
REQ_PER_USER_DAY = 20


# ---- engraving (full fine-tune) cost: C = 6 * P * T FLOPs -------------------
def engrave_cost(params_B: float, tokens_M_per_user: float, users: int = USERS) -> dict:
    P = params_B * 1e9
    T = tokens_M_per_user * 1e6
    flops_per_user = 6 * P * T
    gpu_seconds = flops_per_user / (GPU_TFLOPS * 1e12)
    gpu_hours = gpu_seconds / 3600
    cost_user = gpu_hours * GPU_HR_TRAIN
    return dict(params_B=params_B, gpu_hours_user=gpu_hours,
                cost_user=cost_user, cost_fleet=cost_user * users)


# ---- Erlang C (M/M/c): 1:1 queued serving -----------------------------------
def erlang_c(lmbda: float, mu: float, c: int) -> float:
    """Probability an arriving request must wait (all c servers busy)."""
    a = lmbda / mu               # offered load in Erlangs
    if a >= c:
        return 1.0
    s = sum(a ** k / math.factorial(k) for k in range(c))
    top = a ** c / (math.factorial(c) * (1 - a / c))
    return top / (s + top)


def mean_wait(lmbda: float, mu: float, c: int) -> float:
    pw = erlang_c(lmbda, mu, c)
    return pw / (c * mu - lmbda) if c * mu > lmbda else float("inf")


def servers_for_wait(lmbda: float, mu: float, target_wait_s: float) -> int:
    c = max(1, int(lmbda / mu) + 1)
    while mean_wait(lmbda, mu, c) > target_wait_s:
        c += 1
        if c > 100000:
            break
    return c


def serving_cost(session_s: float, gpus_per_node: int, label: str,
                 target_wait_s: float = 10.0) -> dict:
    lmbda = USERS * REQ_PER_USER_DAY / 86400.0   # requests/sec
    mu = 1.0 / session_s                          # services/sec per node
    c = servers_for_wait(lmbda, mu, target_wait_s)
    gpus = c * gpus_per_node
    cost_day = gpus * GPU_HR_SERVE * 24
    return dict(label=label, lmbda=lmbda, session_s=session_s, nodes=c,
                gpus=gpus, cost_day=cost_day, wait=mean_wait(lmbda, mu, c))


# ---- FHE reference (from literature extrapolation) --------------------------
def fhe_cost(sec_per_token_lo=33.0, sec_per_token_hi=85.0, n_tokens=500,
             gpus=8) -> dict:
    lo_h = sec_per_token_lo * n_tokens / 3600
    hi_h = sec_per_token_hi * n_tokens / 3600
    return dict(hours=(lo_h, hi_h),
                cost=(lo_h * gpus * GPU_HR_TRAIN, hi_h * gpus * GPU_HR_TRAIN),
                n_tokens=n_tokens, gpus=gpus)


def main():
    print("=" * 64)
    print("ENGRAVING (full fine-tune) cost per user and for a 1k-user fleet.")
    print("Each key => a distinct model => a separate fine-tune (no sharing).")
    print("=" * 64)
    print(f"  {'tokens/user':>12} | {'8B $/user':>10} {'8B fleet':>10} | "
          f"{'70B $/user':>11} {'70B fleet':>10}")
    for tM in (5, 100, 500, 1000):
        e8 = engrave_cost(8, tM); e70 = engrave_cost(70, tM)
        print(f"  {tM:>9}M    | ${e8['cost_user']:>8.1f} ${e8['cost_fleet']/1e6:>7.2f}M | "
              f"${e70['cost_user']:>9.0f} ${e70['cost_fleet']/1e6:>7.1f}M")

    print("\n" + "=" * 64)
    print(f"1:1 QUEUED SERVING  (Erlang C, {USERS} users x {REQ_PER_USER_DAY}/day, "
          f"mean wait < 10s)")
    print("=" * 64)
    for session_s, gpn, label in [(60, 8, "70B/user (8 GPU/node)"),
                                   (30, 1, "8B/user  (1 GPU/node)")]:
        s = serving_cost(session_s, gpn, label)
        print(f"  {label:<24}: {s['nodes']} nodes, {s['gpus']} GPUs, "
              f"${s['cost_day']:.0f}/day, mean wait {s['wait']:.1f}s")

    print("\n" + "=" * 64)
    print("FHE REFERENCE (Llama-2-7B, 33-85 s/token on 8 GPUs; literature)")
    print("=" * 64)
    f = fhe_cost()
    print(f"  {f['n_tokens']} tokens: {f['hours'][0]:.1f}-{f['hours'][1]:.1f} h  "
          f"-> ${f['cost'][0]:.0f}-${f['cost'][1]:.0f} on {f['gpus']} GPUs")
    print("  => FHE is ~3-5 orders of magnitude slower than native serving.")


if __name__ == "__main__":
    main()
