# VVOR & VORS Test Analyzer

A tool for processing, visualizing, and evaluating vestibular test data (VVOR & VORS).  
Includes features for loading data files, selecting individual tests, and running automated graphical and numerical analysis.

---

## Authors

- **Jorge Rey-Martinez**
- **Maria Landa**
- **HAL** (AI assistant)

---

## Main Features

- Graphical interface based on Tkinter (Windows and Mac compatible)
- Selection and analysis of test blocks from `.txt` data files
- Automatic results generation, including graphs and reports
- Facilitates reviewing and managing large sets of VVOR/VORS tests

---

## Installation

1. **Clone this repository:**

    ```bash
    git clone https://github.com/bendermh/vvor-test-analyzer.git
    cd vvor-test-analyzer
    ```

2. **(Optional) Create a virtual environment:**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    source venv/bin/activate # On Mac/Linux
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

### Running from source

```bash
python main.py
