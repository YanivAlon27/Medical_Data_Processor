# Medical Data Processor

A Python-based solution for cleaning, formatting, and applying binary flagging to medical examination data using machine learning models.

## Overview

The `MedicalDataProcessor` class consolidates different functionalities into a unified framework to process medical data for machine learning evaluation. It includes data cleaning, binary flagging for medical tests, organs, and contrast, and overall data processing.

### Features

- **Data Cleaning:** Extracts and cleans medical recommendations from referral text.
- **Binary Flagging:** Applies binary flags for medical tests, organs/body parts, and contrast.
- **Standardization:** Standardizes contrast descriptions across different data sources.
- **Full Pipeline Integration:** Combines all steps into a single, easy-to-use processing method.

### Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/medical-data-processor.git
    ```
2. **Install Dependencies:**
    Ensure you have the required dependencies by installing via `pip`:
    ```bash
    pip install pandas numpy
    ```

### Usage

1. **Import the Class:**
    ```python
    from medical_data_processor import MedicalDataProcessor
    ```
2. **Create an Instance of the Processor:**
    ```python
    processor = MedicalDataProcessor()
    ```
3. **Prepare Your DataFrame:**
    Ensure your DataFrame contains the appropriate columns for processing:
    - `original_exam` (Exam Type)
    - `original_organ` (Organ/Body Part)
    - `original_contrast` (Contrast)

    Example DataFrame:
    ```python
    import pandas as pd

    data = pd.DataFrame({
        'original_exam': ['CT scan', 'MRI enterography', 'Ultrasound'],
        'original_organ': ['head', 'abdomen_pelvis', 'thorax'],
        'original_contrast': ['with iv contrast', 'without iv contrast', 'with or without iv contrast']
    })
    ```
4. **Process the Data:**
    Apply the `process_data` method to your DataFrame:
    ```python
    processed_data = processor.process_data(data, 'original_exam', 'original_organ', 'original_contrast')
    ```
5. **View the Processed Data:**
    The processed DataFrame will contain binary flag columns:
    ```python
    print(processed_data)
    ```

### Example Output
```python
# Example Data
original_exam         original_organ    original_contrast   original_exam_flags  original_organ_flags  original_contrast_flags
0    CT scan              head             with iv contrast       1                 1                    1
1    MRI enterography     abdomen_pelvis  without iv contrast     2                 8                    0
2    Ultrasound           thorax           with or without iv contrast  4           4                    2

