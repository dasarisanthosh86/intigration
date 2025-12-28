from fpdf import FPDF
from datetime import datetime

class PRDPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Convert hex to RGB tuples for safety across fpdf versions
        self.primary_color = (15, 23, 42)    # #0f172a (Slate 900)
        self.secondary_color = (30, 41, 59)  # #1e293b (Slate 800)
        self.accent_color = (59, 130, 246)   # #3b82f6 (Blue 500)
        self.text_color = (51, 65, 85)       # #334155 (Slate 600)
        self.bg_color = (248, 250, 252)      # #f8fafc (Slate 50)
        self.muted_color = (148, 163, 184)   # #94a3b8 (Slate 400)
        
    def _set_color(self, color_tuple, type="text"):
        """Helper to set color from RGB tuple."""
        r, g, b = color_tuple
        if type == "text":
            self.set_text_color(r, g, b)
        elif type == "fill":
            self.set_fill_color(r, g, b)
        elif type == "draw":
            self.set_draw_color(r, g, b)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("helvetica", "B", 8)
        self._set_color(self.muted_color)
        self.cell(0, 10, "Product Requirements Document", 0, 0, "L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self._set_color(self.muted_color)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def chapter_title(self, num, label):
        self.set_font("helvetica", "B", 16)
        self._set_color(self.primary_color)
        self.ln(10)
        self.cell(0, 10, f"{num}. {label}", 0, 1, "L")
        self._set_color(self.accent_color, "draw")
        self.line(self.get_x(), self.get_y(), self.get_x() + 180, self.get_y())
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("helvetica", "", 11)
        self._set_color(self.text_color)
        self.multi_cell(0, 7, body)
        self.ln()

    def add_table(self, header, data):
        self.set_font("helvetica", "B", 10)
        self._set_color(self.secondary_color, "fill")
        self.set_text_color(255, 255, 255)
        
        # Calculate column widths based on longest content or even
        num_cols = len(header)
        # Use 180 max width to be safe with margins
        col_width = 180 / num_cols
        
        for col in header:
            self.cell(col_width, 10, col, 1, 0, "C", True)
        self.ln()
        
        self.set_font("helvetica", "", 10)
        self._set_color(self.text_color)
        for row in data:
            self.set_fill_color(255, 255, 255)
            # Calculate max height for the row
            max_h = 10
            # Just use multi_cell if content is long, but for simplicity here we use cell
            for item in row:
                self.cell(col_width, 10, str(item), 1, 0, "C")
            self.ln()
        self.ln(5)

    def create_cover_page(self, title, prepared_by):
        self.add_page()
        self._set_color(self.primary_color, "fill")
        self.rect(0, 0, 210, 297, "F")
        
        self.set_y(120)
        self.set_font("helvetica", "B", 40)
        self.set_text_color(255, 255, 255)
        self.multi_cell(0, 20, title, 0, "C")
        
        self.ln(30)
        self.set_font("helvetica", "", 14)
        self._set_color(self.muted_color)
        self.cell(0, 10, f"Prepared by: {prepared_by}", 0, 1, "C")
        self.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, "C")

    def add_table(self, header, data):
        self.set_font("helvetica", "B", 10)
        self._set_color(self.secondary_color, "fill")
        self.set_text_color(255, 255, 255)
        
        # Specific widths for DB schema: Table (40), Fields (140)
        # Reduced from 150 to ensure 180 total width, preventing overflow
        widths = [40, 140]
        
        for i, col in enumerate(header):
            self.cell(widths[i], 10, col, 1, 0, "C", True)
        self.ln()
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(self.text_color)
        for row in data:
            # We use multi_cell for the fields column to prevent overflow
            start_x = self.get_x()
            start_y = self.get_y()
            
            # Table name
            self.cell(widths[0], 12, str(row[0]), 1, 0, "C")
            
            # Fields (using multi_cell for wrapping)
            curr_x = self.get_x()
            self.multi_cell(widths[1], 12, str(row[1]), 1, "L")
            self.set_xy(start_x, self.get_y())
        self.ln(5)

class PDFService:
    def __init__(self):
        pass

    async def generate_from_markdown(self, markdown_content: str, output_path: str) -> str:
        """
        Converts markdown-style content to a professional PDF.
        Handles code blocks and long strings to prevent fpdf2 errors.
        """
        pdf = PRDPDF()
        pdf.alias_nb_pages()
        
        # Simple header for architecture/reports
        title = "Architecture Report" if "Architecture" in markdown_content else "System Report"
        pdf.create_cover_page(title, "Antigravity SDLC Agent")
        
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Executive Summary", 0, 1)
        pdf.ln(5)
        
        pdf.set_font("helvetica", "", 11)
        
        lines = markdown_content.split('\n')
        in_code_block = False
        
        for line in lines:
            # Handle Code Blocks
            if line.strip().startswith("```"):
                if not in_code_block:
                    # Enter code block
                    in_code_block = True
                    pdf.set_font("courier", "", 9)
                    pdf._set_color(pdf.secondary_color, "text") # Dark slate for code
                    pdf.ln(2)
                    continue
                else:
                    # Exit code block
                    in_code_block = False
                    pdf.set_font("helvetica", "", 11)
                    pdf._set_color(pdf.text_color, "text")
                    pdf.ln(5)
                    continue
            
            if in_code_block:
                try:
                    pdf.multi_cell(0, 5, line)
                except Exception:
                    # Fallback for very long code lines: truncate or char-wrap
                    pdf.multi_cell(0, 5, line[:80] + "...")
                continue

            # Standard Logic
            if line.startswith('## '):
                pdf.ln(5)
                pdf.set_font("helvetica", "B", 13)
                pdf.cell(0, 10, line[3:], 0, 1)
                pdf.set_font("helvetica", "", 11)
            elif line.startswith('# '):
                pdf.ln(10)
                pdf.set_font("helvetica", "B", 16)
                pdf.cell(0, 10, line[2:], 0, 1)
                pdf.set_font("helvetica", "", 11)
            elif line.startswith('**'):
                clean_line = line.replace('**', '')
                pdf.set_font("helvetica", "B", 11)
                try:
                    pdf.multi_cell(0, 7, clean_line)
                except Exception:
                    pdf.multi_cell(0, 7, clean_line[:100] + "...")
                pdf.set_font("helvetica", "", 11)
            else:
                try:
                    pdf.multi_cell(0, 7, line)
                except Exception as e:
                    # Handle "Not enough horizontal space" by brute-force splitting
                    # This happens with very long URLs or tokens
                    if "horizontal space" in str(e).lower() or "character" in str(e).lower():
                        # Simple word breaking strategy
                        chunk_size = 80
                        chunks = [line[i:i+chunk_size] for i in range(0, len(line), chunk_size)]
                        for chunk in chunks:
                            pdf.multi_cell(0, 7, chunk)
                    else:
                        print(f"PDF Gen Warning: Skipping problematic line: {line[:20]}... Error: {e}")

        pdf.output(output_path)
        return output_path

def generate_pdf_from_data(data, output_path):
    pdf = PRDPDF()
    pdf.alias_nb_pages()
    
    # Page 1: Bold PRD Title
    pdf.create_cover_page(data.get("title", "Product Requirements Document (PRD)"), data.get("prepared_by", "ChatGPT"))
    
    # Page-by-page construction
    pages = data.get("pages", [])
    for page_sections in pages:
        pdf.add_page()
        for section in page_sections:
            pdf.chapter_title(section.get("num", ""), section.get("title", ""))
            
            section_type = section.get("type", "text")
            if section_type == "text":
                pdf.chapter_body(section.get("content", ""))
            elif section_type == "table":
                pdf.add_table(section.get("header", []), section.get("data", []))
            elif section_type == "subtitle":
                # For things like User Features vs Admin Features
                pdf.set_font("helvetica", "B", 13)
                pdf.set_text_color("#1e293b")
                pdf.cell(0, 10, section.get("content", ""), 0, 1, "L")
                pdf.ln(2)
            
    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    # Test with Hotel PRD data
    # ... (rest of the file stays same)
    # Test with Hotel PRD data
    hotel_prd_data = {
        "title": "Hotel Booking Application",
        "subtitle": "Product Requirements Document",
        "prepared_by": "ChatGPT",
        "sections": [
            {
                "title": "Product Overview",
                "content": "The Hotel Booking Application allows users to search, view, book, and manage hotel reservations.\nAdmin users can register hotels, manage rooms, pricing, and availability."
            },
            {
                "title": "Objectives",
                "content": "- Enable users to search and book hotels.\n- Provide real-time room availability.\n- Allow hotels to manage rooms and pricing.\n- Ensure secure and smooth user experience."
            },
            {
                "title": "Tech Stack",
                "content": "- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL, Redis\n- Frontend: React or Next.js\n- Testing: PyTest\n- Deployment: Docker, CI/CD"
            },
            {
                "title": "Core Features",
                "content": "User Features:\n- Registration, Login\n- Hotel Search\n- Room Details\n- Booking\n- Payment\n- Booking Management\n\nAdmin Features:\n- Hotel Management\n- Room Management\n- Booking Dashboard"
            },
            {
                "title": "Non-Functional Requirements",
                "content": "- Performance\n- Scalability\n- Security\n- Availability\n- Maintainability"
            },
            {
                "title": "Database Schema",
                "type": "table",
                "header": ["Table", "Fields"],
                "data": [
                    ["Users", "user_id, name, email, password, role"],
                    ["Hotels", "hotel_id, name, city, description, rating"],
                    ["Rooms", "room_id, hotel_id, type, price, capacity, availability_count"],
                    ["Bookings", "booking_id, user_id, room_id, check_in, check_out, price, status"]
                ]
            },
            {
                "title": "API Endpoints",
                "content": "/auth/register\n/auth/login\n/hotels\n/bookings"
            },
            {
                "title": "Unit Test Cases",
                "content": "- User Registration\n- Login\n- Search Hotels\n- Create Booking\n- Cancel Booking"
            },
            {
                "title": "User Stories",
                "content": "- As a user, I want to search hotels.\n- As a user, I want to book rooms.\n- As an admin, I want to manage hotels and rooms."
            },
            {
                "title": "Milestones",
                "content": "- Sprint 1: Auth module\n- Sprint 2: Hotel search\n- Sprint 3: Booking system\n- Sprint 4: Admin dashboard\n- Sprint 5: Testing & Deployment"
            }
        ]
    }
    generate_pdf_from_data(hotel_prd_data, "Hotel_Booking_PRD.pdf")
