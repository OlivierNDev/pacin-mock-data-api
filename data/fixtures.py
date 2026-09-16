"""
Synthetic data generation for PACIN Mock API.
Generates 24 months of data (2024-09 to 2026-08) for two test subjects.
"""

import hashlib
import random
from datetime import date, timedelta

random.seed(42)  # Reproducible data

MONTHS = []
for y in range(2024, 2027):
    for m in range(1, 13):
        key = f"{y}-{m:02d}"
        if "2024-09" <= key <= "2026-08":
            MONTHS.append(key)

SUBJECT_PROFILES = {
    "PACIN_TEST_001": {
        "name": "Alice Uwimana",
        "age": 28,
        "district": "Gasabo",
        "city": "Kigali",
        "national_id": "1199850101110001",
        "phone_hash": hashlib.sha256(b"+250788100001").hexdigest(),
    },
    "PACIN_TEST_002": {
        "name": "Jean-Pierre Habimana",
        "age": 34,
        "district": "Musanze",
        "city": "Musanze",
        "national_id": "1199760202220002",
        "phone_hash": hashlib.sha256(b"+250788200002").hexdigest(),
    },
}

def _days_in_month(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    if m == 12: return (date(y+1,1,1)-date(y,m,1)).days
    return (date(y,m+1,1)-date(y,m,1)).days

def _random_date_in_month(ym):
    return f"{ym}-{random.randint(1,_days_in_month(ym)):02d}"

_ALICE_CP_IN = ["KIGALI TECH LTD","IREMBO GOV","UMURIMO SALARY","JEAN MUKIZA","MARIE INGABIRE"]
_ALICE_CP_OUT = ["SIMBA SUPERMARKET","MTN AIRTIME","WASAC PAYMENT","RECO ELECTRICITY","KFC KIGALI","BANK OF KIGALI"]
_JP_CP_IN = ["MUSANZE COOP","PATRICK NZIZA","CASH DEPOSIT","AGRI PAYMENT","UNKNOWN SENDER"]
_JP_CP_OUT = ["MTN AIRTIME","CASH WITHDRAWAL","BETTING SHOP","LOCAL BAR","MARKET VENDOR","AIRTEL BUNDLES"]

def _gen_momo_alice(month_idx, ym, prev_balance):
    txns = []
    balance = prev_balance
    total_in = total_out = 0
    days = _days_in_month(ym)
    salary = random.randint(75000, 85000)
    sal_day = min(random.randint(25,28), days)
    balance += salary; total_in += salary
    txns.append({"id": f"TXN-A-{ym}-SAL", "date": f"{ym}-{sal_day:02d}", "type": "RECEIVE",
        "amount_rwf": salary, "counterparty": "UMURIMO SALARY", "balance_after_rwf": balance, "description": "Monthly salary"})
    for i in range(random.randint(18,25)-1):
        tx_type = random.choice(["RECEIVE","SEND","SEND","PAYMENT","PAYMENT","AIRTIME"])
        if tx_type == "RECEIVE":
            amt = random.randint(2000,15000); cp = random.choice(_ALICE_CP_IN); balance += amt; total_in += amt; desc = f"Transfer from {cp}"
        elif tx_type == "AIRTIME":
            amt = random.choice([500,1000,2000,3000]); cp = "MTN AIRTIME"; balance -= amt; total_out += amt; desc = "Airtime"
        else:
            amt = random.randint(1000,12000); cp = random.choice(_ALICE_CP_OUT); balance -= amt; total_out += amt; desc = f"Payment to {cp}"
        txns.append({"id": f"TXN-A-{ym}-{i:03d}", "date": f"{ym}-{random.randint(1,days):02d}",
            "type": tx_type, "amount_rwf": amt, "counterparty": cp, "balance_after_rwf": max(balance,0), "description": desc})
    txns.sort(key=lambda t: t["date"])
    return {"subject_id": "PACIN_TEST_001", "month": ym, "transactions": txns,
        "summary": {"total_in": total_in, "total_out": total_out, "closing_balance": max(balance,0), "transaction_count": len(txns)}}, max(balance,0)

def _gen_momo_jp(month_idx, ym, prev_balance):
    txns = []
    balance = prev_balance
    total_in = total_out = 0
    days = _days_in_month(ym)
    if random.random() > 0.3:
        for _ in range(random.randint(1,3)):
            amt = random.randint(10000,45000); balance += amt; total_in += amt
            txns.append({"id": f"TXN-J-{ym}-IN-{_}", "date": f"{ym}-{random.randint(1,days):02d}", "type": "RECEIVE",
                "amount_rwf": amt, "counterparty": random.choice(_JP_CP_IN), "balance_after_rwf": max(balance,0), "description": "Incoming"})
    for i in range(random.randint(8,18)):
        tx_type = random.choice(["WITHDRAW","WITHDRAW","SEND","PAYMENT","AIRTIME"])
        if tx_type == "WITHDRAW": amt = random.randint(5000,30000); cp = "CASH WITHDRAWAL"; desc = "Cash out"
        elif tx_type == "AIRTIME": amt = random.choice([200,500,1000]); cp = "AIRTEL BUNDLES"; desc = "Airtime"
        else: amt = random.randint(1000,15000); cp = random.choice(_JP_CP_OUT); desc = f"Payment to {cp}"
        balance -= amt; total_out += amt
        txns.append({"id": f"TXN-J-{ym}-{i:03d}", "date": f"{ym}-{random.randint(1,days):02d}",
            "type": tx_type, "amount_rwf": amt, "counterparty": cp, "balance_after_rwf": max(balance,0), "description": desc})
    txns.sort(key=lambda t: t["date"])
    return {"subject_id": "PACIN_TEST_002", "month": ym, "transactions": txns,
        "summary": {"total_in": total_in, "total_out": total_out, "closing_balance": max(balance,0), "transaction_count": len(txns)}}, max(balance,0)

def generate_momo_data():
    alice, jp, a_bal, j_bal = [], [], 45000, 8000
    for idx, ym in enumerate(MONTHS):
        a_data, a_bal = _gen_momo_alice(idx, ym, a_bal); alice.append(a_data)
        j_data, j_bal = _gen_momo_jp(idx, ym, j_bal); jp.append(j_data)
    return {"PACIN_TEST_001": alice, "PACIN_TEST_002": jp}

def generate_bank_data():
    alice_stmts = []
    a_bal = 120000
    for ym in MONTHS:
        days = _days_in_month(ym); opening = a_bal; txns = []
        sal = random.randint(150000,165000); sal_day = min(28,days); a_bal += sal
        txns.append({"date": f"{ym}-{sal_day:02d}", "description": "SALARY CREDIT - KIGALI TECH LTD", "debit": 0, "credit": sal, "balance": a_bal, "type": "SALARY"})
        for util in ["RECO ELECTRIC","WASAC WATER"]:
            amt = random.randint(8000,15000); a_bal -= amt
            txns.append({"date": f"{ym}-{random.randint(5,15):02d}", "description": f"BILL PAYMENT - {util}", "debit": amt, "credit": 0, "balance": a_bal, "type": "UTILITY"})
        for _ in range(random.randint(3,6)):
            amt = random.randint(5000,25000); a_bal -= amt
            txns.append({"date": f"{ym}-{random.randint(1,days):02d}", "description": random.choice(["POS SIMBA MARKET","ATM WITHDRAWAL","TRANSFER OUT"]),
                "debit": amt, "credit": 0, "balance": a_bal, "type": random.choice(["POS","ATM","TRANSFER"])})
        txns.sort(key=lambda t: t["date"])
        alice_stmts.append({"month": ym, "opening_balance": opening, "closing_balance": a_bal, "transactions": txns})
    alice_loan_pmts = [{"month": ym, "paid": True, "days_late": 0} for ym in MONTHS[:18]]
    alice_bank = {"subject_id": "PACIN_TEST_001", "account_number": "****4521", "bank_name": "Bank of Kigali",
        "statements": alice_stmts, "loan_accounts": [{"loan_id": "BK-LN-2024-0891", "principal_rwf": 300000,
        "disbursed_date": "2024-09-01", "term_months": 18, "monthly_installment": 19500, "status": "CLOSED",
        "payment_history": alice_loan_pmts}]}
    jp_stmts = []
    j_bal = 25000
    late_months = {"2025-03", "2025-08", "2026-01"}
    for ym in MONTHS:
        days = _days_in_month(ym); opening = j_bal; txns = []
        if random.random() > 0.25:
            inc = random.randint(40000,80000); j_bal += inc
            txns.append({"date": f"{ym}-{random.randint(1,15):02d}", "description": "CASH DEPOSIT", "debit": 0, "credit": inc, "balance": j_bal, "type": "SALARY"})
        for _ in range(random.randint(2,5)):
            amt = random.randint(3000,20000); j_bal -= amt
            txns.append({"date": f"{ym}-{random.randint(1,days):02d}", "description": random.choice(["ATM WITHDRAWAL","POS MARKET","TRANSFER OUT"]),
                "debit": amt, "credit": 0, "balance": max(j_bal,0), "type": random.choice(["ATM","POS","TRANSFER"])})
        txns.sort(key=lambda t: t["date"])
        jp_stmts.append({"month": ym, "opening_balance": opening, "closing_balance": max(j_bal,0), "transactions": txns})
    jp_loan_pmts = [{"month": ym, "paid": ym not in late_months, "days_late": random.randint(15,45) if ym in late_months else 0} for ym in MONTHS]
    jp_bank = {"subject_id": "PACIN_TEST_002", "account_number": "****7731", "bank_name": "Equity BCDC",
        "statements": jp_stmts, "loan_accounts": [{"loan_id": "EQ-LN-2025-3341", "principal_rwf": 200000,
        "disbursed_date": "2025-01-15", "term_months": 24, "monthly_installment": 10200, "status": "ACTIVE",
        "payment_history": jp_loan_pmts}]}
    return {"PACIN_TEST_001": alice_bank, "PACIN_TEST_002": jp_bank}

def generate_utility_data():
    missed_months = {"2025-04", "2025-09", "2026-02"}
    alice_bills = []
    for ym in MONTHS:
        d = _days_in_month(ym)
        for provider, base in [("RECO",12000),("WASAC",5500)]:
            amt = base + random.randint(-1000,2000)
            due = f"{ym}-{min(20,d):02d}"; paid = f"{ym}-{random.randint(5,18):02d}"
            alice_bills.append({"month": ym, "amount_rwf": amt, "due_date": due, "paid_date": paid, "status": "PAID", "days_late": 0, "provider": provider})
    jp_bills = []
    for ym in MONTHS:
        d = _days_in_month(ym)
        amt = random.randint(8000,18000); due = f"{ym}-{min(20,d):02d}"
        if ym in missed_months:
            jp_bills.append({"month": ym, "amount_rwf": amt, "due_date": due, "paid_date": None, "status": "OVERDUE", "days_late": random.randint(30,90), "provider": "RECO"})
        else:
            late_days = random.randint(5,25) if random.random()>0.6 else 0
            paid_date = f"{ym}-{min(20+late_days,d):02d}" if late_days==0 else _random_date_in_month(ym)
            jp_bills.append({"month": ym, "amount_rwf": amt, "due_date": due, "paid_date": paid_date,
                "status": "PAID" if late_days==0 else "OVERDUE", "days_late": late_days, "provider": "RECO"})
    return {
        "PACIN_TEST_001": {"subject_id": "PACIN_TEST_001", "accounts": [{"provider": "RECO", "account_id": "RECO-001-A", "address": "KG 5 Ave, Gasabo",
            "bills": [b for b in alice_bills if b["provider"]=="RECO"]}, {"provider": "WASAC", "account_id": "WASAC-001-A",
            "address": "KG 5 Ave, Gasabo", "bills": [b for b in alice_bills if b["provider"]=="WASAC"]}]},
        "PACIN_TEST_002": {"subject_id": "PACIN_TEST_002", "accounts": [{"provider": "RECO", "account_id": "RECO-002-J",
            "address": "Musanze Town", "bills": jp_bills}]},
    }

def generate_insurance_data():
    alice_pmts = [{"period": f"Q{(MONTHS.index(ym)//3)+1}-{ym[:4]}", "paid": True, "paid_date": _random_date_in_month(ym)}
        for ym in MONTHS[::3]]
    alice_ins = {"subject_id": "PACIN_TEST_001", "policies": [{"policy_id": "RSSB-MUT-2024-55012",
        "provider": "RSSB", "type": "HEALTH", "status": "ACTIVE", "premium_rwf": 3000,
        "frequency": "QUARTERLY", "payment_history": alice_pmts}]}
    jp_ins = {"subject_id": "PACIN_TEST_002", "policies": []}
    return {"PACIN_TEST_001": alice_ins, "PACIN_TEST_002": jp_ins}

def generate_telecom_data():
    alice_months = [{"month": ym, "data_usage_mb": random.randint(1500,3500), "voice_minutes": random.randint(120,300),
        "sms_count": random.randint(30,80), "recharge_amount_rwf": random.randint(4000,8000),
        "recharge_count": random.randint(3,6), "sim_swap_events": 0, "roaming_days": random.choice([0,0,0,0,random.randint(1,5)])} for ym in MONTHS]
    alice_tel = {"subject_id": "PACIN_TEST_001", "operator": "MTN", "msisdn_hash": SUBJECT_PROFILES["PACIN_TEST_001"]["phone_hash"],
        "account_type": "PREPAID", "months": alice_months}
    sim_swap_months = {"2025-02","2025-07","2026-05"}
    jp_months = [{"month": ym, "data_usage_mb": random.randint(200,1200) if random.random()>0.2 else random.randint(0,50),
        "voice_minutes": random.randint(10,80) if random.random()>0.2 else 0, "sms_count": random.randint(5,30) if random.random()>0.2 else 0,
        "recharge_amount_rwf": random.randint(500,3000) if random.random()>0.2 else 0, "recharge_count": random.randint(0,3) if random.random()>0.2 else 0,
        "sim_swap_events": 1 if ym in sim_swap_months else 0, "roaming_days": 0} for ym in MONTHS]
    jp_tel = {"subject_id": "PACIN_TEST_002", "operator": "AIRTEL", "msisdn_hash": SUBJECT_PROFILES["PACIN_TEST_002"]["phone_hash"],
        "account_type": "PREPAID", "months": jp_months}
    return {"PACIN_TEST_001": alice_tel, "PACIN_TEST_002": jp_tel}

MOMO_DATA = generate_momo_data()
BANK_DATA = generate_bank_data()
UTILITY_DATA = generate_utility_data()
INSURANCE_DATA = generate_insurance_data()
TELECOM_DATA = generate_telecom_data()
DATA_STORES = {"momo": MOMO_DATA, "bank": BANK_DATA, "utility": UTILITY_DATA, "insurance": INSURANCE_DATA, "telecom": TELECOM_DATA}
VALID_SUBJECTS = list(SUBJECT_PROFILES.keys())
