import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
from PIL import Image, ImageTk
import pandas as pd

def evaluate_student_marks(student_answers_file, answer_key_file):
    # Load the DataFrames with student answers and answer key
    df_student = pd.read_csv(student_answers_file)
    df_answer_key = pd.read_csv(answer_key_file)

    # Convert columns to object type to ensure compatibility for merging
    df_student.iloc[:, 7:] = df_student.iloc[:, 7:].astype(str)
    df_answer_key.iloc[:, 2:] = df_answer_key.iloc[:, 2:].astype(str)

    # Calculate the total number of questions
    total_questions = len(df_student.columns) - 7  # Exclude non-question columns
    print(total_questions)
    # Initialize a list to store marks for each question
    marks_per_question = []

    # Iterate over each question and check if the answer matches the key
    for i in range(1, total_questions):
        question_col = f'Q{i}'
        if df_student[question_col].iloc[0] != "nan":
            marks_per_question.append((df_student[question_col] == df_answer_key[question_col]).astype(int))

    # Calculate total marks obtained by each student
    total_marks_obtained = pd.DataFrame(marks_per_question).reset_index()[0].sum()

    return total_marks_obtained

def run_command(mobile_number_entry, test_name_var):
    total_marks_label.config(text=f"Total Marks: - / 150")
    mobile_number = mobile_number_entry.get()
    test_name = test_name_var.get()

    # Validate inputs
    if not mobile_number or not test_name:
        messagebox.showerror("Error", "Please enter mobile number and select test name.")
        return

    # Print mobile number and test name
    print("Mobile Number:", mobile_number)
    print("Test Name:", test_name)

    input_path = "./test/end-to-end/testing/Input"
    output_path = "./test/end-to-end/testing/Output"
    variant = "150"
    command = f"python src/main.py {input_path} {output_path} --variant '{variant}'"
    try:
        subprocess.run(command, shell=True, check=True)
        # messagebox.showinfo("Success", "OMR submitted successfully!")
        # Delete input file after successful run
        for file in os.listdir(input_path):
            file_path = os.path.join(input_path, file)
            os.remove(file_path)
        # messagebox.showinfo("Success", "Input file deleted successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"OMR submission failed: {e}")
    total_marks = evaluate_student_marks('./test/end-to-end/testing/Output/results.csv',
                                         './test/end-to-end/150q-core/output/keys.csv')
    total_marks_label.config(text=f"Total Marks: {total_marks} / 150")

def select_images():
    file_paths = filedialog.askopenfilenames(title="Select Images",
                                             filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")))
    if file_paths:
        input_path = "./test/end-to-end/testing/Input"
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            destination_path = os.path.join(input_path, filename)
            subprocess.run(["cp", file_path, destination_path])
        # messagebox.showinfo("Success", "Images uploaded successfully.")

# GUI setup
root = tk.Tk()
root.title("OMR Submission")

# Custom colors
bg_color = "#CAF4FF"  # Light gray
button_bg_color = "#57A6A1"  # Blue
button_fg_color = "black"  # White

# Load the background image
background_image = Image.open("hand-7702627_1280.jpg")  # Replace with your image path
background_photo = ImageTk.PhotoImage(background_image)

# Create a canvas widget to place the background image
canvas = tk.Canvas(root, width=1200, height=800)
canvas.pack(fill="both", expand=True)

# Add the background image to the canvas
canvas.create_image(0, 0, image=background_photo, anchor="nw")

# Create a frame for other widgets on top of the canvas
frame = tk.Frame(canvas, bg=bg_color)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Configure style
style = ttk.Style()
style.configure("TButton", background=button_bg_color, foreground=button_fg_color)

# Label and Entry for mobile number
mobile_number_label = tk.Label(frame, text="Mobile Number:", bg=bg_color)
mobile_number_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
mobile_number_entry = tk.Entry(frame)
mobile_number_entry.grid(row=0, column=1, padx=5, pady=5)

# Label and Combobox for test name
test_name_label = tk.Label(frame, text="Test Name:", bg=bg_color)
test_name_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
test_names = ["Test 1", "Test 2", "Test 3"]  # Example list of test names
test_name_var = tk.StringVar(root)
test_name_var.set(test_names[0])  # Set the default test name
test_name_combobox = ttk.Combobox(frame, textvariable=test_name_var, values=test_names, state="readonly")
test_name_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Button to select images and upload
upload_button = ttk.Button(frame, text="Upload Images", command=select_images)
upload_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

# Button to submit OMR
submit_button = ttk.Button(frame, text="Submit Your OMR",
                           command=lambda: run_command(mobile_number_entry, test_name_var))
submit_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

# Label to display total marks
total_marks_label = tk.Label(frame, text="Total Marks: - / 150", bg=bg_color, fg="red")
total_marks_label.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

root.mainloop()
