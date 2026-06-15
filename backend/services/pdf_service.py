from fpdf import FPDF
import os
import io
import zipfile
import urllib.request

FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fonts')
FONT_PATH = os.path.join(FONT_DIR, 'DejaVuSans.ttf')
FONT_URL = "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-sans-ttf-2.37.zip"

if not os.path.isdir(FONT_DIR):
    os.makedirs(FONT_DIR)

if not os.path.isfile(FONT_PATH):
    try:
        resp = urllib.request.urlopen(FONT_URL)
        z = zipfile.ZipFile(io.BytesIO(resp.read()))
        ttf_name = [n for n in z.namelist() if n.endswith("DejaVuSans.ttf")][0]
        with open(FONT_PATH, "wb") as f:
            f.write(z.read(ttf_name))
    except Exception as e:
        print(f"Warning: Could not download DejaVuSans font: {e}")

class LecturePDF(FPDF):
    def header(self):
        self.set_font('DejaVu', 'B', 15)
        self.cell(0, 10, 'Lecture Study Guide', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_lecture_pdf(data, output_path):
    pdf = LecturePDF()
    pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
    pdf.add_font('DejaVu', 'B', FONT_PATH, uni=True)
    pdf.add_page()

    pdf.set_font('DejaVu', 'B', 14)
    pdf.multi_cell(190, 10, f"Lecture: {data['filename']}")
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(190, 10, f"Date: {data['date']}", 0, 1)
    pdf.ln(5)

    pdf.set_font('DejaVu', 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 10, 'Summary', 0, 1, 'L', True)
    pdf.set_font('DejaVu', '', 11)
    pdf.multi_cell(190, 7, data['materials']['summary'])
    pdf.ln(5)

    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(190, 10, 'Study Notes', 0, 1, 'L', True)
    pdf.set_font('DejaVu', '', 11)
    for note in data['materials']['notes']:
        pdf.multi_cell(190, 7, f"- {note}")
    pdf.ln(5)

    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(190, 10, 'Self-Assessment Quiz', 0, 1, 'L', True)
    pdf.ln(5)

    for i, q in enumerate(data['materials']['quiz']):
        pdf.set_font('DejaVu', 'B', 11)
        pdf.multi_cell(190, 7, f"Q{i+1}: {q['question']}")
        pdf.set_font('DejaVu', '', 10)
        for opt in q['options']:
            pdf.cell(190, 7, f"   {opt}", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(190, 7, f"   Correct Answer: {q['answer']}", 0, 1)
        pdf.ln(3)

    pdf.output(output_path)
    return output_path
