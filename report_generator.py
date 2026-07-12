"""
==========================================================
Orynt Technology - مولّد التقرير الائتماني بالذكاء الاصطناعي
==========================================================
هذا الملف يأخذ نتيجة التحليل المالي (من risk_engine.py)
ويرسلها لـ Claude API ليكتب تقرير ائتماني احترافي بالعربي،
جاهز لمراجعة موظف التمويل، مع شرح واضح لأسباب القرار.
==========================================================
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# تحميل مفتاح API من ملف .env بطريقة آمنة
load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def build_report_prompt(analysis):
    """
    يبني التعليمات (Prompt) التي سترسل لـ Claude، وتحتوي
    على كل بيانات التحليل المالي بشكل منظم.
    """
    ratios = analysis["financial_ratios"]
    risk = analysis["risk_assessment"]
    financing = analysis["financing_recommendation"]

    reasons_text = "\n".join([
        f"- {r['factor']}: {r['value']} ({r['impact']}) - {r['explanation']}"
        for r in risk["reasons"]
    ])

    prompt = f"""أنت محلل ائتماني خبير في بنك سعودي يعمل وفق معايير ساما (SAMA)
والتمويل الإسلامي. اكتب تقريرًا ائتمانيًا احترافيًا بالعربية الفصحى
لموظف التمويل، بناءً على البيانات التالية فقط (لا تخترع أي معلومة
غير موجودة هنا):

اسم العميل: {analysis['customer_name']}

النسب المالية:
- متوسط الدخل الشهري: {ratios['avg_monthly_income']} ريال
- متوسط الالتزامات الشهرية: {ratios['avg_monthly_obligations']} ريال
- نسبة الالتزامات إلى الدخل: {ratios['debt_to_income_ratio']}%
- معدل الادخار: {ratios['savings_rate']}%
- الرصيد الحالي: {ratios['current_balance']} ريال

تقييم المخاطر:
- درجة المخاطر: {risk['risk_score']}/100 ({risk['risk_level']})
- الأسباب التفصيلية:
{reasons_text}

التوصية:
- المنتج المقترح: {financing['recommended_product']}
- درجة الثقة: {financing['confidence']}
- التبرير: {financing['reasoning']}

اكتب التقرير بالتنسيق التالي بالضبط:

## ملخص تنفيذي
(فقرة واحدة قصيرة تلخص الوضع والتوصية)

## تحليل الوضع المالي
(فقرتان تشرحان النسب المالية وما تعنيه عمليًا)

## تقييم المخاطر
(فقرة تشرح درجة المخاطر وأهم الأسباب بلغة واضحة لغير المتخصص)

## التوصية النهائية
(فقرة تشرح لماذا هذا المنتج التمويلي بالذات هو الأنسب)

اجعل الأسلوب مهنيًا، دقيقًا، وموجزًا (لا يتجاوز التقرير الكامل 300 كلمة)."""

    return prompt


def generate_ai_report(analysis):
    """
    يرسل الطلب فعليًا لـ Claude API ويرجع نص التقرير المولّد.
    """
    prompt = build_report_prompt(analysis)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    report_text = message.content[0].text
    return report_text


if __name__ == "__main__":
    risk_profiles = ["good", "average", "risky"]

    for profile in risk_profiles:
        filename = f"analysis_{profile}.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                analysis = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  الملف {filename} غير موجود - شغّلي risk_engine.py أولاً")
            continue

        print("=" * 60)
        print(f"جاري توليد التقرير لعميل: {analysis['customer_name']} ...")
        print("=" * 60)

        report = generate_ai_report(analysis)
        print(report)
        print()

        # حفظ التقرير كملف نصي منفصل
        output_filename = f"report_{profile}.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ تم حفظ التقرير في: {output_filename}\n")