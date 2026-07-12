"""
==========================================================
Orynt Technology - محاكي السيناريوهات (What-if Analysis)
==========================================================
هذا الملف يتيح لموظف التمويل تجربة سيناريوهات افتراضية:
"ماذا لو زاد دخل العميل؟" أو "ماذا لو قلّت التزاماته؟"
ويعيد حساب درجة المخاطر الجديدة، مع مقارنة واضحة
بين الوضع الحالي والوضع الافتراضي.
==========================================================
"""

import json
from risk_engine import calculate_risk_score, recommend_islamic_financing


def apply_scenario(original_ratios, income_change=0, obligations_change=0, balance_change=0):
    """
    يطبّق تعديلات افتراضية على النسب المالية الأصلية.
    """
    new_ratios = original_ratios.copy()

    new_income = max(original_ratios["avg_monthly_income"] + income_change, 1)
    new_obligations = max(original_ratios["avg_monthly_obligations"] + obligations_change, 0)
    new_balance = original_ratios["current_balance"] + balance_change

    new_dti = round((new_obligations / new_income) * 100, 2)

    new_ratios["avg_monthly_income"] = round(new_income, 2)
    new_ratios["avg_monthly_obligations"] = round(new_obligations, 2)
    new_ratios["debt_to_income_ratio"] = new_dti
    new_ratios["current_balance"] = round(new_balance, 2)

    return new_ratios


def run_what_if_scenario(original_analysis, scenario_name, income_change=0,
                           obligations_change=0, balance_change=0):
    """
    يشغّل سيناريو افتراضي كامل ويرجع مقارنة شاملة.
    """
    original_ratios = original_analysis["financial_ratios"]
    original_risk = original_analysis["risk_assessment"]

    new_ratios = apply_scenario(original_ratios, income_change, obligations_change, balance_change)
    new_risk = calculate_risk_score(new_ratios)
    new_financing = recommend_islamic_financing(new_risk, new_ratios)

    score_difference = round(new_risk["risk_score"] - original_risk["risk_score"], 1)

    if score_difference < 0:
        impact_summary = f"تحسّن الوضع: انخفضت درجة المخاطر بمقدار {abs(score_difference)} نقطة"
    elif score_difference > 0:
        impact_summary = f"تراجع الوضع: ارتفعت درجة المخاطر بمقدار {score_difference} نقطة"
    else:
        impact_summary = "لا يوجد تغيير جوهري في درجة المخاطر"

    return {
        "scenario_name": scenario_name,
        "applied_changes": {
            "income_change": income_change,
            "obligations_change": obligations_change,
            "balance_change": balance_change
        },
        "before": {
            "risk_score": original_risk["risk_score"],
            "risk_level": original_risk["risk_level"],
            "debt_to_income_ratio": original_ratios["debt_to_income_ratio"],
            "recommended_product": original_analysis["financing_recommendation"]["recommended_product"]
        },
        "after": {
            "risk_score": new_risk["risk_score"],
            "risk_level": new_risk["risk_level"],
            "debt_to_income_ratio": new_ratios["debt_to_income_ratio"],
            "recommended_product": new_financing["recommended_product"]
        },
        "impact_summary": impact_summary,
        "score_difference": score_difference
    }


if __name__ == "__main__":
    filename = "analysis_average.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            analysis = json.load(f)
    except FileNotFoundError:
        print(f"⚠️  الملف {filename} غير موجود - شغّلي risk_engine.py أولاً")
        exit()

    print("=" * 60)
    print(f"العميل: {analysis['customer_name']}")
    print(f"الوضع الحالي: درجة المخاطر {analysis['risk_assessment']['risk_score']}/100 "
          f"({analysis['risk_assessment']['risk_level']})")
    print("=" * 60)

    scenario_1 = run_what_if_scenario(
        analysis,
        scenario_name="زيادة الدخل الشهري بمقدار 2000 ريال",
        income_change=2000
    )

    scenario_2 = run_what_if_scenario(
        analysis,
        scenario_name="تقليل الالتزامات الشهرية بمقدار 1000 ريال",
        obligations_change=-1000
    )

    scenario_3 = run_what_if_scenario(
        analysis,
        scenario_name="سيناريو شامل: زيادة دخل + تقليل التزامات + تحسين رصيد",
        income_change=1500,
        obligations_change=-800,
        balance_change=3000
    )

    all_scenarios = [scenario_1, scenario_2, scenario_3]

    for scenario in all_scenarios:
        print(f"\n📊 السيناريو: {scenario['scenario_name']}")
        print(f"   قبل: {scenario['before']['risk_score']}/100 ({scenario['before']['risk_level']}) "
              f"- {scenario['before']['recommended_product']}")
        print(f"   بعد: {scenario['after']['risk_score']}/100 ({scenario['after']['risk_level']}) "
              f"- {scenario['after']['recommended_product']}")
        print(f"   {scenario['impact_summary']}")

    output = {
        "customer_name": analysis["customer_name"],
        "scenarios": all_scenarios
    }

    with open("what_if_scenarios.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ تم حفظ جميع السيناريوهات في: what_if_scenarios.json")