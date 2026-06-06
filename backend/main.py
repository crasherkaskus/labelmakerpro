from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import sys
import os

# Ensure parent directory is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.parser import parse_raw_text
from backend.generator import generate_pdf_bytes, load_templates_config, save_templates_config

app = FastAPI(
    title="Label Maker API", 
    description="API backend untuk mem-parse text data WhatsApp dan mencetak label stiker presisi secara dinamis.",
    version="1.1.0"
)

# Enable CORS for potential cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class ParseRequest(BaseModel):
    raw_text: str
    single_line_mode: Optional[bool] = False

class LabelItem(BaseModel):
    nama: str
    alamat: Optional[str] = ""
    detail: Optional[str] = ""

class GeneratePDFRequest(BaseModel):
    labels: List[LabelItem]
    template_type: str
    show_borders: Optional[bool] = False
    font_size_name: Optional[float] = None
    font_size_address: Optional[float] = None
    font_size_detail: Optional[float] = None
    single_line_mode: Optional[bool] = False
    font_family: Optional[str] = "Arial"
    font_bold: Optional[bool] = False
    font_italic: Optional[bool] = False
    font_underline: Optional[bool] = False

class TemplateModel(BaseModel):
    name: str = Field(..., description="Nama Template Label (e.g. Label 103)")
    label_height: float = Field(..., description="Tinggi Label (mm)")
    label_width: float = Field(..., description="Lebar Label (mm)")
    vertical_pitch: float = Field(..., description="Vertical Pitch (mm)")
    horizontal_pitch: float = Field(..., description="Horizontal Pitch (mm)")
    number_across: int = Field(..., description="Jumlah kolom stiker")
    number_down: int = Field(..., description="Jumlah baris stiker")
    top_margin: float = Field(..., description="Margin Atas Kertas (mm)")
    side_margin: float = Field(..., description="Margin Samping Kertas (mm)")
    sheet_width: Optional[float] = Field(210.0, description="Lebar Kertas (mm)")
    sheet_height: Optional[float] = Field(297.0, description="Tinggi Kertas (mm)")

@app.get("/")
def read_root():
    return {"message": "Label Maker API with Dynamic Templates is active!"}

# Template Management CRUD Endpoints
@app.get("/api/templates")
def get_templates():
    """Returns all available label templates and their settings."""
    try:
        return load_templates_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat konfigurasi template: {str(e)}")

@app.post("/api/templates/{template_id}")
def add_template(template_id: str, payload: TemplateModel):
    """Creates a new label template configuration."""
    try:
        templates = load_templates_config()
        if template_id in templates:
            raise HTTPException(status_code=400, detail=f"Template ID '{template_id}' sudah digunakan.")
            
        templates[template_id] = payload.model_dump()
        save_templates_config(templates)
        return {"status": "success", "message": f"Template '{payload.name}' berhasil ditambahkan."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menambah template: {str(e)}")

@app.put("/api/templates/{template_id}")
def update_template(template_id: str, payload: TemplateModel):
    """Updates an existing label template configuration."""
    try:
        templates = load_templates_config()
        if template_id not in templates:
            raise HTTPException(status_code=44, detail=f"Template ID '{template_id}' tidak ditemukan.")
            
        templates[template_id] = payload.model_dump()
        save_templates_config(templates)
        return {"status": "success", "message": f"Template '{payload.name}' berhasil diubah."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengubah template: {str(e)}")

@app.delete("/api/templates/{template_id}")
def delete_template(template_id: str):
    """Deletes a label template configuration."""
    try:
        templates = load_templates_config()
        if template_id not in templates:
            raise HTTPException(status_code=404, detail=f"Template ID '{template_id}' tidak ditemukan.")
            
        name = templates[template_id].get("name", template_id)
        del templates[template_id]
        save_templates_config(templates)
        return {"status": "success", "message": f"Template '{name}' berhasil dihapus."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghapus template: {str(e)}")

# Parser Endpoint
@app.post("/api/parse", response_model=List[LabelItem])
def parse_endpoint(payload: ParseRequest):
    """Parses raw text into structured JSON label items."""
    try:
        parsed_data = parse_raw_text(payload.raw_text, payload.single_line_mode)
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses data teks: {str(e)}")

# Generator Endpoint
@app.post("/api/generate-pdf")
def generate_pdf_endpoint(payload: GeneratePDFRequest):
    """Generates PDF bytes using the specified label template and customizations."""
    try:
        if not payload.labels:
            raise HTTPException(status_code=400, detail="Data label tidak boleh kosong.")

        labels_dict = [item.model_dump() for item in payload.labels]
        
        pdf_bytes = generate_pdf_bytes(
            labels=labels_dict,
            template_type=payload.template_type,
            show_borders=payload.show_borders,
            font_size_name=payload.font_size_name,
            font_size_address=payload.font_size_address,
            font_size_detail=payload.font_size_detail,
            single_line_mode=payload.single_line_mode,
            font_family=payload.font_family,
            font_bold=payload.font_bold,
            font_italic=payload.font_italic,
            font_underline=payload.font_underline
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=label_{payload.template_type}.pdf",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal men-generate PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
