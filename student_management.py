
import json
import csv
import os

DATA_FILE = "students.json"
CSV_FILE = "students.csv"

SUBJECTS = ["English", "Maths", "Science", "Computer", "Hindi"]


# Load student records from JSON file
def load_students():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            students = json.load(file)

    except json.JSONDecodeError:
        raise ValueError(
            "JSON file is invalid. Please repair students.json first."
        )
    except OSError as error:
        raise ValueError(f"Cannot read data file: {error}")

    if not isinstance(students, list):
        raise ValueError("Invalid data structure. Expected a list.")

    for student in students:
        if not isinstance(student, dict):
            raise ValueError("Invalid student record found.")

        if not all(key in student for key in
                   ["roll", "name", "course", "marks"]):
            raise ValueError("A student record is incomplete.")

        if (not isinstance(student["roll"], str)
                or not student["roll"].strip()
                or not isinstance(student["name"], str)
                or not student["name"].strip()
                or not isinstance(student["course"], str)
                or not student["course"].strip()):
            raise ValueError("Invalid student details in JSON.")

        if not isinstance(student["marks"], list):
            raise ValueError("Marks must be stored as a list.")

        if len(student["marks"]) != len(SUBJECTS):
            raise ValueError("Incorrect number of subject marks.")

        for mark in student["marks"]:
            if (isinstance(mark, bool)
                    or not isinstance(mark, (int, float))
                    or not 0 <= mark <= 100):
                raise ValueError("Invalid marks found in JSON.")

    rolls = [student["roll"] for student in students]

    if len(rolls) != len(set(rolls)):
        raise ValueError("Duplicate roll numbers found in JSON.")

    return students


# Save all student records permanently
def save_students(students):
    temp_file = DATA_FILE + ".tmp"

    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(students, file, indent=4)

        os.replace(temp_file, DATA_FILE)

    except OSError as error:
        print("Error saving records:", error)

        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass

        return False

    return True


# Input validation for marks
def input_marks():
    marks = []

    for subject in SUBJECTS:
        while True:
            try:
                mark = float(input(f"Enter {subject} marks (0-100): "))

                if not 0 <= mark <= 100:
                    print("Marks must be between 0 and 100.")
                    continue

                marks.append(mark)
                break

            except ValueError:
                print("Please enter a valid number.")

    return marks


# Calculate total marks
def calculate_total(marks):
    return sum(marks)


# Calculate average marks
def calculate_average(marks):
    return sum(marks) / len(marks)


# Check pass or fail
def get_status(marks):
    if all(mark >= 33 for mark in marks):
        return "PASS"
    return "FAIL"


# Find a student using roll number
def find_student(students, roll):
    for student in students:
        if student["roll"].casefold() == roll.casefold():
            return student

    return None


# Display one student's details
def display_student(student):
    print("\n---------- STUDENT DETAILS ----------")
    print("Roll Number:", student["roll"])
    print("Name:", student["name"])
    print("Course:", student["course"])

    for subject, mark in zip(SUBJECTS, student["marks"]):
        print(f"{subject}: {mark:g}")

    total = calculate_total(student["marks"])
    average = calculate_average(student["marks"])
    status = get_status(student["marks"])

    print("Total Marks:", f"{total:g}", "/ 500")
    print("Average:", f"{average:.2f}")
    print("Result:", status)
    print("-------------------------------------")


# Add a new student
def add_student(students):
    roll = input("Enter roll number: ").strip()

    if not roll:
        print("Roll number cannot be empty.")
        return

    if find_student(students, roll):
        print("This roll number already exists!")
        return

    name = input("Enter student name: ").strip()
    course = input("Enter course name: ").strip()

    if not name or not course:
        print("Name and course cannot be empty.")
        return

    marks = input_marks()

    student = {
        "roll": roll,
        "name": name,
        "course": course,
        "marks": marks
    }

    students.append(student)

    if save_students(students):
        print("Student added successfully!")
    else:
        students.remove(student)
        print("Student was not added because saving failed.")


# Display all students
def display_all_students(students):
    if not students:
        print("No student records found.")
        return

    for student in students:
        display_student(student)


# Search student by roll number
def search_student(students):
    roll = input("Enter roll number to search: ").strip()
    student = find_student(students, roll)

    if student:
        display_student(student)
    else:
        print("Student not found.")


# Update student details and marks
def update_student(students):
    roll = input("Enter roll number to update: ").strip()
    student = find_student(students, roll)

    if not student:
        print("Student not found.")
        return

    print("Press Enter to keep the existing value.")

    name = input(f"New name [{student['name']}]: ").strip()
    course = input(f"New course [{student['course']}]: ").strip()

    old_name = student["name"]
    old_course = student["course"]
    old_marks = student["marks"][:]

    if name:
        student["name"] = name

    if course:
        student["course"] = course

    change_marks = input("Update marks too? (y/n): ").strip().lower()

    if change_marks == "y":
        student["marks"] = input_marks()

    if save_students(students):
        print("Student updated successfully!")
    else:
        student["name"] = old_name
        student["course"] = old_course
        student["marks"] = old_marks
        print("Update was not saved.")


# Delete a student
def delete_student(students):
    roll = input("Enter roll number to delete: ").strip()
    student = find_student(students, roll)

    if not student:
        print("Student not found.")
        return

    confirm = input(
        f"Delete {student['name']}? (y/n): "
    ).strip().lower()

    if confirm == "y":
        index = students.index(student)
        students.pop(index)

        if save_students(students):
            print("Student deleted successfully!")
        else:
            students.insert(index, student)
            print("Deletion was not saved.")
    else:
        print("Deletion cancelled.")


# Find the student with the highest average
def highest_average(students):
    if not students:
        print("No student records available.")
        return

    best_student = max(
        students,
        key=lambda student: calculate_average(student["marks"])
    )

    print("Student with the highest average:")
    display_student(best_student)


# Export records to CSV
def export_csv(students):
    try:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow([
                "Roll Number", "Name", "Course",
                *SUBJECTS, "Total", "Average", "Result"
            ])

            for student in students:
                marks = student["marks"]

                writer.writerow([
                    student["roll"],
                    student["name"],
                    student["course"],
                    *marks,
                    calculate_total(marks),
                    round(calculate_average(marks), 2),
                    get_status(marks)
                ])

        print(f"Records exported successfully to {CSV_FILE}")

    except OSError as error:
        print("Error exporting CSV:", error)


# Main menu
def main():
    try:
        students = load_students()
    except ValueError as error:
        print("DATA ERROR:", error)
        print("No changes have been made to the original file.")
        return

    while True:
        print("\n====================================")
        print("   STUDENT RECORD MANAGEMENT SYSTEM")
        print("====================================")
        print("1. Add Student")
        print("2. Display All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Calculate Total, Average and Result")
        print("7. Find Highest Average")
        print("8. Export Records to CSV")
        print("9. Exit")
        print("====================================")

        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            add_student(students)

        elif choice == "2":
            display_all_students(students)

        elif choice == "3":
            search_student(students)

        elif choice == "4":
            update_student(students)

        elif choice == "5":
            delete_student(students)

        elif choice == "6":
            search_student(students)

        elif choice == "7":
            highest_average(students)

        elif choice == "8":
            export_csv(students)

        elif choice == "9":
            print("Thank you for using Student Record Management System!")
            break

        else:
            print("Invalid choice. Please select 1-9.")


if __name__ == "__main__":
    main()
