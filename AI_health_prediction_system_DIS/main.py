import pandas as pd
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from constraint import Problem, AllDifferentConstraint
from fuzzywuzzy import fuzz
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font

def parse_symptoms(symptoms_str):
    """Convert symptoms string to list of cleaned symptoms."""
    return [s.strip().lower() for s in symptoms_str.split(',') if s.strip()]

def load_data():
    """Load CSP and Bayesian data."""
    csp_data = pd.read_csv("data2.csv")
    bayes_data = pd.read_csv("structured_bayesian_data.csv")
    return csp_data, bayes_data

def fuzzy_match(symptom, disease_symptoms):
    """Check if a symptom matches any of the disease symptoms using fuzzy logic."""
    for ds in disease_symptoms:
        if fuzz.partial_ratio(symptom, ds) > 80:
            return True
    return False

def apply_csp_filter(data, country, age_group, symptoms):
    """Apply CSP filtering based on country, age group, and symptoms."""
    problem = Problem()
    
    # Filter data by country
    country_filtered = data[data['Country'].str.strip().str.lower() == country.strip().lower()]
    if country_filtered.empty:
        print(f"No diseases found for country: {country}")
        return None
    
    diseases = country_filtered['Disease Name'].unique()
    problem.addVariables(diseases, [True, False])
    
    for disease in diseases:
        disease_data = country_filtered[country_filtered['Disease Name'] == disease].iloc[0]
        
        # Check if the selected age group matches the 'Age Group Most Affected'
        age_group_affected = disease_data['Age Group Most Affected'].strip().lower()
        age_match = any(age_group_affected == age.strip().lower() for age in age_group)
        
        # Parse symptoms
        disease_symptoms = set(
            parse_symptoms(disease_data['Common Symptoms (Easy)']) + 
            parse_symptoms(disease_data['Common Symptoms (Complex)'])
        )
        
        def combined_constraint(is_present, age_match=age_match, disease_symptoms=disease_symptoms):
            # At least 2 constraints should match
            symptom_match = sum(1 for symptom in symptoms if fuzzy_match(symptom, disease_symptoms)) >= 2
            matches = sum([age_match, symptom_match, True])  # True for country match
            return not is_present or matches >= 2
        
        problem.addConstraint(combined_constraint, [disease])
    
    problem.addConstraint(AllDifferentConstraint())
    
    solutions = problem.getSolutions()
    if solutions:
        filtered_diseases = [disease for disease, is_present in solutions[0].items() if is_present]
        return filtered_diseases
    else:
        # Fallback to diseases matching country and age group
        fallback_diseases = country_filtered[country_filtered.apply(
            lambda row: row['Age Group Most Affected'].strip().lower() in [age.strip().lower() for age in age_group], axis=1
        )]['Disease Name'].unique()
        return fallback_diseases if len(fallback_diseases) > 0 else None

def calculate_naive_bayes_prediction(structured_data, filtered_diseases, symptoms):
    """Calculate Naive Bayes prediction based on symptoms and filtered diseases."""
    if filtered_diseases:
        data = structured_data[structured_data['Disease Name'].isin(filtered_diseases)]
    else:
        data = structured_data
    
    X = data.drop('Disease Name', axis=1)
    y = data['Disease Name']
    
    symptom_vector = np.zeros(len(X.columns))
    for symptom in symptoms:
        for i, col in enumerate(X.columns):
            if symptom.lower() in col.lower():
                symptom_vector[i] = 1
    
    model = MultinomialNB(alpha=1.0)
    model.fit(X, y)
    
    probs = model.predict_proba([symptom_vector])
    diseases_probs = list(zip(model.classes_, probs[0]))
    
    total_prob = sum(prob for _, prob in diseases_probs)
    normalized_probs = [(disease, prob / total_prob) for disease, prob in diseases_probs]
    
    return sorted(normalized_probs, key=lambda x: x[1], reverse=True)

def get_diagnosis(country, age_groups, symptoms):
    """Main function to get diagnosis based on country, age groups, and symptoms."""
    try:
        csp_data, bayes_data = load_data()
        
        # Apply CSP filtering
        filtered_diseases = apply_csp_filter(csp_data, country, age_groups, symptoms)
        
        # Calculate Naive Bayes prediction for filtered diseases
        filtered_predictions = calculate_naive_bayes_prediction(bayes_data, filtered_diseases, symptoms)
        
        # Calculate global Naive Bayes prediction
        global_predictions = calculate_naive_bayes_prediction(bayes_data, None, symptoms)
        
        result = {
            'filtered': {
                'disease': filtered_predictions[0][0] if filtered_predictions else None,
                'probability': filtered_predictions[0][1] if filtered_predictions else 0,
                'method': 'CSP + Naive Bayes',
                'alternatives': filtered_predictions[1:4] if filtered_predictions else []
            },
            'global': {
                'disease': global_predictions[0][0] if global_predictions else None,
                'probability': global_predictions[0][1] if global_predictions else 0,
                'method': 'Naive Bayes',
                'alternatives': global_predictions[1:4] if global_predictions else []
            }
        }
        
        return result
    except Exception as e:
        return {'error': str(e)}

def show_receipt_window(result, csp_data, country, age_groups, symptoms):
    receipt_window = tk.Toplevel(root)
    receipt_window.title("Diagnosis Receipt")
    receipt_window.geometry("800x600")
    
    receipt_text = tk.Text(receipt_window, wrap="word", font=("Courier", 12), bg="white", fg="black")
    receipt_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    if 'error' in result:
        receipt_text.insert(tk.END, f"Error: {result['error']}")
    else:
        result_text = f"Patient Name: {patient_name_var.get()}\n"
        result_text += f"Country: {country}\n"
        result_text += f"Age Groups: {', '.join(age_groups)}\n"
        result_text += f"Symptoms: {', '.join(symptoms)}\n\n"
        
        result_text += f"CSP Filtered Diseases (by symptoms only):\n"
        diseases_by_symptoms = csp_data[csp_data.apply(
            lambda row: any(fuzzy_match(symptom, parse_symptoms(row['Common Symptoms (Easy)']) + parse_symptoms(row['Common Symptoms (Complex)'])) for symptom in symptoms), axis=1
        )]['Disease Name'].unique()
        result_text += "\n".join(diseases_by_symptoms) if len(diseases_by_symptoms) > 0 else "None"

        result_text += f"\n\nCSP Filtered Diseases (by country + symptoms):\n"
        diseases_by_country_symptoms = csp_data[(csp_data['Country'].str.strip().str.lower() == country.strip().lower()) &
                                               (csp_data.apply(lambda row: any(fuzzy_match(symptom, parse_symptoms(row['Common Symptoms (Easy)']) + parse_symptoms(row['Common Symptoms (Complex)'])) for symptom in symptoms), axis=1))]['Disease Name'].unique()
        result_text += "\n".join(diseases_by_country_symptoms) if len(diseases_by_country_symptoms) > 0 else "None"

        result_text += f"\n\nCSP Filtered Diseases (by age group + symptoms):\n"
        diseases_by_age_symptoms = csp_data[(csp_data.apply(lambda row: row['Age Group Most Affected'].strip().lower() in [age.strip().lower() for age in age_groups], axis=1)) &
                                            (csp_data.apply(lambda row: any(fuzzy_match(symptom, parse_symptoms(row['Common Symptoms (Easy)']) + parse_symptoms(row['Common Symptoms (Complex)'])) for symptom in symptoms), axis=1))]['Disease Name'].unique()
        result_text += "\n".join(diseases_by_age_symptoms) if len(diseases_by_age_symptoms) > 0 else "None"

        result_text += f"\n\nDiagnosis Results (Filtered by CSP):\n"
        result_text += f"Most likely disease: {result['filtered']['disease']}\n"
        result_text += f"Confidence: {result['filtered']['probability']:.2%}\n"
        result_text += f"Method: {result['filtered']['method']}\n"
        if result['filtered']['alternatives']:
            result_text += "\nAlternative possibilities (Filtered):\n"
            for disease, prob in result['filtered']['alternatives']:
                result_text += f"- {disease} ({prob:.2%})\n"

        result_text += f"\nDiagnosis Results (Global Naive Bayes):\n"
        result_text += f"Most likely disease: {result['global']['disease']}\n"
        result_text += f"Confidence: {result['global']['probability']:.2%}\n"
        result_text += f"Method: {result['global']['method']}\n"
        if result['global']['alternatives']:
            result_text += "\nAlternative possibilities (Global):\n"
            for disease, prob in result['global']['alternatives']:
                result_text += f"- {disease} ({prob:.2%})\n"

        receipt_text.insert(tk.END, result_text)

    save_button = ttk.Button(receipt_window, text="Save Receipt", command=lambda: save_receipt(receipt_text))
    save_button.pack(pady=10)

def save_receipt(receipt_text):
    receipt_content = receipt_text.get(1.0, tk.END)
    if receipt_content.strip():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(receipt_content)
            messagebox.showinfo("Success", "Receipt saved successfully!")
    else:
        messagebox.showwarning("Warning", "No receipt content to save.")

def run_diagnosis():
    country = country_var.get()
    selected_ages = [age_groups[int(i)] for i in age_indices_var.get().split(',')]
    symptoms = [s.strip().lower() for s in symptoms_var.get().split(',') if s.strip()]
    
    result = get_diagnosis(country, selected_ages, symptoms)
    csp_data, _ = load_data()
    show_receipt_window(result, csp_data, country, selected_ages, symptoms)

# GUI Implementation
root = tk.Tk()
root.title("Health Diagnosis System")
root.geometry("900x700")

# Define custom styles
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12), foreground="blue")
style.configure("TButton", font=("Helvetica", 12, "bold"), background="green", foreground="white")
style.configure("TEntry", font=("Helvetica", 12))
style.configure("TFrame", background="lightblue")
style.configure("TLabelframe", background="lightblue", font=("Helvetica", 14, "bold"))
style.configure("TLabelframe.Label", background="lightblue", font=("Helvetica", 14, "bold"))

# Patient Name Input
patient_name_frame = ttk.LabelFrame(root, text="Patient Name", padding="10")
patient_name_frame.pack(fill="x", padx=10, pady=5)
patient_name_var = tk.StringVar()
patient_name_entry = ttk.Entry(patient_name_frame, textvariable=patient_name_var)
patient_name_entry.pack(fill="x")

# Country Input
country_frame = ttk.LabelFrame(root, text="Country", padding="10")
country_frame.pack(fill="x", padx=10, pady=5)
country_var = tk.StringVar()
country_entry = ttk.Entry(country_frame, textvariable=country_var)
country_entry.pack(fill="x")

# Age Groups Input
age_groups_frame = ttk.LabelFrame(root, text="Age Groups", padding="10")
age_groups_frame.pack(fill="x", padx=10, pady=5)
age_groups = ["early childhood", "adolescents", "adults", "elderly"]
age_groups_label = ttk.Label(age_groups_frame, text="Available age groups: 0: early childhood, 1: adolescents, 2: adults, 3: elderly")
age_groups_label.pack()
age_indices_var = tk.StringVar()
age_indices_entry = ttk.Entry(age_groups_frame, textvariable=age_indices_var)
age_indices_entry.pack(fill="x")

# Symptoms Input
symptoms_frame = ttk.LabelFrame(root, text="Symptoms", padding="10")
symptoms_frame.pack(fill="x", padx=10, pady=5)
symptoms_var = tk.StringVar()
symptoms_entry = ttk.Entry(symptoms_frame, textvariable=symptoms_var)
symptoms_entry.pack(fill="x")

# Run Diagnosis Button
run_button = ttk.Button(root, text="Run Diagnosis", command=run_diagnosis)
run_button.pack(pady=10)

root.mainloop()
