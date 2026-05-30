from fpdf import FPDF
import os

class LecturePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Lecture Study Guide', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_lecture_pdf(data, output_path):
    pdf = LecturePDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Lecture: {data['filename']}", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f"Date: {data['date']}", 0, 1)
    pdf.ln(5)

    # Summary
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, 'Summary', 0, 1, 'L', True)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, data['materials']['summary'])
    pdf.ln(5)

    # Study Notes
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Study Notes', 0, 1, 'L', True)
    pdf.set_font('Arial', '', 11)
    for note in data['materials']['notes']:
        pdf.multi_cell(0, 7, f"• {note}")
    pdf.ln(5)

    # Quiz
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Self-Assessment Quiz', 0, 1, 'L', True)
    pdf.ln(5)
    
    for i, q in enumerate(data['materials']['quiz']):
        pdf.set_font('Arial', 'B', 11)
        pdf.multi_cell(0, 7, f"Q{i+1}: {q['question']}")
        pdf.set_font('Arial', '', 10)
        for opt in q['options']:
            pdf.cell(0, 7, f"   {opt}", 0, 1)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 7, f"   Correct Answer: {q['answer']}", 0, 1)
        pdf.ln(3)

    pdf.output(output_path)
    return output_path
