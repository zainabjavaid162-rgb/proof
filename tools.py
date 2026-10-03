"""
tools.py - plain Python checks (no AI needed).

Rule of thumb: let code do the maths and fixed rules, and let the AI agents
do the judgement and writing. This keeps numbers correct and saves tokens.
"""

import hashlib
from datetime import date

# ---------------------------------------------------------------------------
# 1) Verhoeff check digit
#    A checksum that catches typos (wrong digit, swapped digits).
#    Here we treat the LAST digit of the NTN as the check digit.
#    NOTE: this is a demo rule from the PROOF stack, not FBR's official logic.
# ---------------------------------------------------------------------------
_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6], [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]
_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2], [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]
_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def verhoeff_is_valid(number: str) -> bool:
    """True if the full digit string (including its last check digit) is valid."""
    c = 0
    for i, digit in enumerate(reversed(number)):
        c = _D[c][_P[i % 8][int(digit)]]
    return c == 0


def verhoeff_make_check_digit(number: str) -> str:
    """Return the check digit to add to the end of `number` (used for demo NTNs)."""
    c = 0
    for i, digit in enumerate(reversed(number)):
        c = _D[c][_P[(i + 1) % 8][int(digit)]]
    return str(_INV[c])


def check_ntn(ntn: str) -> dict:
    """Check format (7 digits + 1 check digit, e.g. 1234567-8) and Verhoeff."""
    digits = ntn.replace("-", "").strip()
    if not digits.isdigit() or len(digits) != 8:
        return {"ok": False, "reason": "NTN must be 8 digits (7 + check digit), e.g. 1234567-8"}
    if not verhoeff_is_valid(digits):
        return {"ok": False, "reason": "Check digit does not match (possible typo or fake NTN)"}
    return {"ok": True, "reason": "Format and check digit are valid"}


# ---------------------------------------------------------------------------
# 2) Buyer payment history - DEMO DATA.
#    In the real product this would come from FBR, bank data or your own records.
# ---------------------------------------------------------------------------
DEMO_BUYERS = {
    "Engro Foods":        {"invoices_paid": 48, "paid_on_time": 46, "avg_days_late": 3},
    "Packages Ltd":       {"invoices_paid": 31, "paid_on_time": 27, "avg_days_late": 9},
    "Nishat Mills":       {"invoices_paid": 22, "paid_on_time": 17, "avg_days_late": 18},
    "Adidas Sourcing PK": {"invoices_paid": 60, "paid_on_time": 59, "avg_days_late": 1},
}


def check_buyer(buyer_name: str) -> dict:
    record = DEMO_BUYERS.get(buyer_name)
    if not record:
        return {"known": False, "on_time_rate": None,
                "summary": "No payment history on file for this buyer (higher risk)."}
    rate = record["paid_on_time"] / record["invoices_paid"]
    return {"known": True, "on_time_rate": round(rate * 100, 1),
            "summary": (f"{record['invoices_paid']} past invoices, {rate:.0%} paid on time, "
                        f"average {record['avg_days_late']} days late.")}


# ---------------------------------------------------------------------------
# 3) Invoice fingerprint (the value PROOF would write to Polygon).
#    Same invoice details -> same hash, so a second funding attempt is caught.
# ---------------------------------------------------------------------------
def invoice_hash(seller_ntn: str, invoice_no: str, buyer: str, amount: float) -> str:
    raw = f"{seller_ntn.replace('-', '')}|{invoice_no.strip().upper()}|{buyer.strip().upper()}|{amount:.2f}"
    return "0x" + hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# 4) Investor and SME maths for the factoring deal.
# ---------------------------------------------------------------------------
def deal_numbers(amount: float, days: int = 90, advance_pct: float = 90.0,
                 investor_pct: float = 95.0, platform_fee_pct: float = 1.5) -> dict:
    advance = amount * advance_pct / 100          # cash the SME gets today
    investor_back = amount * investor_pct / 100   # what the investor receives later
    platform_fee = amount * platform_fee_pct / 100
    sme_balance = amount - investor_back - platform_fee  # paid to SME when buyer pays
    profit = investor_back - advance
    roi = profit / advance * 100
    annual = ((investor_back / advance) ** (365 / days) - 1) * 100
    sme_cost_pct = (investor_back - advance + platform_fee) / amount * 100
    return {
        "invoice_amount": round(amount),
        "advance_to_sme": round(advance),
        "investor_receives": round(investor_back),
        "investor_profit": round(profit),
        "investor_roi_pct": round(roi, 2),
        "investor_annualised_pct": round(annual, 1),
        "platform_fee": round(platform_fee),
        "sme_balance_later": round(sme_balance),
        "sme_total_cost_pct": round(sme_cost_pct, 2),
        "days": days,
    }


def days_until(due: date) -> int:
    return max((due - date.today()).days, 1)
