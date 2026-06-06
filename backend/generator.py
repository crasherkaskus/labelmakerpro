import os
import io
import json
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader

# Try importing WeasyPrint
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

from xhtml2pdf import pisa

# Paths Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
CONFIG_PATH = os.path.join(BASE_DIR, "templates_config.json")

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def load_templates_config() -> Dict[str, Any]:
    """Loads templates from templates_config.json file."""
    if not os.path.exists(CONFIG_PATH):
        # Fallback if config does not exist yet (should not happen)
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_templates_config(config: Dict[str, Any]):
    """Saves updated templates to templates_config.json file."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def chunk_list(lst: List[Any], n: int) -> List[List[Any]]:
    """Yield successive n-sized chunks from lst."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def generate_pdf_bytes(
    labels: List[Dict[str, str]], 
    template_type: str,
    show_borders: bool = False,
    font_size_name: float = None,
    font_size_address: float = None,
    font_size_detail: float = None,
    single_line_mode: bool = False,
    font_family: str = "Arial",
    font_bold: bool = False,
    font_italic: bool = False,
    font_underline: bool = False
) -> bytes:
    """
    Renders dynamic templates using label configurations loaded from JSON
    and returns a PDF file as bytes.
    """
    templates = load_templates_config()
    if template_type not in templates:
        raise ValueError(f"Template type '{template_type}' is not supported. Available templates: {list(templates.keys())}")
    
    cfg = templates[template_type]
    
    # Extract settings
    name = cfg.get("name", f"Label {template_type}")
    label_height = float(cfg["label_height"])
    label_width = float(cfg["label_width"])
    vertical_pitch = float(cfg["vertical_pitch"])
    horizontal_pitch = float(cfg["horizontal_pitch"])
    number_across = int(cfg["number_across"])
    number_down = int(cfg["number_down"])
    top_margin = float(cfg["top_margin"])
    side_margin = float(cfg["side_margin"])
    sheet_width = float(cfg.get("sheet_width", 210.0))
    sheet_height = float(cfg.get("sheet_height", 297.0))
    
    # Compute gaps and outer table sizes
    row_gap = vertical_pitch - label_height
    col_gap = horizontal_pitch - label_width
    
    table_width = (number_across - 1) * horizontal_pitch + label_width
    table_height = (number_down - 1) * vertical_pitch + label_height
    col_span = number_across * 2 - 1
    
    labels_per_page = number_across * number_down
    
    # Setup default font sizes if not custom defined
    f_size_name = font_size_name or (12.0 if label_height > 25 else 10.0)
    f_size_address = font_size_address or (9.0 if label_height > 25 else 8.0)
    f_size_detail = font_size_detail or (8.0 if label_height > 25 else 7.0)
    
    # Process label list
    processed_labels = []
    for lbl in labels:
        processed_labels.append({
            "nama": lbl.get("nama", ""),
            "alamat": lbl.get("alamat", ""),
            "detail": lbl.get("detail", ""),
            "is_empty": False
        })
        
    # Chunk into pages
    pages_raw = chunk_list(processed_labels, labels_per_page)
    
    if pages_raw:
        # Fill the last page with empty slots
        last_page = pages_raw[-1]
        while len(last_page) < labels_per_page:
            last_page.append({"is_empty": True})
            
    # Chunk each page into rows of size equal to 'number_across'
    pages_table_structure = []
    for page in pages_raw:
        rows = chunk_list(page, number_across)
        pages_table_structure.append(rows)
        
    # Render template using dynamic_label.html
    template = env.get_template("dynamic_label.html")
    html_content = template.render(
        pages=pages_table_structure,
        show_borders=show_borders,
        font_size_name=f_size_name,
        font_size_address=f_size_address,
        font_size_detail=f_size_detail,
        template_name=name,
        table_width=table_width,
        table_height=table_height,
        side_margin=side_margin,
        top_margin=top_margin,
        label_width=label_width,
        label_height=label_height,
        col_gap=col_gap,
        row_gap=row_gap,
        col_span=col_span,
        single_line_mode=single_line_mode,
        sheet_width=sheet_width,
        sheet_height=sheet_height,
        font_family=font_family,
        font_bold=font_bold,
        font_italic=font_italic,
        font_underline=font_underline
    )
    
    # Compile PDF
    if WEASYPRINT_AVAILABLE:
        try:
            pdf_bytes = HTML(string=html_content).write_pdf()
            print("Compiled using WeasyPrint (Dynamic).")
            return pdf_bytes
        except Exception as e:
            print(f"WeasyPrint failed (Dynamic), falling back to xhtml2pdf: {e}")
            
    # Fallback to xhtml2pdf
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if pisa_status.err:
        raise RuntimeError(f"xhtml2pdf failed to compile PDF (Dynamic): {pisa_status.err}")
    
    print("Compiled using xhtml2pdf (Dynamic).")
    return pdf_buffer.getvalue()
