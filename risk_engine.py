"""
Orynt Technology - محرك التحليل المالي وتقييم المخاطر
"""

import json
from datetime import datetime


def calculate_financial_ratios(account_data):
    transactions = account_data["transactions"]
    balance = account_data["balance"]["current_balance"]
    months = account_data["summary"]["period_months"]

    salary_transactions = [t for t in transactions if t["category"] == "راتب"]
    avg_monthly_income = (
        sum(t["amount"] for t in salary_transactions) / len(salary_transactions)
        if salary_transactions else 0
    )

    fixed_categories = ["إيجار سكن", "تمويل / قسط بنكي", "فواتير كهرباء وماء", "اتصالات وإنترنت"]
    fixed_obligations = [t for t in transactions if t["category"] in fixed_categories]
    avg_monthly_obligations = (
        sum(t["amount"] for t in fixed_obligations) / months if months else 0
    )

    dti_ratio = (avg_monthly_obligations / avg_monthly_income * 100) if avg_monthly_income else 100

    total_credit = account_data["summary"]["total_credit"]
    total_debit = account_data["summary"]["total_debit"]
    savings_rate = ((total_credit - total_debit) / total_credit * 100) if total_credit else 0

    cash_withdrawals = [t for t in transactions if t["category"] == "سحب نقدي ATM"]
    cash_withdrawal_frequency = len(cash_withdrawals) / months if months else 0

    bank_fees = [t for t in transactions if t["category"] == "رسوم بنكية"]
    bank_fees_count = len(bank_fees)

    if len(salary_transactions) >= 2:
        salary_amounts = [t["amount"] for t in salary_transactions]
        income_variance = (max(salary_amounts) - min(salary_amounts)) / avg_monthly_income * 100
    else:
        income_variance = 0

    return {
        "avg_monthly_income": round(avg_monthly_income, 2),
        "avg_monthly_obligations": round(avg_monthly_obligations, 2),
        "debt_to_income_ratio": round(dti_ratio, 2),
        "savings_rate": round(savings_rate, 2),
        "current_balance": balance,
        "cash_withdrawal_frequency_per_month": round(cash_withdrawal_frequency, 2),
        "bank_fees_count": bank_fees_count,
        "income_variance_pct": round(income_variance, 2),
    }


def calculate_risk_score(ratios):
    score = 0
    reasons = []

    dti = ratios["debt_to_income_ratio"]
    if dti >= 100:
        dti_points = 35
    elif dti <= 15:
        dti_points = 0
    else:
        dti_points = round(((dti - 15) / (100 - 15)) * 35, 1)
    score += dti_points

    if dti > 60:
        impact = "سلبي مرتفع"
        explanation = f"الالتزامات الشهرية تلتهم {dti}% من الدخل، وهذا يتجاوز الحد الآمن المعتمد بنكيًا (40%)، مما يعني هامش سداد ضيق جدًا"
    elif dti > 40:
        impact = "سلبي متوسط"
        explanation = f"نسبة الالتزامات {dti}% قريبة من الحد الأعلى المقبول (40%)، تستدعي حذرًا عند منح تمويل إضافي"
    elif dti > 25:
        impact = "مقبول"
        explanation = f"نسبة الالتزامات {dti}% ضمن النطاق المقبول، تعكس التزامات معتدلة"
    else:
        impact = "إيجابي"
        explanation = f"نسبة الالتزامات منخفضة ({dti}%)، مما يعكس هامش سداد مريح وقدرة استيعاب تمويل إضافي"

    reasons.append({
        "factor": "نسبة الالتزامات إلى الدخل",
        "value": f"{dti}%",
        "impact": impact,
        "points": dti_points,
        "explanation": explanation
    })

    balance = ratios["current_balance"]
    if balance <= -5000:
        balance_points = 20
    elif balance >= 10000:
        balance_points = 0
    else:
        balance_points = round(((10000 - balance) / (10000 - (-5000))) * 20, 1)
        balance_points = max(0, min(balance_points, 20))
    score += balance_points

    if balance < 0:
        impact = "سلبي مرتفع"
        explanation = "الحساب في وضع سالب (على المكشوف)، وهذا مؤشر خطر مباشر على إدارة السيولة"
    elif balance < 2000:
        impact = "سلبي منخفض"
        explanation = "الرصيد منخفض نسبيًا، مما يقلل هامش الأمان المالي لدى العميل"
    else:
        impact = "إيجابي"
        explanation = "الرصيد الحالي يعكس وضعًا ماليًا مستقرًا وهامش أمان جيد"

    reasons.append({
        "factor": "الرصيد الحالي",
        "value": f"{balance} ريال",
        "impact": impact,
        "points": round(balance_points, 1),
        "explanation": explanation
    })

    savings = ratios["savings_rate"]
    if savings <= -20:
        savings_points = 20
    elif savings >= 25:
        savings_points = 0
    else:
        savings_points = round(((25 - savings) / (25 - (-20))) * 20, 1)
        savings_points = max(0, min(savings_points, 20))
    score += savings_points

    if savings < 0:
        impact = "سلبي مرتفع"
        explanation = "العميل ينفق أكثر مما يدخل شهريًا، وهذا نمط غير مستدام ماليًا"
    elif savings < 10:
        impact = "سلبي منخفض"
        explanation = "معدل الادخار ضعيف، مما يشير لهامش مالي محدود لمواجهة الطوارئ"
    else:
        impact = "إيجابي"
        explanation = "معدل ادخار صحي يعكس انضباطًا ماليًا جيدًا"

    reasons.append({
        "factor": "معدل الادخار",
        "value": f"{savings}%",
        "impact": impact,
        "points": round(savings_points, 1),
        "explanation": explanation
    })

    cash_freq = ratios["cash_withdrawal_frequency_per_month"]
    if cash_freq >= 6:
        cash_points = 15
    elif cash_freq <= 1:
        cash_points = 0
    else:
        cash_points = round(((cash_freq - 1) / (6 - 1)) * 15, 1)
    score += cash_points

    if cash_freq > 3:
        impact = "سلبي متوسط"
        explanation = "معدل سحب نقدي مرتفع قد يشير لصعوبة تتبع الإنفاق أو اعتماد على السيولة النقدية خارج الرقابة المصرفية"
    else:
        impact = "طبيعي"
        explanation = "نمط سحب نقدي طبيعي ولا يثير قلقًا"

    reasons.append({
        "factor": "تكرار السحب النقدي",
        "value": f"{cash_freq} مرة/شهريًا",
        "impact": impact,
        "points": round(cash_points, 1),
        "explanation": explanation
    })

    fees = ratios["bank_fees_count"]
    if fees >= 8:
        fees_points = 10
    elif fees <= 1:
        fees_points = 0
    else:
        fees_points = round(((fees - 1) / (8 - 1)) * 10, 1)
    score += fees_points

    if fees > 3:
        impact = "سلبي متوسط"
        explanation = "تكرار الرسوم البنكية مؤشر شائع على تجاوز السقف الائتماني أو تأخر السداد"
    else:
        impact = "طبيعي"
        explanation = "لا توجد رسوم بنكية ملحوظة، مؤشر إيجابي على الانضباط"

    reasons.append({
        "factor": "الرسوم البنكية المتكررة",
        "value": f"{fees} رسوم خلال الفترة",
        "impact": impact,
        "points": round(fees_points, 1),
        "explanation": explanation
    })

    score = round(min(score, 100), 1)

    if score >= 60:
        risk_level = "مرتفع"
    elif score >= 30:
        risk_level = "متوسط"
    else:
        risk_level = "منخفض"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons
    }


def recommend_islamic_financing(risk_result, ratios):
    score = risk_result["risk_score"]
    level = risk_result["risk_level"]

    if level == "منخفض":
        return {
            "recommended_product": "إجارة منتهية بالتمليك",
            "confidence": "عالية",
            "max_suggested_amount_multiplier": 4,
            "reasoning": (
                "الوضع المالي للعميل مستقر جدًا (درجة مخاطر منخفضة "
                f"{score}/100)، مع دخل منتظم ونسبة التزامات صحية. "
                "هذا يؤهله لتمويل طويل الأجل مثل الإجارة المنتهية بالتمليك "
                "لتملك أصل (سيارة أو عقار) بمخاطر منخفضة على البنك."
            ),
            "alternative_products": ["مرابحة"]
        }
    elif level == "متوسط":
        return {
            "recommended_product": "مرابحة",
            "confidence": "متوسطة",
            "max_suggested_amount_multiplier": 2.5,
            "reasoning": (
                f"العميل يحمل مخاطر متوسطة (درجة {score}/100)، ما يجعل "
                "المرابحة الخيار الأنسب لأنها ترتبط بسلعة محددة (مثل سيارة "
                "أو أثاث)، وتتيح للبنك ربطًا مباشرًا بين التمويل والأصل "
                "المُموَّل، ما يقلل المخاطر مقارنة بتمويل نقدي غير مربوط."
            ),
            "alternative_products": ["تورّق بمبلغ محدود"]
        }
    else:
        return {
            "recommended_product": "قرض حسن (بمبلغ محدود)",
            "confidence": "منخفضة - يتطلب مراجعة يدوية",
            "max_suggested_amount_multiplier": 0.5,
            "reasoning": (
                f"درجة المخاطر مرتفعة ({score}/100) بسبب مؤشرات ضغط مالي "
                "واضحة (التزامات مرتفعة و/أو رصيد سالب و/أو سلوك سحب نقدي "
                "متكرر). لا يُنصح بمنح تمويل تجاري تقليدي حاليًا. "
                "قرض حسن بمبلغ محدود ولفترة قصيرة قد يكون خيارًا مسؤولًا "
                "لمساعدة العميل دون تحميله أعباء إضافية، مع ضرورة إعادة "
                "التقييم بعد تحسّن المؤشرات."
            ),
            "alternative_products": ["رفض مؤقت مع خطة تحسين مالي مقترحة"]
        }


def full_credit_analysis(account_data):
    ratios = calculate_financial_ratios(account_data)
    risk_result = calculate_risk_score(ratios)
    financing = recommend_islamic_financing(risk_result, ratios)

    return {
        "customer_name": account_data["account_info"]["customer_name"],
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "financial_ratios": ratios,
        "risk_assessment": risk_result,
        "financing_recommendation": financing
    }


if __name__ == "__main__":
    risk_profiles = ["good", "average", "risky"]

    for profile in risk_profiles:
        filename = f"sample_data_{profile}.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                account_data = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  الملف {filename} غير موجود - شغّلي hsimu.py أولاً")
            continue

        result = full_credit_analysis(account_data)

        print("=" * 60)
        print(f"العميل: {result['customer_name']}")
        print(f"درجة المخاطر: {result['risk_assessment']['risk_score']}/100 "
              f"({result['risk_assessment']['risk_level']})")
        print(f"التمويل المقترح: {result['financing_recommendation']['recommended_product']}")
        print("-" * 60)
        print("أسباب التقييم:")
        for reason in result["risk_assessment"]["reasons"]:
            if reason["points"] > 0:
                print(f"  • {reason['factor']}: {reason['value']} "
                      f"({reason['impact']}, +{reason['points']} نقطة)")
        print()

        output_filename = f"analysis_{profile}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ تم حفظ التحليل الكامل في: {output_filename}\n")