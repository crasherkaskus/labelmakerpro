import re
from typing import List, Dict

def clean_prefix(text: str) -> str:
    """
    Cleans common prefixes from label text fields (e.g., 'Nama: John' -> 'John').
    """
    text = text.strip()
    # Remove leading numbering or bullets like '1.', '-', '*', '[1]', etc.
    text = re.sub(r'^(?:\d+[\.\)]|\*|-|•)\s*', '', text, flags=re.IGNORECASE)
    # Remove prefixes like 'Nama:', 'Alamat:', 'HP:', 'No. HP:', 'Telp:'
    text = re.sub(r'^(?:nama|alamat|hp|no\.?\s*hp|telp|telepon|address|name)\s*:\s*', '', text, flags=re.IGNORECASE)
    return text.strip()

def parse_line(line: str) -> Dict[str, str]:
    """
    Parses a single line into a label dict if it has separators.
    """
    line = line.strip()
    if not line:
        return {}
        
    # Try splitting by common delimiters
    delimiters = [r'\s+-\s+', r'\s*\|\s*', r'\s*;\s*', r'\t']
    parts = []
    for delim in delimiters:
        split_parts = re.split(delim, line)
        if len(split_parts) > 1:
            parts = split_parts
            break
            
    if len(parts) >= 2:
        nama = clean_prefix(parts[0])
        alamat = clean_prefix(parts[1])
        detail = ""
        if len(parts) > 2:
            detail = ", ".join(clean_prefix(p) for p in parts[2:])
        return {"nama": nama, "alamat": alamat, "detail": detail}
    
    return {"nama": clean_prefix(line), "alamat": "", "detail": ""}

def expand_quantities(labels: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Checks if label names end with a space followed by a number (with optional trailing semicolon).
    If so, replicates that label by the specified quantity.
    """
    expanded = []
    for lbl in labels:
        nama = lbl.get("nama", "").strip()
        alamat = lbl.get("alamat", "")
        detail = lbl.get("detail", "")
        
        # Match a space followed by digits, optional semicolon, and optional spaces at the end
        match = re.search(r'\s+(\d+)\s*;?\s*$', nama)
        if match:
            try:
                qty = int(match.group(1))
                # Clean name by removing the quantity suffix
                clean_nama = nama[:match.start()].strip()
                for _ in range(qty):
                    expanded.append({
                        "nama": clean_nama,
                        "alamat": alamat,
                        "detail": detail
                    })
            except ValueError:
                # Fallback in case conversion fails
                expanded.append(lbl)
        else:
            expanded.append(lbl)
    return expanded

def parse_raw_text(raw_text: str, single_line_mode: bool = False) -> List[Dict[str, str]]:
    """
    Parses raw unstructured text (e.g., copy-pasted from WhatsApp) into a structured list
    of labels containing 'nama', 'alamat', and 'detail'.
    """
    if not raw_text or not raw_text.strip():
        return []

    # Normalize line endings
    raw_text = raw_text.replace('\r\n', '\n')
    
    # If single_line_mode is requested, treat every line as a separate block
    if single_line_mode:
        blocks = [line.strip() for line in raw_text.split('\n') if line.strip()]
    else:
        # Try splitting by common block separators like dashed lines
        if re.search(r'\n[-_=*]{3,}\n', raw_text):
            blocks = re.split(r'\n[-_=*]{3,}\n', raw_text)
        else:
            # Otherwise, split by double newlines (empty lines)
            blocks = re.split(r'\n\s*\n', raw_text)

        # If splitting by double newlines yielded only 1 block, let's see if we have line-by-line format
        if len(blocks) <= 1:
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            # Check if most lines start with a number or bullet
            numbered_count = sum(1 for line in lines if re.match(r'^(?:\d+[\.\)]|\*|-|•)', line))
            # Or if most lines end with a number (quantity multiplier format)
            qty_count = sum(1 for line in lines if re.search(r'\s+(\d+)\s*;?\s*$', line))
            
            if (numbered_count >= len(lines) * 0.7 or qty_count >= len(lines) * 0.7) and len(lines) > 1:
                blocks = lines

    parsed_labels = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Split block into lines
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue

        # Heuristic: Check if this block has multiple lines, but most lines contain delimiters (like ' - ', ' | ', ';').
        # If so, it means the block is actually a list of individual single-line labels, not a single multi-line label.
        if len(lines) > 1 and not single_line_mode:
            delimiters = [r'\s+-\s+', r'\s*\|\s*', r'\s*;\s*', r'\t']
            has_delim_count = 0
            for line in lines:
                if any(re.search(delim, line) for delim in delimiters):
                    has_delim_count += 1
            
            if has_delim_count >= len(lines) * 0.7:
                # Treat each line as its own independent label
                for line in lines:
                    parsed = parse_line(line)
                    if parsed and parsed.get("nama"):
                        parsed_labels.append(parsed)
                continue

        nama = ""
        alamat = ""
        detail = ""

        # Case 1: Simple single line
        if len(lines) == 1 or single_line_mode:
            parsed = parse_line(lines[0])
            if parsed:
                parsed_labels.append(parsed)
        
        # Case 2: Multi-line block for a single label
        else:
            # First line is name
            nama = clean_prefix(lines[0])
            
            # Check if fields are explicitly labeled or match certain heuristics
            address_lines = []
            detail_lines = []
            
            for line in lines[1:]:
                cleaned_line = clean_prefix(line)
                lower_line = line.lower()
                
                # Check for phone numbers/details
                if any(k in lower_line for k in ['hp:', 'telp:', 'no. hp', 'telepon']) or re.search(r'\+?\d{9,15}', cleaned_line):
                    detail_lines.append(cleaned_line)
                elif any(k in lower_line for k in ['alamat:', 'jl.', 'jalan', 'gg.', 'gang', 'rt/rw', 'kec.', 'kab.']):
                    address_lines.append(cleaned_line)
                else:
                    # Default: add to address if we don't have one, else to details
                    if not address_lines:
                        address_lines.append(cleaned_line)
                    else:
                        detail_lines.append(cleaned_line)
            
            # Combine address and details
            if address_lines:
                alamat = " ".join(address_lines)
            if detail_lines:
                detail = " | ".join(detail_lines)
                
            # Fallback if address or detail is empty but we have extra lines
            if not alamat and not detail and len(lines) > 1:
                alamat = clean_prefix(lines[1])
                if len(lines) > 2:
                    detail = " | ".join(clean_prefix(l) for l in lines[2:])

            if nama:
                parsed_labels.append({
                    "nama": nama,
                    "alamat": alamat,
                    "detail": detail
                })

    # Expand quantity duplicates
    return expand_quantities(parsed_labels)
