from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from xml.sax.saxutils import escape

path=r'C:/Users/91881/Documents/OneDrive/Desktop/CSRA/Tushar_Saini_ATS_Resume.pdf'
doc=SimpleDocTemplate(path,pagesize=letter,rightMargin=.65*inch,leftMargin=.65*inch,topMargin=.48*inch,bottomMargin=.48*inch)
blue=colors.HexColor('#184667')
styles=getSampleStyleSheet()
name=ParagraphStyle('Name',parent=styles['Normal'],fontName='Helvetica-Bold',fontSize=19,leading=21,textColor=blue,alignment=TA_CENTER,spaceAfter=1)
role=ParagraphStyle('Role',parent=styles['Normal'],fontName='Helvetica-Bold',fontSize=10.5,leading=12,alignment=TA_CENTER,spaceAfter=2)
contact=ParagraphStyle('Contact',parent=styles['Normal'],fontName='Helvetica',fontSize=8.3,leading=10,alignment=TA_CENTER,spaceAfter=2)
section=ParagraphStyle('Section',parent=styles['Normal'],fontName='Helvetica-Bold',fontSize=10,leading=11,textColor=blue,spaceBefore=5,spaceAfter=3,borderPadding=0,borderColor=colors.HexColor('#9BB4C5'),borderWidth=0)
body=ParagraphStyle('Body',parent=styles['Normal'],fontName='Helvetica',fontSize=8.6,leading=10.1,spaceAfter=1)
skill=ParagraphStyle('Skill',parent=body,spaceAfter=.5)
projhead=ParagraphStyle('ProjHead',parent=body,fontSize=9.2,leading=10.4,spaceBefore=2,spaceAfter=.5)
bullet=ParagraphStyle('Bullet',parent=body,leftIndent=10,firstLineIndent=-8,spaceAfter=.5)
story=[]
story += [Paragraph('TUSHAR SAINI',name),Paragraph('Python Backend and Generative AI Engineer',role),Paragraph('Kurukshetra, Haryana  |  8814004472  |  tusharsaini1703@gmail.com',contact),Paragraph('<font color="#184667">GitHub:</font> github.com/tushar17s  |  <font color="#184667">LinkedIn:</font> linkedin.com/in/tushar-saini-6a2b5b248/',contact)]
def sect(t): story.append(Paragraph(t.upper(),section)); story.append(Spacer(1,1))
def para(t,style=body): story.append(Paragraph(t,style))
def project(t,stack,bs):
    items=[Paragraph(f'<b>{escape(t)}</b> <font size="8" color="#4B4B4B"><i>| {escape(stack)}</i></font>',projhead)]
    items += [Paragraph('• '+escape(b),bullet) for b in bs]
    story.append(KeepTogether(items))
sect('Professional Summary')
para('Computer Science graduate with hands-on experience building Python backend applications and REST APIs using FastAPI and Django. Built a retrieval-augmented generation (RAG) customer support assistant with local text embeddings and Groq-powered answer generation. Experienced with PostgreSQL, authentication, API design, and full-stack project development; seeking an entry-level Python GenAI or backend engineering role.')
sect('Technical Skills')
for k,v in [('Languages','Python, SQL, JavaScript (basic)'),('Backend','FastAPI, Django, Django REST Framework, REST APIs, Pydantic'),('Generative AI','Retrieval-Augmented Generation (RAG), embeddings, semantic search, prompt grounding, FastEmbed, Groq API'),('Databases','PostgreSQL, SQLite, JSON-based local vector index'),('Tools','Git, GitHub, Postman, Swagger / OpenAPI, Chrome Extensions (Manifest V3)')]: para(f'<b>{k}:</b> {escape(v)}',skill)
sect('Projects')
project('Customer Support RAG Assistant (CSRA)','Python, FastAPI, FastEmbed, Groq API',[
'Built a RAG application that retrieves relevant support knowledge-base passages using local embeddings and generates grounded answers through the Groq API.',
'Implemented text chunking with overlap, cosine-similarity ranking, a relevance threshold, source attribution, and a no-context fallback.',
'Created chat and document-upload endpoints plus a browser interface; added input validation, file type and size limits, and configurable CORS.'])
project('PersonalVault - Secure Knowledge Management API','Python, FastAPI, PostgreSQL',[
'Developed a backend API for personal learning resources with JWT authentication, CRUD operations, pagination, and user-based access control.',
'Deployed the API with interactive documentation: https://personalvault-api.onrender.com/api/docs.'])
project('JobFlow - Job Application Management System','Python, FastAPI, PostgreSQL, JavaScript, Chrome Extension',[
'Built a Chrome extension to capture job details from Indeed and Naukri and save them to a centralized dashboard.',
'Developed REST APIs and a dashboard with search, sorting, status tracking, statistics, and expandable job descriptions.'])
sect('Education')
para('<b>Bachelor of Technology in Computer Science and Engineering</b> | Kurukshetra University, JMIT Radaur | Aug 2026',skill)
para('Senior Secondary Certificate, 88% | Manish Papneja Memorial Public School, Kurukshetra | 2021',skill)
sect('Certifications and Achievements')
para('Generative AI Workshop - SkillStone  |  Python Training - Hoping Minds, Mohali  |  Practiced DSA on LeetCode, GeeksforGeeks, and HackerRank  |  1st place, inter-college Mukand Cup cricket tournament',skill)
doc.build(story)
print(path)

