"""
==========================================================
Orynt Technology - Open Banking Simulator
==========================================================
هذا الملف يحاكي البيانات التي يرجعها بنك حقيقي عبر
Open Banking API (بنفس بنية البيانات المعتمدة في السعودية
ضمن إطار SAMA Open Banking Framework).

الهدف: توليد بيانات واقعية لعميل بنكي (حساب، رصيد، معاملات)
لنستخدمها لاحقًا في التحليل المالي والذكاء الاصطناعي،
دون الحاجة لاتصال حقيقي ببنك خلال فترة الهاكاثون.

عند التطبيق الفعلي مستقبلاً، هذا الملف بالذات هو الوحيد
الذي يُستبدل بطبقة اتصال حقيقية بـ API البنك -
باقي النظام (التحليل، الذكاء الاصطناعي، التقارير) لن يتغير.
==========================================================
"""

import json
import random
from datetime import datetime, timedelta


# ----------------------------------------------------------
# الخطوة 1: قوائم بيانات واقعية نستخدمها لتوليد معاملات منطقية
# ----------------------------------------------------------

# فئات المعاملات (Transaction Categories) - نفس التصنيفات
# التي تستخدمها البنوك السعودية فعليًا في كشوف الحسابات
MERCHANT_CATEGORIES = {
    "راتب": {"type": "credit", "range": (8000, 25000), "frequency": "monthly"},
    "تحويل من فرد": {"type": "credit", "range": (200, 5000), "frequency": "random"},
    "سوبرماركت": {"type": "debit", "range": (50, 600), "frequency": "frequent"},
    "مطاعم وكافيهات": {"type": "debit", "range": (20, 250), "frequency": "frequent"},
    "فواتير كهرباء وماء": {"type": "debit", "range": (150, 800), "frequency": "monthly"},
    "اتصالات وإنترنت": {"type": "debit", "range": (100, 400), "frequency": "monthly"},
    "إيجار سكن": {"type": "debit", "range": (2000, 6000), "frequency": "monthly"},
    "تمويل / قسط بنكي": {"type": "debit", "range": (1000, 4000), "frequency": "monthly"},
    "تسوق أونلاين": {"type": "debit", "range": (100, 1500), "frequency": "random"},
    "وقود ومواصلات": {"type": "debit", "range": (100, 350), "frequency": "frequent"},
    "سحب نقدي ATM": {"type": "debit", "range": (200, 2000), "frequency": "random"},
    "رسوم بنكية": {"type": "debit", "range": (15, 100), "frequency": "random"},
}


def generate_transactions(months_back: int = 6, monthly_salary: int = 12000,
                            risk_profile: str = "good") -> list:
    """
    توليد قائمة معاملات بنكية واقعية لعدد أشهر محددة.

    risk_profile يتحكم في نمط السلوك المالي للعميل:
    - "good"    : عميل منضبط ماليًا (دخل ثابت، مصاريف متوازنة)
    - "risky"   : عميل عليه مؤشرات خطر (سحوبات نقدية كثيرة، تذبذب دخل)
    - "average" : عميل متوسط الانضباط
    """
    transactions = []
    today = datetime.now()

    for month_offset in range(months_back):
        month_date = today - timedelta(days=30 * month_offset)

        # 1. الراتب الشهري (معاملة ثابتة كل شهر)
        salary_variance = 0 if risk_profile == "good" else random.randint(-2000, 500)
        transactions.append({
            "date": (month_date.replace(day=25)).strftime("%Y-%m-%d"),
            "description": "راتب - تحويل جهة العمل",
            "category": "راتب",
            "amount": monthly_salary + salary_variance,
            "type": "credit"
        })

        # 2. الفواتير الثابتة الشهرية (إيجار، كهرباء، اتصالات، تمويل)
        fixed_bills = ["إيجار سكن", "فواتير كهرباء وماء", "اتصالات وإنترنت"]
        if risk_profile in ["average", "risky"]:
            fixed_bills.append("تمويل / قسط بنكي")

        for bill in fixed_bills:
            low, high = MERCHANT_CATEGORIES[bill]["range"]
            transactions.append({
                "date": (month_date.replace(day=random.randint(1, 5))).strftime("%Y-%m-%d"),
                "description": bill,
                "category": bill,
                "amount": round(random.uniform(low, high), 2),
                "type": "debit"
            })

        # 3. معاملات يومية متكررة (سوبرماركت، مطاعم، وقود)
        frequent_categories = ["سوبرماركت", "مطاعم وكافيهات", "وقود ومواصلات"]
        num_frequent = 15 if risk_profile != "risky" else 25

        for _ in range(num_frequent):
            cat = random.choice(frequent_categories)
            low, high = MERCHANT_CATEGORIES[cat]["range"]
            transactions.append({
                "date": (month_date - timedelta(days=random.randint(0, 28))).strftime("%Y-%m-%d"),
                "description": cat,
                "category": cat,
                "amount": round(random.uniform(low, high), 2),
                "type": "debit"
            })

        # 4. معاملات عشوائية (تسوق، تحويلات، سحوبات)
        random_categories = ["تسوق أونلاين", "تحويل من فرد", "سحب نقدي ATM"]
        num_random = 4 if risk_profile == "good" else 10

        for _ in range(num_random):
            cat = random.choice(random_categories)
            info = MERCHANT_CATEGORIES[cat]
            low, high = info["range"]
            transactions.append({
                "date": (month_date - timedelta(days=random.randint(0, 28))).strftime("%Y-%m-%d"),
                "description": cat,
                "category": cat,
                "amount": round(random.uniform(low, high), 2),
                "type": info["type"]
            })

        # 5. مؤشر خطر إضافي: رسوم بنكية متكررة لعميل "risky"
        # (غالبًا ناتجة عن تجاوز رصيد أو دفعات متأخرة)
        if risk_profile == "risky":
            for _ in range(random.randint(1, 3)):
                transactions.append({
                    "date": (month_date - timedelta(days=random.randint(0, 28))).strftime("%Y-%m-%d"),
                    "description": "رسوم بنكية",
                    "category": "رسوم بنكية",
                    "amount": round(random.uniform(15, 100), 2),
                    "type": "debit"
                })

    # ترتيب المعاملات من الأحدث للأقدم (كما تظهر في أي تطبيق بنكي)
    transactions.sort(key=lambda t: t["date"], reverse=True)
    return transactions


def generate_account_profile(customer_name: str = "عميل تجريبي",
                               monthly_salary: int = 12000,
                               risk_profile: str = "good",
                               months_back: int = 6) -> dict:
    """
    توليد ملف حساب بنكي متكامل بصيغة تحاكي استجابة
    Open Banking API الحقيقية (تحتوي على معلومات الحساب
    + الرصيد + قائمة المعاملات).

    هذا الشكل (account_info / balance / transactions) هو نفس
    البنية المعتمدة في معايير Open Banking العالمية (Berlin Group)
    والتي تبنت عليها السعودية إطارها الخاص عبر ساما.
    """
    transactions = generate_transactions(months_back, monthly_salary, risk_profile)

    total_credit = sum(t["amount"] for t in transactions if t["type"] == "credit")
    total_debit = sum(t["amount"] for t in transactions if t["type"] == "debit")
    current_balance = round(total_credit - total_debit + 5000, 2)  # 5000 رصيد افتراضي بداية الفترة

    account_data = {
        "meta": {
            "source": "Orynt Open Banking Simulator",
            "standard": "Simulated SAMA Open Banking Framework",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "بيانات محاكاة لأغراض العرض التجريبي - قابلة للاستبدال بـ API بنكي حقيقي دون تعديل باقي النظام"
        },
        "account_info": {
            "customer_name": customer_name,
            "bank_name": "البنك التجريبي (Simulated Bank)",
            "account_number_masked": "SA** ** ** " + str(random.randint(1000, 9999)),
            "account_type": "حساب جاري",
            "currency": "SAR",
            "consent_status": "approved",
            "consent_scope": ["balance", "transactions_6_months", "account_info"]
        },
        "balance": {
            "current_balance": current_balance,
            "available_balance": round(current_balance * 0.95, 2),
            "as_of": datetime.now().strftime("%Y-%m-%d")
        },
        "transactions": transactions,
        "summary": {
            "total_transactions": len(transactions),
            "total_credit": round(total_credit, 2),
            "total_debit": round(total_debit, 2),
            "period_months": months_back
        }
    }

    return account_data


# ----------------------------------------------------------
# تشغيل تجريبي: توليد 3 نماذج عملاء مختلفة (جيد / متوسط / خطر)
# ----------------------------------------------------------

if _name_ == "_main_":
    profiles = [
        {"name": "سارة العتيبي", "salary": 14000, "risk": "good"},
        {"name": "محمد القحطاني", "salary": 9500, "risk": "average"},
        {"name": "خالد الشمري", "salary": 8000, "risk": "risky"},
    ]

    for p in profiles:
        data = generate_account_profile(
            customer_name=p["name"],
            monthly_salary=p["salary"],
            risk_profile=p["risk"]
        )

        filename = f"sample_data_{p['risk']}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ تم توليد بيانات العميل: {p['name']} ({p['risk']}) -> {filename}")
        print(f"   الرصيد الحالي: {data['balance']['current_balance']} ريال")
        print(f"   عدد المعاملات: {data['summary']['total_transactions']}")
        print("-" * 50)