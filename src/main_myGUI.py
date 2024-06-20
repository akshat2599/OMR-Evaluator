import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
from PIL import Image, ImageTk
import pandas as pd
import fitz
import base64
from PIL import Image
import io
from io import BytesIO


def convert_pdf_to_images(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    images = []
    # Iterate through each page in the PDF
    for page_number in range(len(doc)):
        # Load the page as a pixmap
        pixmap = doc.load_page(page_number).get_pixmap()
        # Convert the pixmap to a PIL Image
        img = Image.open(io.BytesIO(pixmap.tobytes("jpg")))
        images.append(img)
    return images


def replace_pdfs_with_images(folder_path):
    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            # Convert the PDF to images
            images = convert_pdf_to_images(pdf_path)
            # Save each image as JPEG with the same name
            for i, image in enumerate(images):
                image.save(os.path.splitext(pdf_path)[0] + f"_{i}.jpg", "JPEG")
            # Remove the original PDF file
            os.remove(pdf_path)


def evaluate_student_marks(student_answers_file, answer_file_name):
    # Load the DataFrames with student answers and answer key
    df_student = pd.read_csv(student_answers_file)
    df_answer_key = df_student[df_student["Source File"] == answer_file_name]
    df_student = df_student[df_student["Source File"] != answer_file_name].reset_index(drop="index")
    # Convert columns to object type to ensure compatibility for merging
    df_student.iloc[:, 7:] = df_student.iloc[:, 7:].astype(str)
    df_answer_key.iloc[:, 7:] = df_answer_key.iloc[:, 7:].astype(str)

    # Calculate the total number of questions
    total_questions = len(df_student.columns) - 7  # Exclude non-question columns
    # print(total_questions)
    # Initialize a list to store marks for each question

    # Iterate over each question and check if the answer matches the key
    marks = []
    # print(df_student)
    for j in range(len(df_student)):
        marks_per_question = []
        df = df_student[df_student.index == j]
        # print(df)
        for i in range(1, total_questions + 1):
            question_col = f'Q{i}'
            if df[question_col].iloc[0] != "nan":
                marks_per_question.append(int(df[question_col].iloc[0] == df_answer_key[question_col].iloc[0]))
        # Calculate total marks obtained by each student
        total_marks_obtained = pd.DataFrame(marks_per_question).reset_index()[0].sum()
        marks.append(total_marks_obtained)
    print(marks)
    df_student["marks"] = marks
    return marks, df_student


def run_command():
    # mobile_number = mobile_number_entry.get()
    # test_name = test_name_var.get()
    #
    # # Validate inputs
    # if not mobile_number or not test_name:
    #     messagebox.showerror("Error", "Please enter mobile number and select test name.")
    #     return
    #
    # # Print mobile number and test name
    # print("Mobile Number:", mobile_number)
    # print("Test Name:", test_name)

    input_path = "./test/end-to-end/testing/Input"
    output_path = "./test/end-to-end/testing/Output"
    variant = "150"
    replace_pdfs_with_images(input_path)
    command = f"python src/main.py {input_path} {output_path} --variant '{variant}'"
    try:
        subprocess.run(command, shell=True, check=True)
        # messagebox.showinfo("Success", "OMR submitted successfully!")
        # Delete input file after successful run
        # for file in os.listdir(input_path):
        #     file_path = os.path.join(input_path, file)
        #     os.remove(file_path)
        # messagebox.showinfo("Success", "Input file deleted successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"OMR submission failed: {e}")
    total_marks, evaluated_sheet_df = evaluate_student_marks('./test/end-to-end/testing/Output/results.csv',
                                                             "Hindi.jpg")
    evaluated_sheet_df.to_csv("./test/end-to-end/testing/Output/evaluatedSheet.csv")


run_command()
