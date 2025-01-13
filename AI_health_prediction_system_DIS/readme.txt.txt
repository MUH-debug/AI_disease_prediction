Health Diagnosis System - README

Project Overview

This project is a health diagnosis system that utilizes a combination of Constraint Satisfaction Problem (CSP) filtering and Naive Bayes classification to predict diseases based on input symptoms, country, and age group. It employs fuzzy matching techniques to account for variations in symptom input and uses structured datasets for both Bayesian predictions and CSP filtering. The system features a user-friendly GUI built with Tkinter, allowing users to input patient details and symptoms, and receive a diagnosis with alternative possibilities.

How It Works

The system operates by processing the following inputs from the user:

Patient Name: The name of the patient (for record-keeping purposes).

Country: The country of the patient (used to filter relevant diseases).

Age Groups: The age group(s) most applicable to the patient (e.g., early childhood, adolescents, adults, elderly).

Symptoms: A list of symptoms the patient is experiencing.

The system works in two main stages:

CSP Filtering: The system filters diseases based on country, age group, and symptoms using a Constraint Satisfaction Problem (CSP) approach. This helps narrow down possible diseases based on matching criteria.

Naive Bayes Prediction: The filtered diseases are then passed through a Naive Bayes classifier to calculate the probability of each disease based on the provided symptoms. The result includes the most likely disease along with alternative diagnoses, sorted by probability.

Additionally, fuzzy logic is used to account for small variations in symptom input, ensuring that even partial matches are considered.

Core Components

parse_symptoms: Converts a comma-separated list of symptoms into a list of cleaned, lowercase symptoms.

load_data: Loads data from CSV files containing the disease information for the CSP filtering and Bayesian analysis.

fuzzy_match: Uses the fuzzywuzzy library to find partial matches between input symptoms and the symptoms associated with each disease.

apply_csp_filter: Filters diseases based on the patient's country, age group, and symptoms using a Constraint Satisfaction Problem approach.

calculate_naive_bayes_prediction: Uses a Naive Bayes classifier to predict diseases based on the symptoms and the filtered diseases.

get_diagnosis: Main function that combines both the CSP filtering and Naive Bayes predictions to return a list of diagnoses along with their probabilities.

show_receipt_window: Displays the diagnosis results in a formatted receipt window in the GUI.

save_receipt: Allows the user to save the diagnosis results as a text file.

run_diagnosis: Orchestrates the entire process based on user input from the GUI.

Project Requirements

To run this project, you need to have the following Python libraries installed:

pandas

numpy

sklearn

constraint

fuzzywuzzy

tkinter (typically included with Python installations)

You can install the required libraries using pip:

pip install pandas numpy scikit-learn python-constraint fuzzywuzzy

GUI Overview

The GUI is designed with Tkinter and provides the following input fields:

Patient Name: A text box for entering the patient's name.

Country: A text box for entering the patient's country.

Age Groups: A text box for entering age group indices (e.g., 0,1 for "early childhood" and "adolescents").

Symptoms: A text box for entering symptoms as a comma-separated list.

Once the user enters all necessary information, they can click the "Run Diagnosis" button, which triggers the diagnostic process. The results are displayed in a new window, showing the predicted disease(s), their probabilities, and alternative diagnoses.

The system also allows the user to save the diagnosis results as a text file.

How to Use

Clone the repository or download the project files.

Ensure that the necessary data files (data2.csv and structured_bayesian_data.csv) are in the correct directory.

Run the Python script:

python diagnosis_system.py

Enter the required information into the GUI (patient name, country, age groups, and symptoms).

Click on the "Run Diagnosis" button to get the diagnosis.

Review the results in the new window, and if desired, save the diagnosis by clicking the "Save Receipt" button.

Conclusion

This health diagnosis system integrates AI-based techniques (CSP filtering and Naive Bayes) with a user-friendly GUI to provide accurate disease predictions based on symptoms, country, and age group. It's designed to help users quickly get an idea of potential diseases they may be dealing with, based on the input symptoms.