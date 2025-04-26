from flask import Flask, request, render_template
import pandas as pd
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("excel_file")
        if not file or not file.filename.endswith((".xls", ".xlsx")):
            return "الرجاء رفع ملف Excel صالح", 400

        df = pd.read_excel(file)

        # إعادة تسمية الأعمدة من ملفك إلى الأعمدة التي يتوقعها السكربت
        df.rename(columns={
            "Item Code": "code",
            "Item Alias": "alias",
            "Item Name": "name",
            "PRICE": "price",
            "Current Stock": "stock",
            "Outlet Name": "outlet",
            "Category": "category"
        }, inplace=True)

        required_cols = ["code", "alias", "name", "price", "stock", "outlet", "category"]
        if not all(col in df.columns for col in required_cols):
            return f"🛑 الملف لا يحتوي على كل الأعمدة المطلوبة: {', '.join(required_cols)}", 400

        df = df[df["stock"] > 0].fillna("")
        products = df.to_dict(orient="records")

        js_path = os.path.join(app.static_folder, "products.js")
        with open(js_path, "w", encoding="utf-8") as f:
            f.write("const data = " + json.dumps(products, ensure_ascii=False) + ";")

        return "✅ تم تحديث البيانات بنجاح!"
    
    except Exception as e:
        return f"❌ خطأ أثناء رفع الملف: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
