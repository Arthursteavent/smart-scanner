import json
from pathlib import Path
from typing import List, Dict
from providers.base_provider import BaseAIProvider
from core.file_reader import extract_text

class LocalProvider(BaseAIProvider):
    def __init__(self):
        # Load keywords from JSON file
        self.keyword_map = self._load_keywords()
        
    def _load_keywords(self) -> Dict[str, List[str]]:
        try:
            import sys
            if getattr(sys, 'frozen', False):
                keywords_path = Path(sys._MEIPASS) / "core" / "keywords.json"
            else:
                keywords_path = Path("core/keywords.json")
                
            if keywords_path.exists():
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load keywords.json: {e}")
            
        # Fallback if file is missing
        return {
            'Work': ['laporan', 'kerja', 'work', 'invoice', 'cv', 'resume', 'project'],
            'Education': ['tugas', 'kuliah', 'sekolah', 'skripsi', 'jurnal', 'makalah'],
            'Finance': ['struk', 'tagihan', 'pajak', 'tax', 'bill', 'receipt'],
            'Personal': ['pribadi', 'personal', 'keluarga', 'family', 'liburan', 'foto'],
            'Digital Assets': ['design', 'mockup', 'psd', 'movie', 'video', 'music', 'setup', 'software', 'app'],
            'Archives': ['backup', 'archive', 'arsip', 'bundle']
        }

        
    def get_subcategory(self, ext: str) -> str:
        if ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            return "Documents"
        if ext in ['.xlsx', '.xls', '.csv']:
            return "Spreadsheets"
        if ext in ['.pptx', '.ppt']:
            return "Presentations"
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
            return "Images"
        if ext in ['.mp4', '.mkv', '.avi', '.mov']:
            return "Videos"
        if ext in ['.mp3', '.wav', '.flac']:
            return "Audio"
        if ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return "Archives"
        if ext in ['.html', '.php', '.css', '.js', '.py', '.cpp', '.java', '.json', '.sql']:
            return "Code"
        if ext in ['.exe', '.msi', '.apk']:
            return "Software"
        return "Others"

    def classify_files(self, files_metadata: List[Dict]) -> str:
        """
        Takes the file metadata, scores keywords to find the most accurate context,
        and assigns appropriate subcategories.
        """
        response_files = []
        
        for file in files_metadata:
            path = file.get("full_path", file.get("filename", ""))
            file_size = file.get("file_size", 0)
            created_at = file.get("created_at", "")
            is_duplicate = file.get("is_duplicate", False)
            
            if not path:
                continue
                
            # If it's a duplicate, skip all heuristics and route to Duplicates
            if is_duplicate:
                response_files.append({
                    "path": path,
                    "category": "Duplicates",
                    "subcategory": "",
                    "confidence": 100
                })
                continue
                
            # If it's a project folder, route it directly to Work/Projects
            if file.get("is_project", False):
                response_files.append({
                    "path": path,
                    "category": "Work",
                    "subcategory": "Projects",
                    "confidence": 100
                })
                continue
                
            full_path_lower = Path(path).as_posix().lower()
            ext = Path(path).suffix.lower()
            parent_dir = Path(path).parent.name.lower()
            
            category_scores = {cat: 0 for cat in self.keyword_map.keys()}
            subcategory = self.get_subcategory(ext)
            
            # --- HEURISTIC 1: Contextual Directory Scoring ---
            if parent_dir in ["sekolah", "kuliah", "tugas", "kampus", "materi", "university", "school"]:
                category_scores["Education"] += 15
            elif parent_dir in ["kantor", "kerja", "pt", "cv", "perusahaan", "office", "work"]:
                category_scores["Work"] += 15
            elif parent_dir in ["finance", "keuangan", "pajak", "tagihan", "invoice"]:
                category_scores["Finance"] += 15
            
            # --- HEURISTIC 1: File Size Logic ---
            # If file is > 1 GB (1073741824 bytes), it's almost certainly Digital Assets (Software/Media)
            if file_size > 1_000_000_000 and subcategory in ["Archives", "Software", "Videos", "Others"]:
                category_scores["Digital Assets"] += 10
            
            # --- HEURISTIC 3: Exact Phrase Matching ---
            exact_phrases = {
                "Work": ["laporan keuangan", "slip gaji", "surat keputusan", "meeting notes", "dokumen perusahaan", "kontrak kerja"],
                "Finance": ["kartu kredit", "bukti transfer", "mutasi rekening", "rekening koran", "tagihan listrik"],
                "Personal": ["kartu keluarga", "boarding pass", "tiket pesawat", "buku nikah", "akta kelahiran", "paspor", "resep dokter"],
                "Education": ["tugas akhir", "skripsi final", "kartu tanda mahasiswa", "jadwal kuliah", "silabus matakuliah"],
                "Digital Assets": ["mockup ui", "source code", "logo final", "installer windows", "crack patch"]
            }
            
            # 1. Score based on the full path
            for cat, keywords in self.keyword_map.items():
                for keyword in keywords:
                    normalized_path = full_path_lower.replace('\\', ' ').replace('/', ' ').replace('_', ' ').replace('-', ' ')
                    import re
                    if re.search(rf'\b{re.escape(keyword)}\b', normalized_path):
                        category_scores[cat] += 3 
                        
            # Check exact phrases in path
            for cat, phrases in exact_phrases.items():
                for phrase in phrases:
                    if phrase in full_path_lower.replace('_', ' ').replace('-', ' '):
                        category_scores[cat] += 100 # Absolute certainty
                        
            # 2. Score based on content if it's a readable document
            content_text = ""
            if ext in ['.pdf', '.txt', '.doc', '.docx', '.csv', '.xlsx']:
                content_text = extract_text(path)
                if content_text:
                    import re
                    
                    # Exact phrase check in content
                    for cat, phrases in exact_phrases.items():
                        for phrase in phrases:
                            if phrase in content_text:
                                category_scores[cat] += 100
                    
                    # --- HEURISTIC 3: Financial Currency Detection ---
                    if subcategory in ["Documents", "Spreadsheets"]:
                        currency_matches = re.findall(r'\b(rp|idr|usd|eur|saldo|kredit|debit)\b', content_text)
                        if len(currency_matches) > 3:
                            category_scores["Finance"] += 20 # Massive bonus for Finance
                    
                    # Standard keyword scoring
                    for cat, keywords in self.keyword_map.items():
                        for keyword in keywords:
                            matches = re.findall(rf'\b{re.escape(keyword)}\b', content_text)
                            count = len(matches)
                            category_scores[cat] += min(count, 3)
            
            # --- HEURISTIC 5: Disambiguation & Negative Scoring ---
            # "tugas" conflict
            if "tugas" in full_path_lower or (content_text and "tugas" in content_text):
                if any(w in full_path_lower for w in ["kantor", "manajer", "divisi", "karyawan"]):
                    category_scores["Work"] += 20
                    category_scores["Education"] -= 20
                elif any(w in full_path_lower for w in ["sekolah", "kuliah", "dosen", "mahasiswa", "kampus"]):
                    category_scores["Education"] += 20
                    category_scores["Work"] -= 20
            
            # "budget" / "uang" + spreadsheet synergy
            if ext in ['.xlsx', '.csv'] and ("budget" in full_path_lower or "uang" in full_path_lower):
                if any(w in full_path_lower for w in ["kantor", "proyek", "laporan", "divisi"]):
                    category_scores["Work"] += 30
                elif any(w in full_path_lower for w in ["pribadi", "keluarga", "bulanan"]):
                    category_scores["Personal"] += 30
                else:
                    category_scores["Finance"] += 20
                    
            # Digital Assets conflict
            if "laporan" in full_path_lower or "report" in full_path_lower:
                category_scores["Digital Assets"] -= 20
            
            # Find the category with the highest score
            best_category = max(category_scores, key=category_scores.get)
            
            # If highest score is 0, smart fallback logic based on subcategory
            if category_scores[best_category] <= 0:
                if subcategory in ["Spreadsheets"]:
                    # Assume spreadsheets are mostly Work or Finance
                    category = "Work"
                elif subcategory in ["Documents", "Presentations"]:
                    category = "Work"
                elif subcategory in ["Code"]:
                    category = "Digital Assets"
                elif subcategory in ["Images"]:
                    category = "Personal" # By default images are personal (photos)
                    if "screenshot" in full_path_lower or "design" in full_path_lower:
                        category = "Digital Assets"
                elif subcategory in ["Videos", "Audio", "Software"]:
                    category = "Digital Assets"
                elif subcategory == "Archives":
                    category = "Archives"
                else:
                    category = "Others" # Only for truly unknown files
            else:
                category = best_category
                
            # --- HEURISTIC 4: Chronological Media Sorting ---
            # If it's media and goes to Personal, append the Year to the subcategory
            if category == "Personal" and subcategory in ["Images", "Videos"]:
                if created_at:
                    year = created_at.split("-")[0] # ISO format YYYY-MM-DD
                    subcategory = f"{subcategory}/{year}"
            
            # Add to response
            file_response = {
                "path": path,
                "category": category,
                "subcategory": subcategory,
                "confidence": 100
            }
                
            response_files.append(file_response)
            
        # Return as JSON string just like the AI providers do
        result = {
            "files": response_files
        }
        
        return json.dumps(result)
