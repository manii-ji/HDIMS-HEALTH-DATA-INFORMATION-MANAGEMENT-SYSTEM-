import pandas as pd
import os

class DataManager:
    EXCEL_FILE = 'hospital_data.xlsx'

    def __init__(self):
        # Create Excel file if it does not exist
        if not os.path.exists(self.EXCEL_FILE):
            df = pd.DataFrame(columns=['Hospital Name', 'Patient Name', 'Disease Name', 'Doctor Name'])
            df.to_excel(self.EXCEL_FILE, index=False)

    def get_all_data(self):
        df = pd.read_excel(self.EXCEL_FILE)
        if 'Hospital Name' in df.columns:
            return df.values.tolist()
        return []

    def add_data(self, hospital_name, patient_name, disease_name, doctor_name):
        df = pd.read_excel(self.EXCEL_FILE)
        new_row = pd.DataFrame([{
            'Hospital Name': hospital_name,
            'Patient Name': patient_name,
            'Disease Name': disease_name,
            'Doctor Name': doctor_name
        }])
        
        # Using pd.concat to add the new row
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(self.EXCEL_FILE, index=False)

    def get_unique_hospitals_count(self):
        df = pd.read_excel(self.EXCEL_FILE)
        return df['Hospital Name'].nunique() if 'Hospital Name' in df.columns else 0

    def get_total_patients_count(self):
        df = pd.read_excel(self.EXCEL_FILE)
        return len(df) if 'Patient Name' in df.columns else 0
