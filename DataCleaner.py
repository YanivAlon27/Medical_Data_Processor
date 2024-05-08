import pandas as pd
import re

class DataCleaner:
    """
    A class to clean and format medical examination data.
    
    Attributes:
    ----------
    keywords : list
        List of keywords used to identify contrast details in referrals.
    ct_types : list
        List of CT types to identify specific CT-related medical examinations.
    """

    def __init__(self):
        """
        Initializes DataCleaner with specific keywords and CT types.
        """
        self.keywords = ['w', 'wo', 'with', 'without','wo/w']
        self.ct_types = ["angiography", "arthrography", "enterography", "fistulogram", 
                         "urography", "venography", "quantitative",'scan']

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
    
    def check_columns(self, df, required_columns):
        """
        Checks if all required columns are present in the DataFrame.

        Parameters:
        ----------
        df : pd.DataFrame
            The DataFrame to check.
        required_columns : list
            List of required column names.

        Returns:
        -------
        bool
            True if all required columns are present, raises an error otherwise.
        """
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")
        return True


