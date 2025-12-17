# ===============================
#  knowledge.py (Simplified + Accurate)
#  Curated from Disease-Symptom GitHub Dataset
#  Cleaned + grouped for real-world usability
# ===============================

import csv
import os

# ===============================
#  knowledge.py (Dynamic from CSV)
#  Powered by Kaggle/GitHub Dataset
# ===============================

disease_to_symptoms = {}
csv_path = os.path.join(os.path.dirname(__file__), 'dataset.csv')

try:
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # The dataset uses 'Source' for Disease and 'Target' for Symptom
            disease = row['Source'].strip().title() # e.g. "Influenza"
            symptom = row['Target'].strip().lower() # e.g. "fever"
            
            if disease and symptom:
                if disease not in disease_to_symptoms:
                    disease_to_symptoms[disease] = []
                if symptom not in disease_to_symptoms[disease]:
                    disease_to_symptoms[disease].append(symptom)
                    
    print(f"Successfully loaded {len(disease_to_symptoms)} diseases from dataset.csv")

except FileNotFoundError:
    print("Error: dataset.csv not found. Please ensure the file exists.")
    # Fallback or empty initialization
    disease_to_symptoms = {
        "Example Disease": ["fever", "cough"]
    }
except Exception as e:
    print(f"Error loading dataset: {e}")

# ----------------------------------------------------------
# REVERSE MAPPING (symptom → diseases)
# ----------------------------------------------------------

symptom_to_diseases = {}
for disease, symptoms in disease_to_symptoms.items():
    for symptom in symptoms:
        symptom_to_diseases.setdefault(symptom, []).append(disease)

# ----------------------------------------------------------
# DISEASE DESCRIPTIONS
# ----------------------------------------------------------


# ----------------------------------------------------------
# DISEASE DESCRIPTIONS
# ----------------------------------------------------------

disease_info = {}
desc_path = os.path.join(os.path.dirname(__file__), 'disease_description.csv')

try:
    with open(desc_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'Disease' in row and 'Description' in row:
                disease = row['Disease'].strip().title()
                desc = row['Description'].strip()
                disease_info[disease] = desc
    print(f"Successfully loaded {len(disease_info)} descriptions.")
except FileNotFoundError:
    print("Error: disease_description.csv not found.")
except Exception as e:
    print(f"Error loading descriptions: {e}")

# ----------------------------------------------------------
# TREATMENT INFORMATION
# ----------------------------------------------------------

disease_treatments = {}
prec_path = os.path.join(os.path.dirname(__file__), 'disease_precaution.csv')

try:
    with open(prec_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'Disease' in row:
                disease = row['Disease'].strip().title()
                precautions = []
                # Columns are Precaution_1, Precaution_2, etc.
                for i in range(1, 5):
                    col = f"Precaution_{i}"
                    if row.get(col):
                        p = row[col].strip()
                        if p:
                            precautions.append(p.capitalize())
                
                if precautions:
                    disease_treatments[disease] = {
                        "precautions": precautions
                    }
    print(f"Successfully loaded {len(disease_treatments)} treatments.")
except FileNotFoundError:
    print("Error: disease_precaution.csv not found.")
except Exception as e:
    print(f"Error loading treatments: {e}")