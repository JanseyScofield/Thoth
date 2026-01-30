# Thoth API - Receipt OCR

API developed with FastAPI to process receipts using OCR (PaddleOCR).

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Linux system

## 🚀 Step-by-Step Setup on Linux

### 1. Check Python installation

```bash
python3 --version
```

If Python is not installed, install it with:
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Create virtual environment (recommended)

```bash
cd /home/jansey/Documents/python-projects/thoth/Thoth
python3 -m venv venv
source venv/bin/activate
```

### 3. Install system dependencies (for PDF and image processing)

`pdf2image` requires `poppler`:

```bash
sudo apt install poppler-utils
```

### 4. Install Python dependencies

Execute the following commands in order:

```bash
# Install PaddleOCR and main dependencies
pip install "paddlepaddle>=2.6.0" "paddleocr==2.7.3" layoutparser shapely

# Remove opencv-python (if exists) and install compatible headless version
pip uninstall opencv-python opencv-python-headless -y
pip install opencv-python-headless==4.8.1.78

# Install compatible numpy version
pip install "numpy<2.0.0" --force-reinstall

# Install FastAPI and server
pip install fastapi uvicorn[standard]

# Install PDF processor
pip install pdf2image
```

**OR** install everything at once using the requirements.txt file:

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive documentation**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/

## 📝 Endpoints

### POST /scan
Upload a receipt image or PDF for processing.

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/scan" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/receipt.jpg"
```

## 🔧 Troubleshooting

### Error: `AttributeError: module 'cv2' has no attribute 'INTER_NEAREST'`
This error occurs when there's incompatibility between `imgaug` (PaddleOCR dependency) and OpenCV. Solution:

**Option 1: Quick script (recommended)**
```bash
bash fix_opencv.sh
```

**Option 2: Manual**
```bash
pip uninstall opencv-python opencv-python-headless -y
pip install opencv-python-headless==4.8.1.78
```

### OpenCV errors (others)
If you encounter other OpenCV-related errors, make sure you've uninstalled `opencv-python` and installed the compatible version:
```bash
pip uninstall opencv-python opencv-python-headless -y
pip install opencv-python-headless==4.8.1.78
```

### NumPy errors
If there are conflicts with NumPy, force reinstallation:
```bash
pip install "numpy<2.0.0" --force-reinstall
```

### PDF processing errors
Make sure you have installed `poppler-utils`:
```bash
sudo apt install poppler-utils
```

## 📦 Project Structure

```
Thoth/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── scan.py
│   ├── services/
│   │   ├── ocr_engines/
│   │   │   ├── ocr_engine.py
│   │   │   └── paddle_engine.py
│   │   ├── processors/
│   │   │   ├── image_processor.py
│   │   │   ├── pdf_processor.py
│   │   │   └── processor.py
│   │   └── receipt_service.py
│   └── main.py
├── requirements.txt
└── README.md
```
