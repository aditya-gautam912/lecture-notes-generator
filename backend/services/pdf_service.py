from fpdf import FPDF
import os

class LecturePDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Lecture Study Guide', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def sanitize(text):
    """Strips non-latin characters and control characters for PDF safety."""
    if not text:
        return ""
    # Convert to string if not already
    text = str(text)
    # Filter only printable ASCII for maximum safety with basic FPDF fonts
    return "".join(c for i, c in enumerate(text) if ord(c) < 128)

def create_lecture_pdf(data, output_path):
    pdf = LecturePDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Helvetica', 'B', 14)
    filename = sanitize(data['filename'])
    pdf.multi_cell(190, 10, f"Lecture: {filename}")
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(190, 10, f"Date: {data['date']}", 0, 1)
    pdf.ln(5)

    # Summary
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 10, 'Summary', 0, 1, 'L', True)
    pdf.set_font('Helvetica', '', 11)
    pdf.multi_cell(190, 7, sanitize(data['materials']['summary']))
    pdf.ln(5)

    # Study Notes
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(190, 10, 'Study Notes', 0, 1, 'L', True)
    pdf.set_font('Helvetica', '', 11)
    for note in data['materials']['notes']:
        pdf.multi_cell(190, 7, f"- {sanitize(note)}")
    pdf.ln(5)

    # Quiz
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(190, 10, 'Self-Assessment Quiz', 0, 1, 'L', True)
    pdf.ln(5)
    
    for i, q in enumerate(data['materials']['quiz']):
        pdf.set_font('Helvetica', 'B', 11)
        pdf.multi_cell(190, 7, f"Q{i+1}: {sanitize(q['question'])}")
        pdf.set_font('Helvetica', '', 10)
        for opt in q['options']:
            pdf.cell(190, 7, f"   {sanitize(opt)}", 0, 1)
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(190, 7, f"   Correct Answer: {sanitize(q['answer'])}", 0, 1)
        pdf.ln(3)

    pdf.output(output_path)
    return output_path
