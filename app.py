from flask import Flask, render_template, request
#import pdfplumber
import pandas as pd
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- Helper Functions ---------------- #

def extract_email(text):
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return emails[0] if emails else "Not Found"


def extract_phone(text):
    phones = re.findall(r'\+?\d[\d\s\-]{8,15}', text)
    return phones[0] if phones else "Not Found"


def detect_document_type(text):

    text = text.lower()

    if "skills" in text and "education" in text:
        return "Resume"

    elif "invoice" in text:
        return "Invoice"

    elif "research" in text or "abstract" in text:
        return "Research Paper"

    elif "student" in text or "marks" in text:
        return "Student Report"

    return "General Document"


def generate_summary(text):

    if not text:
        return "No text found."

    text = text.replace("\n", " ")

    sentences = text.split(".")

    summary = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) > 20:
            summary.append(sentence)

        if len(summary) >= 5:
            break

    return ". ".join(summary)


# ---------------- Route ---------------- #

@app.route("/", methods=["GET", "POST"])
def home():

    summary = None
    document_type = None
    email = None
    phone = None
    table_html = None

    if request.method == "POST":

        file = request.files.get("pdf")

        if not file:
            return "Please select a PDF."

        if not file.filename.lower().endswith(".pdf"):
            return "Please upload a PDF file."

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(filepath)

        text_data = ""
        table_rows = []
        headers = None

        try:

            with pdfplumber.open(filepath) as pdf:

                for page in pdf.pages:

                    text = page.extract_text()

                    if text:
                        text_data += text + "\n"

                    tables = page.extract_tables()

                    for table in tables:

                        if table and len(table) > 1:

                            headers = table[0]

                            for row in table[1:]:
                                table_rows.append(row)

        except Exception as e:
            return f"Error reading PDF: {e}"

        # Extract information
        summary = generate_summary(text_data)
        document_type = detect_document_type(text_data)
        email = extract_email(text_data)
        phone = extract_phone(text_data)

        # Create table
        if table_rows and headers:

            try:

                df = pd.DataFrame(
                    table_rows,
                    columns=headers
                )

                df.to_csv(
                    "output.csv",
                    index=False
                )

                table_html = df.to_html(
                    classes="table table-bordered table-striped",
                    index=False
                )

            except:
                pass

        return render_template(
            "index.html",
            summary=summary,
            document_type=document_type,
            email=email,
            phone=phone,
            tables=table_html
        )

    return render_template(
        "index.html",
        summary=None,
        document_type=None,
        email=None,
        phone=None,
        tables=None
    )
import webbrowser

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)


#venv\Scripts\activate