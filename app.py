# app.py - Enhanced Real Estate Investment Calculator (Updated with Breakeven Price & Property Name in Exports)
import streamlit as st
import numpy_financial as npf
import numpy as np
import plotly.express as px
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
import requests

# Session state initialization
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'deep_dive_results' not in st.session_state:
    st.session_state.deep_dive_results = {}

st.set_page_config(page_title="Fourplex Investment Analyzer", layout="wide")
st.title("Real Estate Investment Calculator")
st.markdown("Analyze fourplexes and similar properties. Includes basics, expanded deep dive, partnerships, and exports.")

# Property Details (Optional, shown at top)
st.header("Property Details (Optional)")
col1, col2 = st.columns(2)
with col1:
    property_name = st.text_input("Property Name", value="")
    property_address = st.text_input("Property Address", value="")
with col2:
    listing_link = st.text_input("Listing Link", value="")
    picture_url = st.text_input("Picture URL (optional)", value="")
if picture_url:
    try:
        st.image(picture_url, caption="Property Preview", use_column_width=True)
    except:
        st.warning("Could not load image preview")

# Tabs
tab1, tab2, tab3 = st.tabs(["Basic Calculator", "Deep Dive Analysis", "Investor Partnership Modeling"])

with tab1:
    # Inputs in Sidebar
    with st.sidebar:
        st.header("Property & Financing")
        purchase_price = st.number_input("Purchase Price ($)", min_value=0.0, value=400000.0, step=1000.0)
        num_units = st.number_input("Number of Units", min_value=1, value=4, step=1)
        
        # Down Payment: Slider for % (steps of 5%), or direct number input
        down_payment_perc = st.slider("Down Payment (%)", min_value=0.0, max_value=100.0, value=20.0, step=5.0)
        down_payment = st.number_input("Down Payment Amount ($ - overrides % if set)", min_value=0.0, value=(down_payment_perc / 100) * purchase_price, step=1000.0)
        
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
    if st.button("Calculate Basics"):
        loan_amount = purchase_price - down_payment
        monthly_interest_rate = interest_rate / 12
        num_payments = loan_term_years * 12
        if interest_rate > 0:
            monthly_mortgage = -npf.pmt(monthly_interest_rate, num_payments, loan_amount)
        else:
            monthly_mortgage = loan_amount / num_payments if num_payments > 0 else 0
        annual_mortgage = monthly_mortgage * 12
        
        gross_monthly_rent = monthly_rent_per_unit * num_units
        gross_annual_rent = gross_monthly_rent * 12
        effective_annual_rent = gross_annual_rent * (1 - vacancy_rate_perc)
        total_annual_income = effective_annual_rent + other_annual_income
        
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
        
        noi = total_annual_income - total_annual_expenses
        annual_cash_flow = noi - annual_mortgage
        monthly_cash_flow = annual_cash_flow / 12
        
        cap_rate = (noi / purchase_price) * 100 if purchase_price > 0 else 0
        cash_on_cash_return = (annual_cash_flow / down_payment) * 100 if down_payment > 0 else 0
        
        # First Year Amortization
        balance = loan_amount
        total_interest_first_year = 0
        total_principal_first_year = 0
        for month in range(1, 13):
            interest = balance * monthly_interest_rate
            principal = monthly_mortgage - interest
            balance -= principal
            total_interest_first_year += interest
            total_principal_first_year += principal
        
        # Breakeven Price if Cash Flow Negative
        breakeven_price = None
        if annual_cash_flow < 0 and noi > 0:
            affordable_monthly = noi / 12
            max_loan = npf.pv(monthly_interest_rate, num_payments, -affordable_monthly) if monthly_interest_rate > 0 else affordable_monthly * num_payments
            breakeven_price = max_loan + down_payment
        
        # Store results
        st.session_state.results = {
            'purchase_price': purchase_price,
            'down_payment': down_payment,
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'loan_term_years': loan_term_years,
            'monthly_mortgage': monthly_mortgage,
            'annual_mortgage': annual_mortgage,
            'gross_annual_rent': gross_annual_rent,
            'effective_annual_rent': effective_annual_rent,
            'total_annual_income': total_annual_income,
            'total_annual_expenses': total_annual_expenses,
            'noi': noi,
            'annual_cash_flow': annual_cash_flow,
            'monthly_cash_flow': monthly_cash_flow,
            'cap_rate': cap_rate,
            'cash_on_cash_return': cash_on_cash_return,
            'num_units': num_units,
            'monthly_rent_per_unit': monthly_rent_per_unit,
            'vacancy_rate_perc': vacancy_rate_perc,
            'total_interest_first_year': total_interest_first_year,
            'total_principal_first_year': total_principal_first_year,
            'balance_after_year1': balance,
            'monthly_interest_rate': monthly_interest_rate,
            'num_payments': num_payments,
            'breakeven_price': breakeven_price
        }
        
        # Display
        st.header("Results")
        st.subheader("Financing")
        st.write(f"Loan Amount: ${loan_amount:,.2f}")
        st.write(f"Monthly Mortgage: ${monthly_mortgage:,.2f}")
        st.write(f"Annual Mortgage: ${annual_mortgage:,.2f}")
        
        st.subheader("Income")
        st.write(f"Gross Annual Rent: ${gross_annual_rent:,.2f}")
        st.write(f"Effective Annual Rent: ${effective_annual_rent:,.2f}")
        st.write(f"Total Annual Income: ${total_annual_income:,.2f}")
        
        st.subheader("Expenses")
        st.write(f"Total Annual Expenses: ${total_annual_expenses:,.2f}")
        
        st.subheader("Metrics")
        st.write(f"NOI: ${noi:,.2f}")
        st.write(f"Annual Cash Flow: ${annual_cash_flow:,.2f}")
        st.write(f"Monthly Cash Flow: ${monthly_cash_flow:,.2f}")
        st.write(f"Cap Rate: {cap_rate:.2f}%")
        st.write(f"Cash-on-Cash Return: {cash_on_cash_return:.2f}%")
        
        if annual_cash_flow < 0 and breakeven_price is not None:
            st.subheader("Breakeven Analysis")
            st.write(f"Maximum Offer Price for Breakeven Cash Flow: ${breakeven_price:,.2f} (keeps down payment at ${down_payment:,.2f})")
        
        st.subheader("First Year Amortization")
        st.write(f"Interest Paid: ${total_interest_first_year:,.2f}")
        st.write(f"Principal Paid: ${total_principal_first_year:,.2f}")
        st.write(f"Remaining Balance: ${balance:,.2f}")

with tab2:
    if not st.session_state.results:
        st.warning("Run basics first.")
    else:
        basics = st.session_state.results
        st.header("Deep Dive Analysis")
        st.markdown("Enter additional details for advanced projections, including repairs, refi, and profitability analysis.")

        # Expanded Inputs
        holding_period = st.number_input("Holding Period (Years)", min_value=1, value=5, step=1)
        repair_timeline_months = st.number_input("Repair Timeline (Months)", min_value=0, value=3, step=1)
        repair_costs = st.number_input("Repair/Renovation Costs ($)", min_value=0.0, value=20000.0, step=1000.0)
        expected_arv_increase = st.number_input("Expected ARV Increase from Repairs ($)", min_value=0.0, value=50000.0, step=1000.0)
        arv = basics['purchase_price'] + expected_arv_increase
        annual_appreciation_rate = st.slider("Annual Appreciation Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5) / 100
        farv = arv * (1 + annual_appreciation_rate) ** (holding_period - (repair_timeline_months / 12))
        refi_interest_rate = st.slider("Refi Interest Rate (%)", min_value=0.0, max_value=20.0, value=4.5, step=0.1) / 100
        refi_ltv = st.slider("Refi LTV (%)", min_value=0.0, max_value=100.0, value=80.0, step=5.0) / 100
        heloc_ltv = st.slider("HELOC LTV (%)", min_value=0.0, max_value=100.0, value=80.0, step=5.0) / 100
        annual_rent_growth = st.slider("Annual Rent Growth Rate (%)", min_value=0.0, max_value=20.0, value=2.0, step=0.5) / 100
        annual_expense_inflation = st.slider("Annual Expense Inflation Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5) / 100
        resale_costs_perc = st.slider("Resale Costs (% of Sale Price)", min_value=0.0, max_value=20.0, value=6.0, step=0.5) / 100
        target_cap_rate = st.number_input("Target Cap Rate (%)", min_value=0.0, value=7.0, step=0.5) / 100

        if st.button("Calculate Deep Dive"):
            # IRR Calculation (with repairs factored in initial cash flows)
            cash_flows = [-basics['down_payment'] - repair_costs]  # Initial outlay including repairs
            for year in range(1, holding_period + 1):
                adjusted_rent = basics['gross_annual_rent'] * (1 + annual_rent_growth) ** (year - 1)
                adjusted_expenses = basics['total_annual_expenses'] * (1 + annual_expense_inflation) ** (year - 1)
                adjusted_noi = (adjusted_rent * (1 - basics['vacancy_rate_perc'])) - adjusted_expenses
                adjusted_cash_flow = adjusted_noi - basics['annual_mortgage']
                cash_flows.append(adjusted_cash_flow)

            future_value = basics['purchase_price'] * (1 + annual_appreciation_rate) ** holding_period
            approx_principal_paid = basics['total_principal_first_year'] * holding_period
            remaining_loan = max(0, basics['loan_amount'] - approx_principal_paid)
            equity_at_sale = future_value - remaining_loan
            net_proceeds = equity_at_sale - (future_value * resale_costs_perc)
            cash_flows[-1] += net_proceeds

            irr = npf.irr(cash_flows) * 100 if len(cash_flows) > 1 else 0

            # Refi/HELOC
            new_loan_refi = farv * refi_ltv
            cash_out_refi = new_loan_refi - remaining_loan
            heloc_amount = farv * heloc_ltv - remaining_loan

            # Breakeven Analysis
            breakeven_months = np.ceil(repair_costs / max(1, basics['monthly_cash_flow'])) if basics['monthly_cash_flow'] > 0 else float('inf')
            breakeven_occupancy = (total_annual_expenses + annual_mortgage + repair_costs / (holding_period or 1)) / basics['gross_annual_rent'] if basics['gross_annual_rent'] > 0 else 0
            value_at_target_cap = basics['noi'] / target_cap_rate if target_cap_rate > 0 else 0
            profitability_without_reno = basics['annual_cash_flow'] > 0
            profitability_with_reno = (basics['annual_cash_flow'] * holding_period + expected_arv_increase - repair_costs) > 0

            # Store Deep Dive Results
            st.session_state.deep_dive_results = {
                'holding_period': holding_period,
                'repair_timeline_months': repair_timeline_months,
                'repair_costs': repair_costs,
                'expected_arv_increase': expected_arv_increase,
                'arv': arv,
                'farv': farv,
                'irr': irr,
                'equity_at_sale': equity_at_sale,
                'cash_out_refi': cash_out_refi,
                'heloc_amount': heloc_amount,
                'breakeven_months': breakeven_months,
                'breakeven_occupancy': breakeven_occupancy * 100,
                'value_at_target_cap': value_at_target_cap,
                'profitability_without_reno': profitability_without_reno,
                'profitability_with_reno': profitability_with_reno
            }

            # Display Deep Dive Results
            st.subheader("Deep Dive Metrics")
            st.write(f"After Repair Value (ARV): ${arv:,.2f}")
            st.write(f"Future ARV (FARV after holding): ${farv:,.2f}")
            st.write(f"IRR: {irr:.2f}%")
            st.write(f"Equity at Sale: ${equity_at_sale:,.2f}")
            st.write(f"Cash-Out Refi Potential: ${cash_out_refi:,.2f}")
            st.write(f"HELOC Potential (80% LTV): ${heloc_amount:,.2f}")
            st.write(f"Breakeven Months (to recover repairs): {breakeven_months:.0f} months")
            st.write(f"Breakeven Occupancy: {breakeven_occupancy:.2f}%")
            st.write(f"Value at Target Cap Rate: ${value_at_target_cap:,.2f}")
            st.write(f"Profitable Without Reno: {'Yes' if profitability_without_reno else 'No'}")
            st.write(f"Profitable With Reno: {'Yes' if profitability_with_reno else 'No'}")

            # Additional Deep Dive Features (e.g., Sensitivity Chart for Cap Rate)
            st.subheader("Cap Rate Sensitivity")
            cap_rates = np.linspace(max(0.01, cap_rate - 0.05), cap_rate + 0.05, 5)
            values = [noi / cr for cr in cap_rates]
            sens_df = pd.DataFrame({'Cap Rate (%)': cap_rates * 100, 'Property Value': values})
            fig = px.line(sens_df, x='Cap Rate (%)', y='Property Value', title='Value at Different Cap Rates')
            st.plotly_chart(fig)

with tab3:
    if not st.session_state.results:
        st.warning("Run basics first.")
    else:
        basics = st.session_state.results
        st.header("Investor Partnership Modeling")
        st.markdown("Flesh out partnerships with investors, including types, contributions, returns, and preferred options.")

        num_investors = st.number_input("Number of Investors", min_value=1, value=1, step=1)
        total_equity = basics['down_payment']
        sponsor_equity_perc = st.slider("Sponsor Equity %", 0.0, 100.0, 20.0, step=5.0) / 100
        investor_equity_perc = 1 - sponsor_equity_perc
        preferred_return_perc = st.slider("Preferred Return % for Investors", 0.0, 20.0, 8.0, step=0.5) / 100
        profit_split_investor = st.slider("Investor Profit Split % After Pref", 50.0, 90.0, 70.0, step=5.0) / 100

        investor_contribution = total_equity * investor_equity_perc / num_investors if num_investors > 0 else 0
        st.write(f"Per Investor Contribution: ${investor_contribution:,.2f}")

        if st.button("Model Returns"):
            # Simple modeling - expand with cash flows, IRR per investor, etc.
            annual_pref = total_equity * investor_equity_perc * preferred_return_perc
            remaining_cf = basics['annual_cash_flow'] - annual_pref
            investor_annual = annual_pref / num_investors + (remaining_cf * profit_split_investor) / num_investors
            st.write(f"Estimated Annual Return per Investor: ${investor_annual:,.2f}")

            # Add charts, sensitivity, etc.

# Export Section
if st.session_state.results:
    st.markdown("---")
    st.header("Export Analysis")

    basics = st.session_state.results
    deep_dive = st.session_state.deep_dive_results if 'deep_dive_results' in st.session_state else {}

    # Sanitize property name for filename
    safe_name = property_name.replace(' ', '_').replace('.', '').replace('/', '') if property_name else "analysis"

    if st.button("Download CSV"):
        export_data = {
            "Property Name": property_name,
            "Address": property_address,
            "Listing Link": listing_link,
            "Picture URL": picture_url,
            **basics,
            **deep_dive
        }
        df = pd.DataFrame([export_data])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, f"{safe_name}.csv", "text/csv")

    if st.button("Generate PDF Report"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        flowables = []

        flowables.append(Paragraph("Real Estate Investment Report", styles['Title']))
        flowables.append(Spacer(1, 12))
        if property_name:
            flowables.append(Paragraph(f"Property: {property_name}", styles['Heading1']))
        if property_address:
            flowables.append(Paragraph(f"Address: {property_address}", styles['Normal']))
        if listing_link:
            flowables.append(Paragraph(f"Link: {listing_link}", styles['Normal']))
        
        if picture_url:
            try:
                img_data = requests.get(picture_url).content
                img_buffer = BytesIO(img_data)
                img = Image(img_buffer, width=4*inch, height=3*inch)
                flowables.append(img)
            except:
                flowables.append(Paragraph("Could not load image for PDF.", styles['Italic']))

        flowables.append(Spacer(1, 24))
        flowables.append(Paragraph("Basic Metrics", styles['Heading2']))

        data_basic = [
            ["Metric", "Value"],
            ["Purchase Price", f"${basics['purchase_price']:,.2f}"],
            ["Down Payment", f"${basics['down_payment']:,.2f}"],
            ["Loan Amount", f"${basics['loan_amount']:,.2f}"],
            ["NOI", f"${basics['noi']:,.2f}"],
            ["Annual Cash Flow", f"${basics['annual_cash_flow']:,.2f}"],
            ["Cap Rate", f"{basics['cap_rate']:.2f}%"],
            ["Cash-on-Cash Return", f"{basics['cash_on_cash_return']:.2f}%"]
        ]
        if basics.get('breakeven_price'):
            data_basic.append(["Breakeven Price (for Positive CF)", f"${basics['breakeven_price']:,.2f}"])

        table_basic = Table(data_basic, colWidths=[3*inch, 3*inch])
        table_basic.setStyle([
            ('BACKGROUND', (0,0), (-1,0), '#d0d0d0'),
            ('GRID', (0,0), (-1,-1), 1, '#000000'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT')
        ])
        flowables.append(table_basic)

        if deep_dive:
            flowables.append(Spacer(1, 24))
            flowables.append(Paragraph("Deep Dive Metrics", styles['Heading2']))

            data_deep = [
                ["Metric", "Value"],
                ["Holding Period (Years)", deep_dive['holding_period']],
                ["Repair Timeline (Months)", deep_dive['repair_timeline_months']],
                ["Repair Costs", f"${deep_dive['repair_costs']:,.2f}"],
                ["ARV Increase", f"${deep_dive['expected_arv_increase']:,.2f}"],
                ["ARV", f"${deep_dive['arv']:,.2f}"],
                ["FARV", f"${deep_dive['farv']:,.2f}"],
                ["IRR", f"{deep_dive['irr']:.2f}%"],
                ["Equity at Sale", f"${deep_dive['equity_at_sale']:,.2f}"],
                ["Cash-Out Refi", f"${deep_dive['cash_out_refi']:,.2f}"],
                ["HELOC Amount", f"${deep_dive['heloc_amount']:,.2f}"],
                ["Breakeven Months", f"{deep_dive['breakeven_months']:.0f}"],
                ["Breakeven Occupancy %", f"{deep_dive['breakeven_occupancy']:.2f}%" ],
                ["Value at Target Cap", f"${deep_dive['value_at_target_cap']:,.2f}"],
                ["Profitable Without Reno", 'Yes' if deep_dive['profitability_without_reno'] else 'No'],
                ["Profitable With Reno", 'Yes' if deep_dive['profitability_with_reno'] else 'No']
            ]

            table_deep = Table(data_deep, colWidths=[3*inch, 3*inch])
            table_deep.setStyle([
                ('BACKGROUND', (0,0), (-1,0), '#d0d0d0'),
                ('GRID', (0,0), (-1,-1), 1, '#000000'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT')
            ])
            flowables.append(table_deep)

        doc.build(flowables)
        buffer.seek(0)
        st.download_button("Download PDF", buffer, f"{safe_name}.pdf", "application/pdf")

st.markdown("""
### Notes:
- Calculations are estimates. Consult professionals.
""")