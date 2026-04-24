# views/__init__.py - Central export for all application view frames
from views.dashboard import DashboardFrame
from views.add_expense import AddExpenseFrame
from views.browse import ViewExpensesFrame
from views.monthly import MonthlySummaryFrame
from views.budget import SetBudgetFrame
from views.export_csv import ExportCSVFrame

__all__ = [
    'DashboardFrame',
    'AddExpenseFrame', 
    'ViewExpensesFrame',
    'MonthlySummaryFrame',
    'SetBudgetFrame',
    'ExportCSVFrame'
]
