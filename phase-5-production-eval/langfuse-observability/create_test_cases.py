"""
create_test_cases.py — One-time script to generate banking_test_cases.xlsx
Run once: python3 create_test_cases.py
"""
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

cases = [
    # Category, Question, MustContain, MustNotContain, Notes
    ("account_info",    "What documents do I need to open a savings account?",            "identity,address",           "credit card",         "Basic account opening query"),
    ("account_info",    "What is the minimum balance required for a savings account?",    "minimum,balance",            "",                    "Balance policy question"),
    ("account_info",    "Can I have multiple savings accounts at SecureBank?",            "",                           "",                    "Policy clarification"),
    ("transactions",    "How do I transfer money to another bank account?",               "transfer",                   "",                    "Transfer instruction"),
    ("transactions",    "What are the daily transaction limits for online transfers?",     "limit",                      "",                    "Limit policy question"),
    ("transactions",    "How long does an international wire transfer take?",              "business day,working day",   "",                    "International transfer timing"),
    ("loans",           "What is the interest rate for a personal loan?",                  "interest,rate",              "",                    "Loan rate query"),
    ("loans",           "How do I apply for a home loan?",                                 "apply,loan",                 "",                    "Home loan application"),
    ("loans",           "What is the maximum loan amount I can borrow?",                   "income,eligib",              "",                    "Loan eligibility"),
    ("security",        "My debit card was stolen. What should I do immediately?",         "block,cancel,report",        "",                    "Security emergency — urgent"),
    ("security",        "How do I enable two-factor authentication on my account?",        "two-factor,2fa,authenticat", "",                    "2FA setup"),
    ("security",        "I received a suspicious email asking for my banking password.",   "phishing,scam,do not",       "provide,give,share",  "Phishing detection — must warn"),
    ("fees",            "What are the charges for a failed transaction?",                  "fee,charge",                 "",                    "Fee query"),
    ("fees",            "Is there a monthly maintenance fee for my current account?",      "fee,charge,maintenance",     "",                    "Account fee query"),
    ("out_of_scope",    "What is the best restaurant near my bank branch?",                "outside,scope,banking",      "",                    "Out-of-scope — should decline"),
    ("out_of_scope",    "Can you help me write a cover letter for a job application?",     "outside,scope,banking",      "",                    "Out-of-scope — should decline"),
    ("account_info",    "How do I update my registered mobile number?",                    "update,mobile,contact",      "",                    "Contact update query"),
    ("transactions",    "Can I cancel a pending transaction?",                             "pending,cancel",             "",                    "Cancellation query"),
    ("loans",           "What documents are needed for a car loan application?",           "document,income,identity",   "",                    "Car loan documents"),
    ("security",        "How do I reset my online banking password?",                      "reset,password",             "",                    "Password reset"),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Test Cases"

headers = ["CaseID", "Category", "Question", "MustContain", "MustNotContain", "Notes"]
header_fill = PatternFill(start_color="1C1C21", end_color="1C1C21", fill_type="solid")
header_font = Font(bold=True, color="F7A06A")

for col_idx, header in enumerate(headers, start=1):
    cell = ws.cell(row=1, column=col_idx, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

for row_idx, (category, question, must_contain, must_not_contain, notes) in enumerate(cases, start=2):
    ws.cell(row=row_idx, column=1, value=f"TC{row_idx-1:02d}")
    ws.cell(row=row_idx, column=2, value=category)
    ws.cell(row=row_idx, column=3, value=question)
    ws.cell(row=row_idx, column=4, value=must_contain)
    ws.cell(row=row_idx, column=5, value=must_not_contain)
    ws.cell(row=row_idx, column=6, value=notes)

ws.column_dimensions["A"].width = 8
ws.column_dimensions["B"].width = 18
ws.column_dimensions["C"].width = 60
ws.column_dimensions["D"].width = 30
ws.column_dimensions["E"].width = 25
ws.column_dimensions["F"].width = 40

out_path = os.path.join(SCRIPT_DIR, "banking_test_cases.xlsx")
wb.save(out_path)
print(f"Created: {out_path} ({len(cases)} test cases)")
