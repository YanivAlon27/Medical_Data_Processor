import pandas as pd
import re

class MedicalDataProcessor:
    """
    A class to clean, format, and flag medical examination data.
    
    Attributes:
    ----------
    keywords : list
        List of keywords used to identify contrast details in referrals.
    ct_types : list
        List of CT types to identify specific CT-related medical examinations.
    exam_categories : dict
        Dictionary mapping medical exam categories to associated terms.
    organ_clusters : dict
        Dictionary mapping organ clusters to associated terms.
    contrast_standardization_map : dict
        Dictionary mapping various contrast descriptions to standardized terms.
    """

    def __init__(self):
        """
        Initializes MedicalDataProcessor with specific keywords, CT types, exam categories,
        organ clusters, and contrast standardization map.
        """
        # Keywords for contrast extraction
        self.keywords = ['w', 'wo', 'with', 'without','wo/w']

        # CT types for exam extraction
        self.ct_types = ["angiography", "arthrography", "enterography", "fistulogram", 
                         "urography", "venography", "quantitative",'scan']

        # Exam categories for binary flagging
        self.exam_categories = {
            'CT Scans': ['ct', 'ct angiography', 'ct enterography', 'ct high resolution', 'ct colonography', 'ct venography', 'ct maxillofacial',
                         'ct pancreatitis protocol', 'ct retroperitoneal', 'ct angiography retroperitoneum', 'ct retroperitoneal space',
                         'ct retroperitineal space', 'ct pancreas protoco', 'ct enteroclysis', 'ct angiography perfusion', 'ct angiography aortography',
                         'ct arteriography', 'ct artrography', 'computed tomography ct scan', 'high resolution ct scan', 'ct, x-ray', 'ct, ct urography', 'ct, xray'],
            'MRI': ['mri', 'mri enterography', 'mri angiography', 'mri brain and mr angiography', 'cardiac mri', 'pelvic mri', 'mrcp', 'mrv'],
            'Ultrasound and Doppler Studies': ['ultrasound', 'doppler ultrasound', 'carotid duplex ultrasound', 'pelvic ultrasound', 'arterial/venous duplex ultrasound', 'duplex ultrasound'],
            'Radiography and X-Ray': ['xray', 'mammogram', 'mammography', 'radiography', 'dental ct scan', 'barium swallow study', 'x-ray'],
            'Nuclear Medicine': ['petct', 'nuclear bone scan', 'bone scan', 'whole body bone scan', 'pet scan', 'dexa scan'],
            'Invasive and Interventional Procedures': ['cervical nerve root block', 'lumbar nerve root block', 'pudendal nerve root block', 'catheter',
                                                       'biopsy', 'colonoscopy', 'retrograde pyelogram', 'esophagography', 'cystoscopy', 'cystography',
                                                       'esophagogastroduodenoscopy', 'epidural steroid injection'],
            'Cardiovascular Specific Exams': ['echocardiogram', 'stress test', 'coronary angiography', 'stress echocardiogram'],
            'Health Check-ups and Other Exams': ['general health check-up', 'general physical exam', 'complete blood count', 'general check-up',
                                                 'physical examination', 'comprehensive metabolic panel', 'complete body scan', 'check-up', 'general check up']
        }

        # Organ clusters for binary flagging
        self.organ_clusters = {
            "head": ["head", "cranial", "skull", "brain", "cerebral", "facial", "sinus", "paranasal sinuses", "temporal bone", 
                     "face", "orbit", "temporomandibular joints", "maxilla", "sinuses", "mandible", "pituitary gland", 
                     "maxillofacial area", "maxillofacial", "nasopharynx", "salivary glands", "maxillofacial region", 
                     "mouth area", 'tongue', 'scalp', 'pituitary', 'eye', 'intracranial', "ear", "temporomandibular joint"],
            "neck": ["neck", "cervical", "throat", "nuchal", "larynx", "esophagus", "carotid arteries", "carotid", "parotid gland", "thyroid"],
            "thorax": ["thorax", "chest", "thoracic", "pulmonary", "heart", "cardiac", "breast", "mediastinum", "aorta", 
                       "aortic", "coronary", "coronaries", "aorta branches", "sternoclavicular joint", "breasts", "trachea", "lung", "lungs", "clavicula", "scapula bone",
                       "joint sternoclavicular", "subclavian artery", "coronary arteries"],
            "abdomen_pelvis": ["abdomen", "abdominal", "stomach", "intestinal", "gastrointestinal", "liver", "pancreas", "spleen", "small bowel", "colon", 
                               "colonography colon", "gallbladder", "kidney", "kidneys", "urinary organs", "biliary tract", "biliary system", "renal", "adrenal",
                               "adrenal gland", "adrenal glands", "pelvis", "pelvic", "hip", "inguinal", "pubic", "iliac vein", "urinary bladder", "urinary tract", "prostate",
                               "uterus", "uterus and ovaries"],
            "upper_extremities": ["upper", "arm", "shoulder", "elbow", "wrist", "hand", "scapula", "clavicle", 
                                  "humerus", "right humerus", "ulna left", "forearm", "left forearm", "finger", 'brachial plexus', "right thumb"],
            "lower_extremities": ["lower", "leg", "knee", "knees", "foot", "thigh", "tibia", "femur", "calcaneus", 
                                  "popliteal artery", "knees bilateral", "right malleolus", 'femoral nerve left', "lower extremities", "iliofemoral arteries", "ankle"],
            "spine": ["spine", "vertebral", "lumbar", "sacral", "spinal canal", "spinal cord", "spinal", "thoracic spine"],
            "skeletal": ["joint", "bone", "bones", "skeletal", "skeleton", "extremities", "musculoskeletal", "musculoskeletal system"],
            "lymphatic": ["lymph nodes", "lymphatic system"],
            "body": ["whole body", "body", 'full body', 'various organs', 'multiple organs',
                     "extremities", "multiple organ systems", 'muscular system', 'skin', 'limbs', "blood", "peripheral", 'endocrine system', "muscles",
                     "vascular region", "vascular system", "arterial system"]
        }

        # Contrast standardization map
        self.contrast_standardization_map = {
            'with iv contrast ': 'with iv contrast', 
            'without iv contrast ': 'without iv contrast',
            ' with iv contrast': 'with iv contrast',
            ' with or without iv contrast':'with or without iv contrast', 
            ' without iv contrast': 'without iv contrast',
            'with or without iv contrast ':'with or without iv contrast',
        }

    def clean_recommendation(self, text):
        """
        Extracts and cleans recommendation text based on specific keywords.

        Parameters:
        ----------
        text : str
            The recommendation or referral text to be cleaned.

        Returns:
        -------
        str
            The cleaned recommendation or referral.
        """
        match = re.search(r"(Recommendation|Exam):\s*([^.\n]+)", text, re.IGNORECASE)
        if match:
            return match.group(2).strip()
        else:
            return text.replace("\n", " ").strip().rstrip('.')
        
    def format_referral(self, row):
        """
        Processes a referral row to extract examination details.

        Parameters:
        ----------
        row : str
            A single row from the referral data containing medical information.

        Returns:
        -------
        list
            A list containing three elements: the exam type, the body part, and the contrast details.
            If parsing fails, returns a list of None values.
        """
        if not isinstance(row, str):
            return [None, None, None]
        
        try:
            # Split and clean elements from the referral text
            elements = row.split(' ')
            elements = [s.strip().replace(',', '') for s in elements]

            # Identify the exam type
            ct_index = None
            for index, element in enumerate(elements):
                if element in self.ct_types:
                    ct_index = index
                    break

            if ct_index is not None:
                exam = ' '.join(elements[:ct_index + 1])
            else:
                exam = elements[0]
                ct_index = 0

            other_elements = elements[ct_index + 1:]
            body_part, contrast, keyword_index = None, None, None

            # Extract the body part and contrast details
            for index, element in enumerate(other_elements):
                if element in self.keywords:
                    keyword_index = index
                    break

            if keyword_index is not None:
                body_part = ' '.join(other_elements[:keyword_index])
                contrast = ' '.join(other_elements[keyword_index:])
            else:
                body_part = ' '.join(other_elements)

            return [exam, body_part, contrast]
        
        except Exception:
            return [None, None, None]
    
    def apply_cleaning_to_dataframe(self, df, column_name):
        """
        Applies the cleaning function to a DataFrame column.

        Parameters:
        ----------
        df : pd.DataFrame
            The DataFrame containing referral data.
        column_name : str
            The name of the column to clean.

        Returns:
        -------
        pd.Series
            The cleaned recommendations as a pandas Series.
        """
        return df[column_name].apply(self.clean_recommendation)
    
    def apply_formatting_to_dataframe(self, df, column_name):
        """
        Applies the formatting function to a DataFrame and expands into multiple columns.

        Parameters:
        ----------
        df : pd.DataFrame
            The DataFrame containing referral data.
        column_name : str
            The name of the column to format.

        Returns:
        -------
        pd.DataFrame
            The formatted DataFrame with 'Exam', 'Body Part', and 'Contrast' columns.
        """
        return df.apply(lambda x: pd.Series(self.format_referral(x[column_name])), axis=1)

    def tokenize_and_flag_organs(self, phrase):
        """
        Converts organ/body part text into binary flag categories.

        Parameters:
        ----------
        phrase : str
            The organ/body part text to be converted into binary flags.

        Returns:
        -------
        int
            The binary flag representing matched organ clusters.
        """
        if pd.isna(phrase):
            return None
        cleaned_phrase = re.sub(r"-", " ", str(phrase))
        cleaned_phrase = re.sub(r"[^\w\s]", "", cleaned_phrase.lower())
        binary_flag = 0
        cluster_tokens = {
            "head": 1 << 0, "neck": 1 << 1, "thorax": 1 << 2, "abdomen_pelvis": 1 << 3,
            "upper_extremities": 1 << 4, "lower_extremities": 1 << 5, "spine": 1 << 6,
            "skeletal": 1 << 7, "lymphatic": 1 << 8, "body": 1 << 9
        }
        for cluster, terms in self.organ_clusters.items():
            if any(re.search(r"\b" + re.escape(term) + r"\b", cleaned_phrase) for term in terms):
                binary_flag |= cluster_tokens[cluster]
        return binary_flag

    def map_exam_to_binary_flag(self, exam_name):
        """
        Converts exam type text into binary flag categories.

        Parameters:
        ----------
        exam_name : str
            The exam type text to be converted into binary flags.

        Returns:
        -------
        int
            The binary flag representing matched exam categories.
        """
        if pd.isna(exam_name):
            return None  # Return None for missing values
        cleaned_exam = re.sub(r"-", " ", str(exam_name))  # Replace hyphens with spaces
        cleaned_exam = re.sub(r"[^\w\s]", "", cleaned_exam.lower())  # Remove punctuation and convert to lower case
        
        binary_flag = 0
        # Define binary positions for each exam category
        categories_to_flags = {
            'CT Scans': 1 << 0,
            'MRI': 1 << 1,
            'Ultrasound and Doppler Studies': 1 << 2,
            'Radiography and X-Ray': 1 << 3,
            'Nuclear Medicine': 1 << 4,
            'Invasive and Interventional Procedures': 1 << 5,
            'Cardiovascular Specific Exams': 1 << 6,
            'Health Check-ups and Other Exams': 1 << 7
        }
        
        # Check each category for matching terms in the exam description
        for category, flag in categories_to_flags.items():
            if any(re.search(r"\b" + re.escape(term) + r"\b", cleaned_exam) for term in self.exam_categories[category]):
                binary_flag |= flag

        return binary_flag

    def standardize_contrast(self, column):
        """
        Applies standardization to contrast descriptions.

        Parameters:
        ----------
        column : pd.Series
            The pandas Series containing contrast data.

        Returns:
        -------
        pd.Series
            The standardized contrast data as a pandas Series.
        """
        return column.map(self.contrast_standardization_map).fillna(column)

    def encode_binary_flags_contrast(self, df, column):
        """
        Encodes contrast descriptions into binary flags.

        Parameters:
        ----------
        df : pd.DataFrame
            The DataFrame containing contrast data.
        column : str
            The name of the column to encode.

        Returns:
        -------
        None
            Modifies the DataFrame in place to include a new column with binary flags.
        """
        df[column + '_flags'] = df[column].map({
            'with iv contrast': 1,
            'without iv contrast': 0,
            'with or without iv contrast': 2  # or another suitable encoding
        })

    def process_data(self, df, exam_column, organ_column, contrast_column):
        """
        Applies the entire processing pipeline to a DataFrame.

        Parameters:
        ----------
        df : pd.DataFrame
            The DataFrame containing medical examination data.
        exam_column : str
            The name of the column containing exam type data.
        organ_column : str
            The name of the column containing organ/body part data.
        contrast_column : str
            The name of the column containing contrast data.

        Returns:
        -------
        pd.DataFrame
            The processed DataFrame with binary flag columns added.
        """
        # Apply exam binary flags
        df[exam_column + '_flags'] = df[exam_column].apply(self.map_exam_to_binary_flag)

        # Apply organ binary flags
        df[organ_column + '_flags'] = df[organ_column].apply(self.tokenize_and_flag_organs)

        # Apply contrast standardization and binary flags
        df[contrast_column] = self.standardize_contrast(df[contrast_column])
        self.encode_binary_flags_contrast(df, contrast_column)

        return df

# Usage example:
# processor = MedicalDataProcessor()
# data = pd.read_csv('medical_data.csv')
# processed_data = processor.process_data(data, 'original_exam', 'original_organ', 'original_contrast')
