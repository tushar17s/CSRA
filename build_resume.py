from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

out = Path(r'C:/Users/91881/Documents/OneDrive/Desktop/CSRA/Tushar_Saini_ATS_Resume.docx')
doc = Document()
sec=doc.sections[0]
sec.top_margin=Inches(.48); sec.bottom_margin=Inches(.48); sec.left_margin=Inches(.65); sec.right_margin=Inches(.65)
styles=doc.styles
normal=styles['Normal']; normal.font.name='Arial'; normal.font.size=Pt(9); normal.font.color.rgb=RGBColor(35,35,35)
normal._element.rPr.rFonts.set(qn('w:ascii'),'Arial'); normal._element.rPr.rFonts.set(qn('w:hAnsi'),'Arial')
normal.paragraph_format.space_after=Pt(1.5); normal.paragraph_format.line_spacing=1.0

def set_keep(p, next=False):
    p.paragraph_format.keep_together=True
    if next: p.paragraph_format.keep_with_next=True

def add_text(text, bold=False, size=9, color=(35,35,35), italic=False):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(1.5); set_keep(p)
    r=p.add_run(text); r.bold=bold; r.italic=italic; r.font.name='Arial'; r.font.size=Pt(size); r.font.color.rgb=RGBColor(*color)
    return p

def heading(text):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(5); p.paragraph_format.space_after=Pt(2); set_keep(p,True)
    r=p.add_run(text.upper()); r.bold=True; r.font.name='Arial'; r.font.size=Pt(10); r.font.color.rgb=RGBColor(24,70,103)
    pPr=p._p.get_or_add_pPr(); borders=OxmlElement('w:pBdr'); bottom=OxmlElement('w:bottom'); bottom.set(qn('w:val'),'single'); bottom.set(qn('w:sz'),'4'); bottom.set(qn('w:space'),'1'); bottom.set(qn('w:color'),'9BB4C5'); borders.append(bottom); pPr.append(borders)

def project(title, stack, bullets):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(2); p.paragraph_format.space_after=Pt(.5); set_keep(p,True)
    r=p.add_run(title); r.bold=True; r.font.size=Pt(9.4); r.font.name='Arial'
    if stack:
        r=p.add_run(' | '+stack); r.italic=True; r.font.size=Pt(8.4); r.font.name='Arial'; r.font.color.rgb=RGBColor(75,75,75)
    for b in bullets:
        p=doc.add_paragraph(style='Normal'); p.paragraph_format.left_indent=Inches(.13); p.paragraph_format.first_line_indent=Inches(-.11); p.paragraph_format.space_after=Pt(.5); set_keep(p)
        r=p.add_run('• '+b); r.font.name='Arial'; r.font.size=Pt(8.65)

p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(1)
r=p.add_run('TUSHAR SAINI'); r.bold=True; r.font.name='Arial'; r.font.size=Pt(19); r.font.color.rgb=RGBColor(24,70,103)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(2)
r=p.add_run('Python Backend and Generative AI Engineer'); r.bold=True; r.font.name='Arial'; r.font.size=Pt(10.5)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(4)
r=p.add_run('Kurukshetra, Haryana  |  8814004472  |  tusharsaini1703@gmail.com'); r.font.name='Arial'; r.font.size=Pt(8.5)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(2)
for i,(label,url) in enumerate([('GitHub','https://github.com/tushar17s'),('LinkedIn','https://www.linkedin.com/in/tushar-saini-6a2b5b248/')]):
    if i: p.add_run('  |  ')
    r=p.add_run(f'{label}: {url}'); r.font.name='Arial'; r.font.size=Pt(8.2); r.font.color.rgb=RGBColor(24,70,103)

heading('Professional Summary')
add_text('Computer Science graduate with hands-on experience building Python backend applications and REST APIs using FastAPI and Django. Built a retrieval-augmented generation (RAG) customer support assistant with local text embeddings and Groq-powered answer generation. Experienced with PostgreSQL, authentication, API design, and full-stack project development; seeking an entry-level Python GenAI or backend engineering role.')
heading('Technical Skills')
for label, value in [
('Languages','Python, SQL, JavaScript (basic)'),
('Backend','FastAPI, Django, Django REST Framework, REST APIs, Pydantic'),
('Generative AI','Retrieval-Augmented Generation (RAG), embeddings, semantic search, prompt grounding, FastEmbed, Groq API'),
('Databases','PostgreSQL, SQLite, JSON-based local vector index'),
('Tools','Git, GitHub, Postman, Swagger / OpenAPI, Chrome Extensions (Manifest V3)')]:
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(.5); set_keep(p)
    r=p.add_run(label+': '); r.bold=True; r.font.size=Pt(8.7); r.font.name='Arial'
    r=p.add_run(value); r.font.size=Pt(8.7); r.font.name='Arial'
heading('Projects')
project('Customer Support RAG Assistant (CSRA)','Python, FastAPI, FastEmbed, Groq API',[
'Built a RAG application that retrieves relevant support knowledge-base passages using local embeddings and generates grounded answers through the Groq API.',
'Implemented text chunking with overlap, cosine-similarity ranking, a relevance threshold, source attribution, and a no-context fallback.',
'Created chat and document-upload endpoints plus a browser interface; added input validation, file type and size limits, and configurable CORS.'])
project('PersonalVault - Secure Knowledge Management API','Python, FastAPI, PostgreSQL',[
'Developed a backend API for personal learning resources with JWT authentication, CRUD operations, pagination, and user-based access control.',
'Deployed the API with interactive documentation: https://personalvault-api.onrender.com/api/docs/'])
project('JobFlow - Job Application Management System','Python, FastAPI, PostgreSQL, JavaScript, Chrome Extension',[
'Built a Chrome extension to capture job details from Indeed and Naukri and save them to a centralized dashboard.',
'Developed REST APIs and a dashboard with search, sorting, status tracking, statistics, and expandable job descriptions.'])
heading('Education')
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(.5); set_keep(p,True)
r=p.add_run('Bachelor of Technology in Computer Science and Engineering'); r.bold=True; r.font.size=Pt(9); r.font.name='Arial'
r=p.add_run(' | Kurukshetra University, JMIT Radaur | Aug 2026'); r.font.size=Pt(8.6); r.font.name='Arial'
add_text('Senior Secondary Certificate, 88% | Manish Papneja Memorial Public School, Kurukshetra | 2021',size=8.6)
heading('Certifications and Achievements')
add_text('Generative AI Workshop - SkillStone  |  Python Training - Hoping Minds, Mohali  |  Practiced DSA on LeetCode, GeeksforGeeks, and HackerRank  |  1st place, inter-college Mukand Cup cricket tournament',size=8.4)

doc.core_properties.title='Tushar Saini - Python Backend and Generative AI Engineer Resume'
doc.core_properties.subject='ATS-friendly resume'
doc.core_properties.author='Tushar Saini'
doc.save(out)
print(out)
