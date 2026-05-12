from flask import Flask, render_template, request, send_file, redirect, url_for, Response
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "khmer_attendance_key"

# បញ្ជីសិស្សសកល (Global list) ដើម្បីរក្សាទុកទិន្នន័យដែលបាន import
student_list = []

KHMER_DIGITS = str.maketrans('0123456789', '០១២៣៤៥៦៧៨៩')
KHMER_MONTHS = [
    "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
    "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ"
]

def format_khmer_number(value):
    return str(value).translate(KHMER_DIGITS)


def format_khmer_date(date_obj):
    day = format_khmer_number(date_obj.day)
    month = KHMER_MONTHS[date_obj.month - 1]
    year = format_khmer_number(date_obj.year)
    return f"ថ្ងៃទី {day} ខែ {month} ឆ្នាំ {year}"


async def create_pdf(html_content):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_path = f"attendance_report_{timestamp}.pdf"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        await page.pdf(path=pdf_path, format="A4", print_background=True)
        await browser.close()
    return pdf_path

@app.route('/')
def index():
    return render_template('index.html', students=student_list)

@app.route('/import', methods=['POST'])
def import_excel():
    global student_list
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        # អានទិន្នន័យពី Excel ដោយប្រើ pandas
        df = pd.read_excel(file)
        
        # បំប្លែងទិន្នន័យទៅជា List នៃ Dictionary
        # សន្មតថា Column ក្នុង Excel ឈ្មោះ "ឈ្មោះសិស្ស"
        if "ឈ្មោះសិស្ស" in df.columns:
            student_list = []
            for index, row in df.iterrows():
                student_list.append({
                    "id": index + 1,
                    "name": row["ឈ្មោះសិស្ស"]
                })
        return redirect(url_for('index'))

@app.route('/export', methods=['POST'])
def export_pdf():
    present_ids = request.form.getlist('attendance')
    leave_ids = request.form.getlist('leave')
    attendance_data = []
    
    for s in student_list:
        if str(s['id']) in leave_ids:
            status = "សុំច្បាប់"
        elif str(s['id']) in present_ids:
            status = "វត្តមាន"
        else:
            status = "អវត្តមាន"
        attendance_data.append({"name": s['name'], "status": status})

    report_date = format_khmer_date(datetime.now())
    report_title = f"របាយការណ៍វត្តមានសិស្ស {report_date}"
    rendered_html = render_template(
        'report_template.html',
        data=attendance_data,
        days=report_date,
        title=report_title
    )
    pdf_file = asyncio.run(create_pdf(rendered_html))
    download_name = f"របាយការណ៍វត្តមាន_{report_date}.pdf"

    with open(pdf_file, 'rb') as f:
        pdf_content = f.read()
    os.remove(pdf_file)  # Remove the PDF file after reading
    return Response(pdf_content, mimetype='application/pdf', headers={'Content-Disposition': f'attachment; filename*=UTF-8\'\'{quote(download_name)}'})

if __name__ == '__main__':
    app.run(debug=True)