"""
Saharasoil model engine — pure functions, no Streamlit dependency, so they can be
unit-tested against the source workbook (Saharasoil_B2B_Model_Reanchored.xlsx)
before being wired into the dashboard.
"""
import numpy as np

QUARTER_LABELS = ["Y1 Q1", "Y1 Q2", "Y1 Q3", "Y1 Q4",
                   "Y2 Q1", "Y2 Q2", "Y2 Q3", "Y2 Q4",
                   "Y3 Q1", "Y3 Q2", "Y3 Q3", "Y3 Q4"]

DEFAULT_SIGNINGS = [1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5]

DEFAULTS = dict(
    price=900.0,                 # AED / tonne, bulk
    topdress_pct=0.20,           # top-dressing revenue as % of bulk revenue
    topdress_cogs_pct=0.40,      # top-dressing COGS as % of its own revenue
    feedstock_cost=100.0,        # AED/tonne — camel manure offtake
    biochar_cost=350.0,          # AED/tonne — blended-in biochar share
    blending_cost=100.0,         # AED/tonne — blending, finishing, packaging
    tonnes_per_contractor=6.0,   # THE swing variable, per Demand-Side Risk tab
    churn=0.05,                  # quarterly contractor churn
    signings_multiplier=1.0,     # scales the whole signings ramp up/down
    opex_y1y2=63000.0,           # AED/quarter, Years 1-2
    opex_y3=72000.0,             # AED/quarter, Year 3
    onetime_moccae=40000.0,      # AED, Q1 only
    deposit_pct=0.30,            # upfront deposit on signing
    collection_lag_q=1,          # quarters until balance is collected
    funding_ask=550000.0,        # AED
    cac_narrow=2500.0,           # AED per contractor, acquisition activity only
    bd_cost_per_quarter=30000.0, # AED/quarter, founder/BD time (also inside opex)
)


def compute_model(a: dict) -> dict:
    """Recompute the full 12-quarter model from an assumptions dict `a`.
    Mirrors Saharasoil_B2B_Model_Reanchored.xlsx exactly at default inputs."""
    n = 12
    signings = np.array(DEFAULT_SIGNINGS, dtype=float) * a["signings_multiplier"]

    active = np.zeros(n)
    for i in range(n):
        active[i] = signings[i] if i == 0 else active[i - 1] * (1 - a["churn"]) + signings[i]

    cogs_per_tonne = a["feedstock_cost"] + a["biochar_cost"] + a["blending_cost"]

    tonnes = active * a["tonnes_per_contractor"]
    bulk_rev = tonnes * a["price"]
    topdress_rev = bulk_rev * a["topdress_pct"]
    total_rev = bulk_rev + topdress_rev

    bulk_cogs = tonnes * cogs_per_tonne
    topdress_cogs = topdress_rev * a["topdress_cogs_pct"]
    total_cogs = bulk_cogs + topdress_cogs

    gross_profit = total_rev - total_cogs
    gross_margin = np.divide(gross_profit, total_rev, out=np.zeros(n), where=total_rev != 0)

    opex = np.array([a["opex_y1y2"]] * 8 + [a["opex_y3"]] * 4)
    onetime = np.zeros(n); onetime[0] = a["onetime_moccae"]
    total_opex = opex + onetime

    ebitda = gross_profit - total_opex
    cum_ebitda = np.cumsum(ebitda)

    # Cash: deposit collected same quarter, balance collected `collection_lag_q` later
    deposit = total_rev * a["deposit_pct"]
    balance = total_rev * (1 - a["deposit_pct"])
    lag = int(a["collection_lag_q"])
    balance_collected = np.zeros(n)
    for i in range(n):
        if i - lag >= 0:
            balance_collected[i] = balance[i - lag]
    cash_collected = deposit + balance_collected
    cash_paid_out = total_cogs + total_opex
    net_cash_flow = cash_collected - cash_paid_out
    cum_cash_before = np.cumsum(net_cash_flow)
    cum_cash_incl = a["funding_ask"] + cum_cash_before

    trough = cum_cash_before.min()
    recommended_ask = abs(trough) * 1.10
    runway_ok = cum_cash_incl.min() >= 0

    ebitda_positive_idx = next((i for i, v in enumerate(ebitda) if v > 0), None)
    ebitda_positive_q = QUARTER_LABELS[ebitda_positive_idx] if ebitda_positive_idx is not None else "Not within 3 years"

    # Unit economics (per-tonne / per-contractor), always internally consistent
    bulk_gp_per_tonne = a["price"] - cogs_per_tonne
    bulk_margin = bulk_gp_per_tonne / a["price"] if a["price"] else 0
    topdress_rev_basis = a["price"] * a["topdress_pct"]
    topdress_gp_per_unit = topdress_rev_basis * (1 - a["topdress_cogs_pct"])
    topdress_margin = 1 - a["topdress_cogs_pct"]

    rev_per_contractor_q = a["tonnes_per_contractor"] * a["price"] * (1 + a["topdress_pct"])
    gp_per_contractor_q = (a["tonnes_per_contractor"] * bulk_gp_per_tonne
                            + a["tonnes_per_contractor"] * topdress_rev_basis * (1 - a["topdress_cogs_pct"]))

    avg_signings_per_q = float(np.mean(signings)) if signings.sum() > 0 else 1.0
    cac_all_in = a["cac_narrow"] + (a["bd_cost_per_quarter"] / avg_signings_per_q if avg_signings_per_q else 0)

    life_q = 1 / a["churn"] if a["churn"] else np.inf
    ltv = gp_per_contractor_q * life_q
    ltv_cac_narrow = ltv / a["cac_narrow"] if a["cac_narrow"] else np.nan
    ltv_cac_allin = ltv / cac_all_in if cac_all_in else np.nan
    cac_payback_q = a["cac_narrow"] / gp_per_contractor_q if gp_per_contractor_q else np.nan

    # break-even contractors at Year-3 opex level
    breakeven_contractors_y3 = a["opex_y3"] / gp_per_contractor_q if gp_per_contractor_q else np.nan

    # churn sensitivity for LTV:CAC (all-in)
    churn_grid = [0.05, 0.10, 0.15, 0.20, 0.25]
    ltv_cac_sensitivity = [
        (gp_per_contractor_q * (1 / c)) / cac_all_in if cac_all_in else np.nan for c in churn_grid
    ]

    # tonnes/contractor sensitivity (Demand-Side Risk tab)
    tonnes_grid = [4, 6, 8, 10]
    tonnes_sensitivity = []
    for t in tonnes_grid:
        rev_c = t * a["price"] * (1 + a["topdress_pct"])
        gp_c = t * bulk_gp_per_tonne + t * topdress_rev_basis * (1 - a["topdress_cogs_pct"])
        be = a["opex_y3"] / gp_c if gp_c else np.nan
        tonnes_sensitivity.append(dict(tonnes=t, rev_per_contractor_q=rev_c, gp_per_contractor_q=gp_c,
                                        breakeven_contractors=be, rev_per_contractor_yr=rev_c * 4))

    return dict(
        quarters=QUARTER_LABELS, signings=signings, active=active, tonnes=tonnes,
        bulk_rev=bulk_rev, topdress_rev=topdress_rev, total_rev=total_rev,
        bulk_cogs=bulk_cogs, topdress_cogs=topdress_cogs, total_cogs=total_cogs,
        gross_profit=gross_profit, gross_margin=gross_margin,
        opex=total_opex, ebitda=ebitda, cum_ebitda=cum_ebitda,
        deposit=deposit, balance=balance, cash_collected=cash_collected,
        cash_paid_out=cash_paid_out, net_cash_flow=net_cash_flow,
        cum_cash_before=cum_cash_before, cum_cash_incl=cum_cash_incl,
        trough=trough, recommended_ask=recommended_ask, runway_ok=runway_ok,
        ebitda_positive_q=ebitda_positive_q,
        cogs_per_tonne=cogs_per_tonne, bulk_gp_per_tonne=bulk_gp_per_tonne, bulk_margin=bulk_margin,
        topdress_rev_basis=topdress_rev_basis, topdress_gp_per_unit=topdress_gp_per_unit, topdress_margin=topdress_margin,
        rev_per_contractor_q=rev_per_contractor_q, gp_per_contractor_q=gp_per_contractor_q,
        cac_narrow=a["cac_narrow"], cac_all_in=cac_all_in, avg_signings_per_q=avg_signings_per_q,
        life_q=life_q, ltv=ltv, ltv_cac_narrow=ltv_cac_narrow, ltv_cac_allin=ltv_cac_allin,
        cac_payback_q=cac_payback_q, breakeven_contractors_y3=breakeven_contractors_y3,
        churn_grid=churn_grid, ltv_cac_sensitivity=ltv_cac_sensitivity,
        tonnes_grid=tonnes_grid, tonnes_sensitivity=tonnes_sensitivity,
        year1_rev=float(total_rev[0:4].sum()), year2_rev=float(total_rev[4:8].sum()), year3_rev=float(total_rev[8:12].sum()),
    )


if __name__ == "__main__":
    m = compute_model(DEFAULTS)
    checks = [
        ("EBITDA Q1", m["ebitda"][0], -100252, 1),
        ("EBITDA Q12", m["ebitda"][11], 2481.28, 1),
        ("Cumulative EBITDA Q12", m["cum_ebitda"][11], -433464.31, 1),
        ("Active contractors Q12", m["active"][11], 27.1038135401047, 4),
        ("Total revenue Q1", m["total_rev"][0], 6480, 1),
        ("Total revenue Q12", m["total_rev"][11], 175632.711739878, 1),
        ("Year 1 revenue", m["year1_rev"], 80756.19, 0),
        ("Year 2 revenue", m["year2_rev"], 290140.751481188, 0),
        ("Year 3 revenue", m["year3_rev"], 568881.535461124, 0),
        ("Cum cash incl funding Q1", m["cum_cash_incl"][0], 445212, 0),
        ("Cum cash incl funding Q12", m["cum_cash_incl"][11], -6407.21077386069, 0),
        ("Deepest trough", m["trough"], -556407.210773861, 0),
        ("Recommended ask", m["recommended_ask"], 612047.931851247, 0),
        ("LTV:CAC narrow", m["ltv_cac_narrow"], 20.256, 2),
        ("LTV:CAC all-in", m["ltv_cac_allin"], 3.77654237288136, 2),
        ("CAC all-in", m["cac_all_in"], 13409.0909090909, 1),
        ("Breakeven contractors Y3", m["breakeven_contractors_y3"], 28.436018957346, 1),
    ]
    all_ok = True
    for name, got, expect, dp in checks:
        ok = abs(got - expect) < 10 ** (-dp) * 5 if dp > 0 else abs(got - expect) < 5
        status = "OK " if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"[{status}] {name}: got={got:.4f} expect={expect:.4f}")
    print("\nALL CHECKS PASSED" if all_ok else "\nSOME CHECKS FAILED")
