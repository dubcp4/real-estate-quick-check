# app.py - Real Estate Investment Calculator (Fixed & with Export)
import streamlit as st
import numpy_financial as npf
import numpy as np
import plotly.express as px
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# Session state initialization
if 'results' not in st.session_state:
    st.session_state.results = {}

st.set_page_config(page_title="Fourplex Investment Analyzer", layout="wide")
st.title("Real Estate Investment Calculator")
st.markdown("Basic analysis, deep dive, partnership modeling & export options.")

# Sidebar - Property Identification (for export & context)
with st.sidebar:
    st.header("Property Info (for Export)")
    property_address = st.text_input("Property Address", "123 Example St, Salt Lake City, UT")
    listing_link = st.text_input("Listing Link", "")
    picture_url = st.text_input("Picture URL (optional)", "")
    if picture_url:
        try:
            st.image(picture_url, caption="Property Preview", use_column_width=True)
        except:
            st.warning("Could not load image preview")

# Tabs
tab1, tab2, tab3 = st.tabs(["Basic", "Deep Dive", "Partnerships"])

with tab1:
    with st.sidebar:
        st.header("Core Inputs")
        purchase_price = st.number_input("Purchase Price ($)", 0.0, value=400000.0, step=5000.0)
        num_units = st.number_input("Number of Units", 1, value=4)
        down_payment_perc = st.slider("Down Payment %", 0.0, 100.0, 20.0)
        down_payment = purchase_price * (down_payment_perc / 100)
        interest_rate = st.slider("Interest Rate %", 0.0, 15.0, 5.5) / 100
        loan_term_years = st.number_input("Loan Term (Years)", 5, 40, 30)

        st.header("Income & Expenses")
        monthly_rent_per_unit = st.number_input("Rent per Unit/Month", 500.0, value=1200.0)
        vacancy_rate_perc = st.slider("Vacancy Rate %", 0.0, 30.0, 5.0) / 100
        management_fee_perc = st.slider("Management Fee %", 0.0, 20.0, 8.0) / 100
        annual_property_taxes = st.number_input("Annual Taxes ($)", 0.0, value=5000.0)
        annual_insurance = st.number_input("Annual Insurance ($)", 0.0, value=2000.0)
        maintenance_perc = st.slider("Maintenance % of Rent", 0.0, 30.0, 10.0) / 100
        annual_utilities = st.number_input("Annual Utilities ($)", 0.0, value=0.0)
        other_expenses = st.number_input("Other Annual Expenses ($)", 0.0, value=0.0)

    if st.button("Calculate"):
        loan_amount = purchase_price - down_payment
        monthly_rate = interest_rate / 12
        n_payments = loan_term_years * 12

        monthly_mortgage = -npf.pmt(monthly_rate, n_payments, loan_amount) if interest_rate > 0 else loan_amount / n_payments
        annual_mortgage = monthly_mortgage * 12

        gross_annual_rent = monthly_rent_per_unit * num_units * 12
        effective_rent = gross_annual_rent * (1 - vacancy_rate_perc)
        total_income = effective_rent

        maint_cost = maintenance_perc * gross_annual_rent
        mgmt_cost = management_fee_perc * gross_annual_rent
        total_expenses = annual_property_taxes + annual_insurance + maint_cost + mgmt_cost + annual_utilities + other_expenses

        noi = total_income - total_expenses
        annual_cf = noi - annual_mortgage
        cap_rate = (noi / purchase_price) * 100 if purchase_price > 0 else 0
        coc_return = (annual_cf / down_payment) * 100 if down_payment > 0 else 0

        # Amortization for first year & storage
        balance = loan_amount
        interest_year1 = 0
        principal_year1 = 0

        for _ in range(12):
            if balance <= 0:
                break
            interest = balance * monthly_rate
            principal = monthly_mortgage - interest
            balance -= principal
            interest_year1 += interest
            principal_year1 += principal

        # Store everything
        st.session_state.results = {
            'purchase_price': purchase_price,
            'down_payment': down_payment,
            'loan_amount': loan_amount,
            'monthly_mortgage': monthly_mortgage,
            'annual_mortgage': annual_mortgage,
            'gross_annual_rent': gross_annual_rent,
            'effective_annual_rent': effective_rent,
            'noi': noi,
            'annual_cash_flow': annual_cf,
            'cap_rate': cap_rate,
            'cash_on_cash_return': coc_return,
            'principal_year1': principal_year1,
            'balance_after_year1': balance,
            'monthly_rate': monthly_rate,
            'n_payments': n_payments,
            'num_units': num_units,
            'monthly_rent_per_unit': monthly_rent_per_unit,
            'vacancy_rate_perc': vacancy_rate_perc,
            'total_expenses': total_expenses
        }

        st.success("Calculation complete! Check Deep Dive & Partnerships tabs.")

        st.subheader("Quick Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("NOI", f"${noi:,.0f}")
        col2.metric("Annual Cash Flow", f"${annual_cf:,.0f}")
        col3.metric("Cash-on-Cash", f"{coc_return:.1f}%")

# ────────────────────────────────────────────────────────────────
# DEEP DIVE TAB
# ────────────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.results:
        st.info("Run calculation in Basic tab first")
    else:
        r = st.session_state.results

        st.header("Deep Dive")

        holding_years = st.slider("Holding Period (years)", 1, 15, 5)
        appr_rate = st.slider("Annual Appreciation %", 0.0, 10.0, 3.0) / 100

        future_value = r['purchase_price'] * (1 + appr_rate) ** holding_years

        # Approximate remaining loan (better than old version)
        monthly_principal_est = r['principal_year1'] / 12 if holding_years >= 1 else 0
        principal_paid_est = monthly_principal_est * 12 * holding_years
        remaining_loan = max(0, r['loan_amount'] - principal_paid_est)

        equity_at_sale = future_value - remaining_loan
        st.write(f"Projected Value: **${future_value:,.0f}**")
        st.write(f"Est. Equity at Sale: **${equity_at_sale:,.0f}**")

        # (You can expand with full IRR, sensitivity, etc. as before)

# ────────────────────────────────────────────────────────────────
# PARTNERSHIPS TAB (stub - expand as needed)
# ────────────────────────────────────────────────────────────────
with tab3:
    if not st.session_state.results:
        st.info("Run calculation first")
    else:
        st.header("Investor Partnership Modeling")
        st.info("Partnership features coming soon — basic structure placeholder")
        # Add your previous partnership code here when ready

# ────────────────────────────────────────────────────────────────
# EXPORT SECTION
# ────────────────────────────────────────────────────────────────
if st.session_state.results:
    st.markdown("---")
    st.header("Export Results")

    r = st.session_state.results

    export_dict = {
        "Date": "2026-01-19",
        "Property": property_address,
        "Listing Link": listing_link,
        "Photo URL": picture_url,
        "Purchase Price": r['purchase_price'],
        "Down Payment": r['down_payment'],
        "Loan Amount": r['loan_amount'],
        "Monthly Mortgage": r['monthly_mortgage'],
        "NOI": r['noi'],
        "Annual Cash Flow": r['annual_cash_flow'],
        "Cap Rate %": r['cap_rate'],
        "Cash-on-Cash %": r['cash_on_cash_return'],
    }

    df_export = pd.DataFrame([export_dict])

    # CSV Download
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv,
        f"analysis_{property_address.replace(' ','_')[:25]}.csv",
        "text/csv"
    )

    # Simple PDF Report
    if st.button("Generate PDF Report"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        flowables = []

        flowables.append(Paragraph("Investment Analysis Report", styles['Title']))
        flowables.append(Spacer(1, 12))
        flowables.append(Paragraph(f"Property: {property_address}", styles['Heading2']))
        flowables.append(Spacer(1, 24))

        data = [["Metric", "Value"]] + [[k, f"${v:,.0f}" if isinstance(v, (int,float)) and k not in ["Cap Rate %", "Cash-on-Cash %"] else f"{v:.1f}%" if k in ["Cap Rate %", "Cash-on-Cash %"] else v] for k,v in export_dict.items() if k not in ["Date","Property","Listing Link","Photo URL"]]

        table = Table(data)
        table.setStyle([
            ('BACKGROUND', (0,0), (-1,0), '#336699'),
            ('TEXTCOLOR', (0,0), (-1,0), 'white'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, '#cccccc')
        ])
        flowables.append(table)

        doc.build(flowables)
        buffer.seek(0)

        st.download_button(
            "📄 Download PDF",
            buffer,
            f"report_{property_address.replace(' ','_')[:25]}.pdf",
            "application/pdf"
        )

st.markdown("---")
st.caption("For educational use. Consult professionals for real investments.")
