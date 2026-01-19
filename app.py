# app.py
# Real Estate Investment Calculator for Fourplexes and Similar Properties
# This is a Streamlit web app. To run it locally: pip install streamlit numpy-financial
# Then: streamlit run app.py
# To deploy: Create a GitHub repo, add this file as app.py, add requirements.txt with: streamlit\nnumpy-financial
# Then deploy to Streamlit Cloud (streamlit.io) by connecting your GitHub repo.

import streamlit as st
import numpy_financial as npf  # For financial calculations like PMT

st.title("Real Estate Investment Calculator")
st.markdown("""
This app helps you evaluate real estate investments, such as fourplexes. It calculates mortgage payments, cash flow, cap rate, cash-on-cash return, and more.
Enter the details below and click 'Calculate' to see the results.
""")

# Sidebar for inputs
with st.sidebar:
    st.header("Property Details")
    purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, value=400000.0, step=1000.0)
    num_units = st.number_input("Number of Units", min_value=1, value=4, step=1)
    
    st.header("Financing")
    down_payment_perc = st.slider("Down Payment (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.5)
    down_payment = (down_payment_perc / 100) * purchase_price
    st.write(f"Down Payment Amount: ${down_payment:,.2f}")
    interest_rate = st.slider("Annual Interest Rate (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1) / 100
    loan_term_years = st.number_input("Loan Term (Years)", min_value=1, value=30, step=1)
    
    st.header("Income")
    monthly_rent_per_unit = st.number_input("Monthly Rent per Unit ($)", min_value=0.0, value=1200.0, step=50.0)
    other_annual_income = st.number_input("Other Annual Income ($)", min_value=0.0, value=0.0, step=100.0)
    
    st.header("Expenses")
    annual_property_taxes = st.number_input("Annual Property Taxes ($)", min_value=0.0, value=5000.0, step=100.0)
    annual_insurance = st.number_input("Annual Insurance ($)", min_value=0.0, value=2000.0, step=100.0)
    maintenance_perc = st.slider("Maintenance (% of Gross Rent)", min_value=0.0, max_value=50.0, value=10.0, step=0.5) / 100
    vacancy_rate_perc = st.slider("Vacancy Rate (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5) / 100
    management_fee_perc = st.slider("Management Fee (% of Gross Rent)", min_value=0.0, max_value=50.0, value=8.0, step=0.5) / 100
    annual_utilities = st.number_input("Annual Utilities (if paid by owner) ($)", min_value=0.0, value=0.0, step=100.0)
    other_annual_expenses = st.number_input("Other Annual Expenses ($)", min_value=0.0, value=0.0, step=100.0)

# Calculations
if st.button("Calculate"):
    # Financing Calculations
    loan_amount = purchase_price - down_payment
    monthly_interest_rate = interest_rate / 12
    num_payments = loan_term_years * 12
    if interest_rate > 0:
        monthly_mortgage = -npf.pmt(monthly_interest_rate, num_payments, loan_amount)
    else:
        monthly_mortgage = loan_amount / num_payments
    annual_mortgage = monthly_mortgage * 12
    
    # Income Calculations
    gross_monthly_rent = monthly_rent_per_unit * num_units
    gross_annual_rent = gross_monthly_rent * 12
    effective_annual_rent = gross_annual_rent * (1 - vacancy_rate_perc)
    total_annual_income = effective_annual_rent + other_annual_income
    
    # Expense Calculations
    annual_maintenance = maintenance_perc * gross_annual_rent
    annual_management = management_fee_perc * gross_annual_rent
    total_annual_expenses = (
        annual_property_taxes +
        annual_insurance +
        annual_maintenance +
        annual_management +
        annual_utilities +
        other_annual_expenses
    )
    
    # Key Metrics
    noi = total_annual_income - total_annual_expenses  # Net Operating Income
    annual_cash_flow = noi - annual_mortgage
    monthly_cash_flow = annual_cash_flow / 12
    
    cap_rate = (noi / purchase_price) * 100 if purchase_price > 0 else 0
    cash_on_cash_return = (annual_cash_flow / down_payment) * 100 if down_payment > 0 else 0
    
    # Display Results
    st.header("Results")
    
    st.subheader("Financing Summary")
    st.write(f"Loan Amount: ${loan_amount:,.2f}")
    st.write(f"Monthly Mortgage Payment: ${monthly_mortgage:,.2f}")
    st.write(f"Annual Mortgage Payments: ${annual_mortgage:,.2f}")
    
    st.subheader("Income Summary")
    st.write(f"Gross Annual Rent: ${gross_annual_rent:,.2f}")
    st.write(f"Effective Annual Rent (after vacancy): ${effective_annual_rent:,.2f}")
    st.write(f"Total Annual Income: ${total_annual_income:,.2f}")
    
    st.subheader("Expenses Summary")
    st.write(f"Annual Maintenance: ${annual_maintenance:,.2f}")
    st.write(f"Annual Management Fees: ${annual_management:,.2f}")
    st.write(f"Total Annual Expenses: ${total_annual_expenses:,.2f}")
    
    st.subheader("Key Investment Metrics")
    st.write(f"Net Operating Income (NOI): ${noi:,.2f}")
    st.write(f"Annual Cash Flow: ${annual_cash_flow:,.2f}")
    st.write(f"Monthly Cash Flow: ${monthly_cash_flow:,.2f}")
    st.write(f"Cap Rate: {cap_rate:.2f}%")
    st.write(f"Cash-on-Cash Return: {cash_on_cash_return:.2f}%")
    
    # Additional Features: Simple Break-Even Analysis
    st.subheader("Break-Even Analysis")
    break_even_occupancy = (total_annual_expenses + annual_mortgage) / gross_annual_rent if gross_annual_rent > 0 else 0
    st.write(f"Break-Even Occupancy Rate: {break_even_occupancy * 100:.2f}%")
    
    # Amortization Preview (first year)
    st.subheader("First Year Amortization Preview")
    balance = loan_amount
    total_interest_first_year = 0
    total_principal_first_year = 0
    for month in range(1, 13):
        interest = balance * monthly_interest_rate
        principal = monthly_mortgage - interest
        balance -= principal
        total_interest_first_year += interest
        total_principal_first_year += principal
    
    st.write(f"Total Interest Paid in First Year: ${total_interest_first_year:,.2f}")
    st.write(f"Total Principal Paid in First Year: ${total_principal_first_year:,.2f}")
    st.write(f"Remaining Balance After First Year: ${balance:,.2f}")

st.markdown("""
### Notes:
- This is a basic calculator. Consult a financial advisor for professional advice.
- Assumptions: Expenses are annual; vacancy reduces rent proportionally.
- You can extend this app by adding more features like IRR calculation using numpy-financial.irr().
""")