"""
==========================================================
Orynt Technology - مؤشر احتمالية التعثر واقتراحات التحسين
==========================================================
"""

import json
import math
from risk_engine import calculate_risk_score, recommend_islamic_financing
from what_if_analysis import run_what_if_scenario


def calculate_default_probability(risk_score):
    """
    يحوّل درجة المخاطر (0-100) إلى احتمالية تعثر مئوية،
    باستخدام دالة لوجستية (S-curve) تجعل الخطر يتسارع
    بشكل واقعي كلما اقتربت الدرجة من الحدود الحرجة.
    """
    k = 0.08
    midpoint = 50
    probability = 1 / (1 + math.exp(-k * (risk_score - midpoint)))
    probability_pct = round(probability * 100, 1)

    if probability_pct >= 65:
        category = "احتمالية تعثر مرتفعة"
        color_code = "أحمر"
    elif probability_pct >= 35:
        category = "احتمالية تعثر متوسطة"
        color_code = "أصفر"
    else:
        category = "احتمالية تعثر منخفضة"
        color_code = "أخضر"

    return {
        "default_probability_pct": probability_pct,
        "category": category,
        "color_code": color_code
    }


def identify_weakest_factors(risk_reasons, top_n=2):
    negative_factors = [r for r in risk_reasons if r["points"] > 0]
    sorted_factors = sorted(negative_factors, key=lambda r: r["points"], reverse=True)
    return sorted_factors[:top_n]


def generate_improvement_suggestions(analysis):
    weakest_factors = identify_weakest_factors(analysis["risk_assessment"]["reasons"])
    suggestions = []

    factor_strategies = {
        "نسبة الالتزامات إلى الدخل": {
            "action": "تقليل الالتزامات الشهرية أو زيادة مصادر الدخل",
            "scenario_params": {"obligations_change": -1000}
        },
        "الرصيد الحالي": {
            "action": "بناء رصيد احتياطي وتجنب السحب على المكشوف",
            "scenario_params": {"balance_change": 3000}
        },
        "معدل الادخار": {
            "action": "تخصيص نسبة ثابتة من الدخل للادخار الشهري",
            "scenario_params": {"balance_change": 2000}
        },
        "تكرار السحب النقدي": {
            "action": "الاعتماد على المدفوعات الإلكترونية بدل السحب النقدي المتكرر",
            "scenario_params": {}
        },
        "الرسوم البنكية المتكررة": {
            "action": "ضبط موعد السداد لتجنب رسوم التأخير والتجاوز",
            "scenario_params": {"balance_change": 1000}
        }
    }

    for factor in weakest_factors:
        factor_name = factor["factor"]
        strategy = factor_strategies.get(factor_name)

        if not strategy:
            continue

        suggestion = {
            "weak_point": factor_name,
            "current_value": factor["value"],
            "why_it_matters": factor["explanation"],
            "recommended_action": strategy["action"]
        }

        if strategy["scenario_params"]:
            scenario_result = run_what_if_scenario(
                analysis,
                scenario_name=f"تحسين: {factor_name}",
                **strategy["scenario_params"]
            )
            suggestion["expected_impact"] = scenario_result["impact_summary"]
            suggestion["new_risk_level"] = scenario_result["after"]["risk_level"]

        suggestions.append(suggestion)

    return suggestions


def full_predictive_analysis(analysis):
    risk_score = analysis["risk_assessment"]["risk_score"]
    default_prediction = calculate_default_probability(risk_score)
    improvement_suggestions = generate_improvement_suggestions(analysis)

    return {
        "customer_name": analysis["customer_name"],
        "current_risk_score": risk_score,
        "default_prediction": default_prediction,
        "improvement_suggestions": improvement_suggestions
    }


if __name__ == "__main__":
    risk_profiles = ["good", "average", "risky"]

    for profile in risk_profiles:
        filename = f"analysis_{profile}.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                analysis = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  الملف {filename} غير موجود")
            continue

        result = full_predictive_analysis(analysis)

        print("=" * 60)
        print(f"العميل: {result['customer_name']}")
        print(f"درجة المخاطر الحالية: {result['current_risk_score']}/100")
        print(f"احتمالية التعثر: {result['default_prediction']['default_probability_pct']}% "
              f"({result['default_prediction']['category']})")
        print("-" * 60)

        if result["improvement_suggestions"]:
            print("اقتراحات التحسين:")
            for i, sug in enumerate(result["improvement_suggestions"], 1):
                print(f"\n{i}. نقطة الضعف: {sug['weak_point']} ({sug['current_value']})")
                print(f"   الإجراء المقترح: {sug['recommended_action']}")
                if "expected_impact" in sug:
                    print(f"   الأثر المتوقع: {sug['expected_impact']}")
        else:
            print("لا توجد نقاط ضعف جوهرية - الملف المالي للعميل مستقر.")

        print()

        output_filename = f"predictive_{profile}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ تم حفظ التحليل التنبؤي في: {output_filename}\n")