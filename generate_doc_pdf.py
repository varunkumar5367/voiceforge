#!/usr/bin/env python3
"""
VoiceForge — generate_doc_pdf.py
Generates a professional, easy-to-understand PDF documentation for VoiceForge.
Explains terms simply for non-technical audiences and fixes table text wrapping.
"""

import sys
import subprocess

# Auto-install reportlab if not present
try:
    import reportlab
except ImportError:
    print("Installing reportlab dependency...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to calculate total page count and draw
    headers and footers dynamically on all pages except the cover page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page
            
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#5858a0"))
        
        # Running Header
        self.drawString(54, 750, "VoiceForge — Project Presentation Guide")
        self.setStrokeColor(colors.HexColor("#e1e1f0"))
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)
        
        # Running Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Live Studio Link: https://voiceforge-pzxd.onrender.com")
        self.line(54, 52, 558, 52)
        
        self.restoreState()

def generate_pdf():
    pdf_filename = "VoiceForge_Documentation.pdf"
    
    # Document Setup with 0.75 in (54 pt) margins
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=30,
        leading=36,
        textColor=colors.HexColor('#7c3aed'), # Violet
        spaceAfter=15,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#2563eb'), # Blue
        spaceAfter=140,
        alignment=1
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        textColor=colors.HexColor('#5858a0'),
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=22,
        textColor=colors.HexColor('#07071a'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#7c3aed'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=colors.HexColor('#1a1a3e'),
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'CodeCustom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2563eb'),
        backColor=colors.HexColor('#f4f4fa'),
        borderColor=colors.HexColor('#d1d1eb'),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=10
    )

    # Styles for table wrapping
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1a1a3e')
    )

    table_code_style = ParagraphStyle(
        'TableCode',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#2563eb')
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 140))
    story.append(Paragraph("VoiceForge Studio", title_style))
    story.append(Paragraph("The Simple Guide to Our AI Narrator Project", subtitle_style))
    
    meta_text = """
    <b>Project Guide & Friendly Documentation</b><br/>
    <b>Live Link to Try It:</b> <font color="#2563eb">https://voiceforge-pzxd.onrender.com</font><br/>
    <b>Designed For:</b> General Audiences & Presentations<br/>
    <b>Date:</b> June 2026<br/>
    <b>Made with:</b> HTML · CSS · JavaScript · Python · AI Voices
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(PageBreak())
    
    # ------------------ SECTION 1 ------------------
    story.append(Paragraph("1. Project Introduction & Purpose", h1_style))
    story.append(Paragraph(
        "<b>What is VoiceForge?</b><br/>"
        "VoiceForge is a website that takes written text (like an article, a video script, or a PDF document) "
        "and converts it into realistic, high-quality audio narration. We built it using Microsoft's "
        "advanced artificial intelligence (AI) voice technology. It sounds like a real person—with natural pauses, "
        "proper word pronunciation, and a choice of regional accents (British, American, Indian, Australian, etc.).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Why did we build this?</b><br/>"
        "Typical voice generator tools have three main problems: they sound like old robotic computers, they limit "
        "how much text you can type at once, and they require paid plans. VoiceForge solves this for free. It is "
        "designed for content creators, students who prefer listening to books, and general users who want to "
        "turn long PDFs into audible podcasts easily.",
        body_style
    ))
    
    # ------------------ TECH STACK SECTION ------------------
    story.append(Paragraph("2. The Technology Stack (Explained Simply)", h1_style))
    story.append(Paragraph(
        "To build VoiceForge, we used a combination of different technologies. Here is what they are "
        "and how they contribute to the project:",
        body_style
    ))
    
    tech_stack_data = [
        ["Technology", "What it is", "What it does in VoiceForge"],
        ["HTML5", "The Skeleton", "Builds the basic structure of the site—creating the text boxes, voice buttons, pitch sliders, and audio players."],
        ["CSS3", "The Appearance", "Adds style and color! Gives the site its 'glass' look, animations, and handles the button to toggle between Light and Dark mode."],
        ["JavaScript (JS)", "The Brain on the Page", "Detects when you click buttons, reads your uploaded PDF, manages the progress bar, and plays the audio clips."],
        ["Python", "The Server Engine", "Runs in the cloud, listens to requests, handles backend calculations, and prepares files for download."],
        ["edge-tts", "The AI Translator", "A package that connects the server to Microsoft's AI servers to translate the written text into natural spoken voices."],
        ["PDF.js", "The PDF Reader", "A script built by Mozilla that lets the website extract text from your uploaded PDF files without needing external readers."]
    ]
    
    t_tech = Table(tech_stack_data, colWidths=[95, 105, 300])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d1eb')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
    ]))
    
    # Convert tech stack data to paragraphs for proper cell wrapping
    formatted_tech = []
    formatted_tech.append([
        Paragraph(tech_stack_data[0][0], table_header_style),
        Paragraph(tech_stack_data[0][1], table_header_style),
        Paragraph(tech_stack_data[0][2], table_header_style)
    ])
    for row in tech_stack_data[1:]:
        formatted_tech.append([
            Paragraph(row[0], table_code_style),
            Paragraph(row[1], table_body_style),
            Paragraph(row[2], table_body_style)
        ])
        
    t_tech = Table(formatted_tech, colWidths=[90, 110, 300])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7c3aed')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d1eb')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_tech)
    story.append(PageBreak())
    
    # ------------------ SECTION 3 ------------------
    story.append(Paragraph("3. How VoiceForge Works (The Core Workflow)", h1_style))
    story.append(Paragraph(
        "Here is the simple step-by-step path of how a sentence typed on the screen becomes an audio file you can download:",
        body_style
    ))
    
    workflow_steps = """
    <b>Step 1: Inputting Content</b><br/>
    The user pastes a script on the website or drops in a PDF. If it's a PDF, our reader (PDF.js) extracts the text automatically.<br/><br/>
    
    <b>Step 2: The Word Cutter (Chunking)</b><br/>
    AI voices can crash or slow down if you send them a 10,000-word book all at once. The server automatically cuts the script into smaller pieces (about 2500 characters each). It is smart—it only cuts at paragraph breaks, periods, or commas so it does not cut a word in half.<br/><br/>
    
    <b>Step 3: Talking and Recording</b><br/>
    The website sends each piece of text to our cloud backend. The backend calls Microsoft's AI service, which speaks the text and returns a small audio clip.<br/><br/>
    
    <b>Step 4: Memory Vault (Caching)</b><br/>
    To make things fast, our server saves every generated audio clip. If you generate the same sentence again, it retrieves the file from its disk memory instantly, rather than waiting to create it from scratch.<br/><br/>
    
    <b>Step 5: Stitching and Downloading</b><br/>
    Once all the smaller text pieces are converted into small audio clips, the site combines (stitches) them together into one single long MP3 file. The audio player updates on your screen and shows a green 'Save as MP3' button for you to download.
    """
    story.append(Paragraph(workflow_steps, body_style))
    story.append(Spacer(1, 10))
    
    # ------------------ SECTION 4 ------------------
    story.append(Paragraph("4. System Modularity: What do the files do?", h1_style))
    story.append(Paragraph(
        "To make the code clean and organized, we divided it into separate files. Here is what each file does, explained in simple terms:",
        body_style
    ))
    
    story.append(Paragraph("The Backend Files (Running in the Cloud):", h2_style))
    
    backend_raw = [
        ["File Name", "Analogy", "What it does in simple terms"],
        ["chunker.py", "The Word Cutter", "Splits long books or scripts into smaller paragraphs and sentences so the AI voice generator can read them smoothly without crashing."],
        ["tts_service.py", "The Voice Actor", "Takes the small text pieces, sends them to Microsoft's AI, and returns the spoken audio bytes."],
        ["cache_manager.py", "The Memory Vault", "Remembers previous audio generations. If you read the same script again, it pulls the audio instantly from storage, saving processing time."],
        ["progress_manager.py", "The Scorekeeper", "Tracks statistics—how many words were generated, how long the processing took, and how many times we reused saved audio."],
        ["server.py", "The Store Manager", "The master brain. Runs on the computer, coordinates between the website UI and the Python files, and serves the site."]
    ]
    
    formatted_backend = []
    formatted_backend.append([
        Paragraph(backend_raw[0][0], table_header_style),
        Paragraph(backend_raw[0][1], table_header_style),
        Paragraph(backend_raw[0][2], table_header_style)
    ])
    for row in backend_raw[1:]:
        formatted_backend.append([
            Paragraph(row[0], table_code_style),
            Paragraph(row[1], table_body_style),
            Paragraph(row[2], table_body_style)
        ])
        
    t_backend = Table(formatted_backend, colWidths=[110, 110, 280])
    t_backend.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7c3aed')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d1eb')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_backend)
    story.append(PageBreak())
    
    story.append(Paragraph("The Frontend Files (Running on your Browser):", h2_style))
    
    frontend_raw = [
        ["File Name", "Analogy", "What it does in simple terms"],
        ["presets.js", "Quick-Setting Buttons", "Provides one-click settings. Clicking 'Audiobook' or 'Conversational' instantly moves the speed/pitch sliders to pre-optimized levels."],
        ["chunking.js", "The Loading Coordinator", "Sends the text chunks to the backend one by one, moves the progress bar, and automatically retries once if the internet drops."],
        ["comparison.js", "The Audition Panel", "Lets you select up to 4 voices and plays a short preview of your script side-by-side so you can pick the best voice."],
        ["audioPlayer.js", "The Stats Sheet", "Builds the collapsible stats panel at the bottom of the screen showing characters, time elapsed, and estimated audio length."],
        ["app.js", "The Stage Manager", "Controls the website visual state: handles text box counts, drops in PDFs, and switches between Dark and Light mode."]
    ]
    
    formatted_frontend = []
    formatted_frontend.append([
        Paragraph(frontend_raw[0][0], table_header_style),
        Paragraph(frontend_raw[0][1], table_header_style),
        Paragraph(frontend_raw[0][2], table_header_style)
    ])
    for row in frontend_raw[1:]:
        formatted_frontend.append([
            Paragraph(row[0], table_code_style),
            Paragraph(row[1], table_body_style),
            Paragraph(row[2], table_body_style)
        ])
        
    t_frontend = Table(formatted_frontend, colWidths=[110, 110, 280])
    t_frontend.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563eb')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d1eb')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_frontend)
    story.append(Spacer(1, 10))

    # ------------------ SECTION 5 ------------------
    story.append(Paragraph("5. Main Features Explained", h1_style))
    
    story.append(Paragraph("5.1 Voice Presets", h2_style))
    story.append(Paragraph(
        "Instead of forcing users to guess the best speed and pitch numbers, we created 5 built-in presets "
        "designed for popular video and narration styles. When clicked, they automatically tune the controls:",
        body_style
    ))
    
    presets_raw = [
        ["Preset Name", "Speech Speed", "Voice Pitch (Tone)", "Volume Level"],
        ["Professional Narration", "Slightly Faster (+5%)", "Warm / Deep (-1 Hz)", "Normal (+3%)"],
        ["Conversational", "Upbeat / Fast (+8%)", "Bright / Friendly (+2 Hz)", "Loud (+5%)"],
        ["Documentary", "Calm / Slow (+4%)", "Deep / Serious (-2 Hz)", "Balanced (+2%)"],
        ["Audiobook", "Normal Speed (0%)", "Relaxed (-1 Hz)", "Loud (+4%)"],
        ["Fast Presentation", "Very Fast (+15%)", "Energetic (+1 Hz)", "Loud (+5%)"]
    ]
    
    formatted_presets = []
    formatted_presets.append([
        Paragraph(presets_raw[0][0], table_header_style),
        Paragraph(presets_raw[0][1], table_header_style),
        Paragraph(presets_raw[0][2], table_header_style),
        Paragraph(presets_raw[0][3], table_header_style)
    ])
    for row in presets_raw[1:]:
        formatted_presets.append([
            Paragraph(row[0], table_body_style),
            Paragraph(row[1], table_body_style),
            Paragraph(row[2], table_body_style),
            Paragraph(row[3], table_body_style)
        ])
        
    t_presets = Table(formatted_presets, colWidths=[150, 110, 110, 130])
    t_presets.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f4f4fa')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e1e1f0')),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_presets)
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.2 Voice Comparison (Audition Grid)", h2_style))
    story.append(Paragraph(
        "If you don't know which voice suits your script best, check the 'Compare' boxes on your favorite voices "
        "and click 'Compare Voices'. The site generates short previews of all of them at the same time. "
        "They appear side-by-side, each with a play button, a download button, and a green 'Use This Voice' button. "
        "This makes choosing a voice simple and fast.",
        body_style
    ))
    story.append(PageBreak())

    # ------------------ SECTION 6 ------------------
    story.append(Paragraph("6. Security & Settings", h1_style))
    
    story.append(Paragraph("6.1 Folder Path Protection (Security fix)", h2_style))
    story.append(Paragraph(
        "A common security problem on websites is 'Path Traversal' (when an attacker tricks the site into "
        "opening system files outside the web folder by sending requests like `../../Windows/System32`).<br/><br/>"
        "We protected VoiceForge by adding code that converts every request into an absolute file path and "
        "validates that it starts within the project folder. If a request tries to escape, it is blocked "
        "with a 404 error, keeping user data secure.",
        body_style
    ))
    
    story.append(Paragraph("6.2 Cloud Ready Port Binding", h2_style))
    story.append(Paragraph(
        "When websites are deployed online (like on Render), the cloud platform assigns a dynamic port number. "
        "We updated the server code to read the port dynamically. This ensures the app deploys successfully and "
        "is instantly reachable on the web.",
        body_style
    ))
    
    # ------------------ SECTION 7 ------------------
    story.append(Paragraph("7. How to run and test it yourself", h1_style))
    story.append(Paragraph(
        "You can run this project locally on your machine or try the live link I deployed for you.",
        body_style
    ))
    
    story.append(Paragraph("Live Production Link:", h2_style))
    story.append(Paragraph(
        "The live studio instance is running and fully operational in the cloud at:<br/>"
        "<b><font color='#2563eb'>https://voiceforge-pzxd.onrender.com</font></b>",
        body_style
    ))
    
    story.append(Paragraph("To Run Locally (Installation):", h2_style))
    story.append(Paragraph(
        "1. Open your terminal inside the project directory.<br/>"
        "2. Run the command to install dependencies:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font name='Courier'>pip install -r requirements.txt</font><br/>"
        "3. Start the server:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font name='Courier'>python server.py</font><br/>"
        "4. Open your web browser and go to:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#2563eb'>http://localhost:8080</font>",
        body_style
    ))
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Documentation PDF updated and wrapped successfully.")

if __name__ == "__main__":
    generate_pdf()
