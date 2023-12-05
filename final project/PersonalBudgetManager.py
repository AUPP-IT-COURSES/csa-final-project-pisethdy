import PySimpleGUI as sg
from datetime import datetime

# Global variables to store expense data and cumulative totals
expenses = []
total_balance = 0
total_income = 0
total_spending = 0

def handleRemoveExpense(main_window):
    # Prepare data for layout
    global total_balance, total_income, total_spending
    data = []
    for i, expense in enumerate(expenses, start=1):
        amount_prefix = '+' if expense['amount'] >= 0 else ''
        data.append([f"{i}", expense['name'], f"{amount_prefix}${abs(expense['amount']):.2f}", expense['category'], f"{expense['date']}"])

    # Create the layout with checkboxes for each expense
    layout = [
        [sg.Text("Select expenses to remove:")],
        [sg.Table(values=data, headings=['#', 'Name', 'Amount', 'Category', 'Date'], auto_size_columns=False,
                  col_widths=[4, 15, 15, 20, 20], justification='center', display_row_numbers=False, num_rows=min(25, len(data)), key='table')],
        [sg.Button("Remove Selected"), sg.Button("Back")]
    ]

    # Set up the window
    window = sg.Window("Remove Expenses", layout)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Back"):
            break
        elif event == "Remove Selected":
            # Get selected rows from the table (returned as strings)
            selected_rows_str = values['table']

            # Convert selected rows to integers
            selected_rows = [int(index) for index in selected_rows_str]

            # Remove selected expenses
            for index in selected_rows:
                if 0 <= index < len(expenses):
                    expense = expenses[index]
                    total_balance -= expense['amount']
                    if expense['amount'] >= 0:
                        total_income -= expense['amount']
                    else:
                        total_spending -= expense['amount']
                    expenses.remove(expense)

            sg.popup("Selected expenses removed successfully.")
            break

    window.close()
    main_window.bring_to_front()



def addTransaction(is_spending):
    title = "Add Spending" if is_spending else "Add Income"
    button_text = "Add Spending" if is_spending else "Add Income"
    key_prefix = "spending" if is_spending else "income"
    default_category = "Income" if not is_spending else None  # Set default category to "Income" for income transactions

    categories = ['Food', 'Rent', 'Utilities', 'Transportation', 'Entertainment', 'Miscellaneous', 'Other']

    layout = [
        [sg.Text(f"Enter the name of the {key_prefix}:"), sg.InputText(key=f"{key_prefix}_name", size=(19, 1))],
        [sg.Text(f"How much was this {key_prefix}? (in USD)"), sg.InputText(key=f"{key_prefix}_amount", size=(13, 1))],
        [sg.Text("Select the category:"), sg.DropDown(categories if is_spending else [default_category], key=f"{key_prefix}_category", size=(13, 1))],
        [sg.Text("Date (YYYY-MM-DD)"), sg.InputText(default_text=datetime.now().strftime("%Y-%m-%d"), key=f"{key_prefix}_date", size=(14, 1))],
        [sg.Button(button_text), sg.Button("Back")]
    ]

    window = sg.Window(title, layout)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Back"):
            break

        try:
            name = values[f"{key_prefix}_name"]
            amountToAdd = float(values[f"{key_prefix}_amount"]) * (-1 if is_spending else 1)
            category = "Income" if not is_spending else values[f"{key_prefix}_category"]
            date = datetime.strptime(values[f"{key_prefix}_date"], "%Y-%m-%d").date()

            global total_balance, total_income, total_spending
            expenses.append({'name': name, 'amount': amountToAdd, 'category': category, 'date': date})

            total_balance += amountToAdd
            if amountToAdd >= 0:
                total_income += amountToAdd
            else:
                total_spending += amountToAdd

            sg.popup(f"{title} added successfully.")

            break
        except ValueError:
            sg.popup_error("Invalid input. Please enter again")

    window.close()


def handleListExpenses(main_window):
    all_categories = ['All', 'Income', 'Food', 'Rent', 'Utilities', 'Transportation', 'Entertainment', 'Miscellaneous', 'Other']

    # Initially, show all expenses
    filtered_expenses = expenses

    # Prepare data for layout
    data = []
    for i, expense in enumerate(filtered_expenses, start=1):
        amount_prefix = '+' if expense['amount'] >= 0 else ''
        data.append(
            [f"#{i}", expense['name'], f"{amount_prefix}${abs(expense['amount']):.2f}", expense['category'],
             f"{expense['date']}"])

    # Create the initial layout
    layout = [
        [sg.Text("Select a category:"),
         sg.DropDown(all_categories, default_value='All', key='selected_category')],
        [sg.Button("Filter"), sg.Button("Back")],
        [sg.Table(values=data, headings=['#', 'Name', 'Amount', 'Category', 'Date'],
                  auto_size_columns=False, col_widths=[4, 15, 15, 20, 20], justification='center',
                  display_row_numbers=False, num_rows=25, key='table')]
    ]

    # Set up the initial window
    window = sg.Window("List of Expenses", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "Back":
            break
        elif event == "Filter":
            selected_category = values["selected_category"]
            if selected_category == 'All':
                filtered_expenses = expenses
            else:
                filtered_expenses = [expense for expense in expenses if expense['category'] == selected_category]

            # Prepare data for layout
            data = []
            for i, expense in enumerate(filtered_expenses, start=1):
                amount_prefix = '+' if expense['amount'] >= 0 else ''
                data.append(
                    [f"#{i}", expense['name'], f"{amount_prefix}${abs(expense['amount']):.2f}", expense['category'],
                     f"{expense['date']}"])

            # Update the table with the filtered data
            window['table'].update(values=data)

    window.close()
    main_window.bring_to_front()


def main():
    layout = [
        [sg.Text(f"Total Balance: ${total_balance:.2f}\nTotal Income: {'+' if total_income > 0 else ''}${abs(total_income):.2f}\nTotal Spending: ${total_spending:.2f}", key='total')],
        [sg.Text("Please choose from one of the following options:")],
        [sg.Button("Add A New Transaction"), sg.Button("Remove Expense"), sg.Button("List All Expenses"), sg.Button("Exit")]
    ]

    window = sg.Window("Personal Budget Manager", layout)

    while True:
        event, _ = window.read()

        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event == "Add A New Transaction":
            handleAddTransactionMenu(window)
        elif event == "Remove Expense":
            handleRemoveExpense(window)
        elif event == "List All Expenses":
            handleListExpenses(window)

        # Update the total values on the main page
        window['total'].update(f"Total Balance: {'-' if total_balance < 0 else ''}${abs(total_balance):.2f}\nTotal Income: {'+' if total_income > 0 else ''}${abs(total_income):.2f}\nTotal Spending: {'-' if total_spending < 0 else ''}${abs(total_spending):.2f}")

    window.close()


def handleAddTransactionMenu(main_window):
    layout = [
        [sg.Text("Please choose the type of transaction:")],
        [sg.Button("Add Income"), sg.Button("Add Spending"), sg.Button("Back")]
    ]

    add_transaction_window = sg.Window("Add Transaction", layout)

    while True:
        event, values = add_transaction_window.read()

        if event in (sg.WINDOW_CLOSED, "Back"):
            break
        elif event == "Add Income":
            addTransaction(is_spending=False)
        elif event == "Add Spending":
            addTransaction(is_spending=True)

    add_transaction_window.close()
    main_window.bring_to_front()


if __name__ == "__main__":
    main()
