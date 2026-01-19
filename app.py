# app.py
# Enhanced Real Estate Investment Calculator with Deep Dive and Investor Partnership Modeling
# This is a Streamlit web app. To run it locally: pip install streamlit numpy-financial plotly
# Then: streamlit run app.py
# To deploy: Create a GitHub repo, add this file as app.py, add requirements.txt with: streamlit\numpy-financial\nplotly
# Then deploy to Streamlit Cloud (streamlit.io) by connecting your GitHub repo.

import streamlit as st
import numpy_financial as npf  # For financial calculations like PMT, IRR
import numpy as np
import plotly.express as px
import pandas as pd

# Use session state to store calculations across tabs
if 'results' not in st.session_state:
    st.session_state.results = {}

st.title("Real Estate Investment Calculator")
st.markdown("""
This app helps you evaluate real estate investments, such as fourplexes. It includes basic calculations, deep dive analysis, and now investor partnership modeling.
Use the tabs below to navigate.
""")

# Tabs for Main, Deep Dive, and Investor Modeling
tab1, tab2, tab3 = st.tabs(["Basic Calculator", "Deep Dive Analysis", "Investor Partnership Modeling"])

with tab1:
    # Sidebar for inputs (moved inside tab for clarity)
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
    if st.button("Calculate Basics"):
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
        
        # Store in session state
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
        }
        
        # Display Results
        st.header("Basic Results")
        
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
        
        # Basic Break-Even Analysis
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

with tab2:
    if not st.session_state.results:
        st.warning("Please run the basic calculations first in the 'Basic Calculator' tab.")
    else:
        # Retrieve basics
        basics = st.session_state.results
        purchase_price = basics['purchase_price']
        down_payment = basics['down_payment']
        loan_amount = basics['loan_amount']
        interest_rate = basics['interest_rate']
        loan_term_years = basics['loan_term_years']
        monthly_mortgage = basics['monthly_mortgage']
        annual_mortgage = basics['annual_mortgage']
        gross_annual_rent = basics['gross_annual_rent']
        total_annual_income = basics['total_annual_income']
        total_annual_expenses = basics['total_annual_expenses']
        noi = basics['noi']
        annual_cash_flow = basics['annual_cash_flow']
        num_units = basics['num_units']
        monthly_rent_per_unit = basics['monthly_rent_per_unit']
        vacancy_rate_perc = basics['vacancy_rate_perc']

        st.header("Deep Dive Analysis")
        st.markdown("Enter additional details below for advanced metrics. Sections are expandable.")

        # 1. Financial Metrics and Projections
        with st.expander("Financial Metrics and Projections", expanded=True):
            holding_period = st.number_input("Holding Period (Years)", min_value=1, value=5, step=1, key="holding_period_deep")
            annual_appreciation_rate = st.slider("Expected Annual Appreciation Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5, key="apprec_deep") / 100
            annual_rent_growth = st.slider("Annual Rent Growth Rate (%)", min_value=0.0, max_value=20.0, value=2.0, step=0.5, key="rent_growth_deep") / 100
            annual_expense_inflation = st.slider("Annual Expense Inflation Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5, key="exp_infl_deep") / 100
            resale_costs_perc = st.slider("Resale Costs (% of Sale Price)", min_value=0.0, max_value=20.0, value=6.0, step=0.5, key="resale_deep") / 100

            # IRR Calculation
            cash_flows = [-down_payment]  # Initial investment
            for year in range(1, holding_period + 1):
                adjusted_rent = gross_annual_rent * (1 + annual_rent_growth) ** (year - 1)
                adjusted_expenses = total_annual_expenses * (1 + annual_expense_inflation) ** (year - 1)
                adjusted_noi = (adjusted_rent * (1 - vacancy_rate_perc)) - adjusted_expenses
                adjusted_cash_flow = adjusted_noi - annual_mortgage  # Assuming fixed mortgage
                cash_flows.append(adjusted_cash_flow)

            # Add exit cash flow
            future_value = purchase_price * (1 + annual_appreciation_rate) ** holding_period
            equity_at_sale = future_value - (loan_amount - total_principal_first_year * holding_period)  # Approximate
            net_proceeds = equity_at_sale - (future_value * resale_costs_perc)
            cash_flows[-1] += net_proceeds

            irr = npf.irr(cash_flows) * 100 if len(cash_flows) > 1 else 0
            st.write(f"Internal Rate of Return (IRR): {irr:.2f}%")

            # Equity Buildup
            # Full Amortization Table (simplified)
            monthly_interest_rate = interest_rate / 12
            num_payments = loan_term_years * 12
            balances = [loan_amount]
            for _ in range(1, num_payments + 1):
                interest = balances[-1] * monthly_interest_rate
                principal = monthly_mortgage - interest
                balances.append(balances[-1] - principal)
            equity_df = pd.DataFrame({
                'Month': range(1, num_payments + 1),
                'Remaining Balance': balances[1:]
            })
            st.subheader("Amortization Schedule")
            st.dataframe(equity_df.style.format({'Remaining Balance': '${:,.2f}'}))

            # DSCR
            dscr = noi / annual_mortgage if annual_mortgage > 0 else float('inf')
            st.write(f"Debt Service Coverage Ratio (DSCR): {dscr:.2f}x")

            # Sensitivity Testing
            st.subheader("Sensitivity Analysis")
            rent_changes = np.linspace(-0.2, 0.2, 5)  # -20% to +20%
            cf_matrix = []
            for change in rent_changes:
                adjusted_rent = gross_annual_rent * (1 + change)
                adjusted_noi = (adjusted_rent * (1 - vacancy_rate_perc)) - total_annual_expenses
                adjusted_cf = adjusted_noi - annual_mortgage
                cf_matrix.append(adjusted_cf)
            sens_df = pd.DataFrame({'Rent Change (%)': rent_changes * 100, 'Annual Cash Flow': cf_matrix})
            fig = px.line(sens_df, x='Rent Change (%)', y='Annual Cash Flow', title='Cash Flow Sensitivity to Rent Changes')
            st.plotly_chart(fig)

        # 2. Market and Location Analysis
        with st.expander("Market and Location Analysis"):
            # Rental Demand and Vacancy Trends
            local_vacancy_rate = st.slider("Local Market Vacancy Rate (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5) / 100
            adjusted_effective_rent = gross_annual_rent * (1 - local_vacancy_rate)
            st.write(f"Adjusted Effective Annual Rent (Local Vacancy): ${adjusted_effective_rent:,.2f}")

            # Appreciation Potential
            future_value = purchase_price * (1 + annual_appreciation_rate) ** holding_period
            st.write(f"Projected Property Value in {holding_period} Years: ${future_value:,.2f}")

            # Comparable Properties
            st.subheader("Comparable Properties (Comps)")
            num_comps = st.number_input("Number of Comps", min_value=1, max_value=10, value=3)
            comp_prices = []
            comp_cap_rates = []
            for i in range(num_comps):
                col1, col2 = st.columns(2)
                with col1:
                    comp_prices.append(st.number_input(f"Comp {i+1} Price ($)", min_value=0.0, value=purchase_price))
                with col2:
                    comp_cap_rates.append(st.number_input(f"Comp {i+1} Cap Rate (%)", min_value=0.0, value=basics['cap_rate']) / 100)
            avg_comp_price = np.mean(comp_prices) if comp_prices else 0
            avg_comp_cap = np.mean(comp_cap_rates) * 100 if comp_cap_rates else 0
            st.write(f"Average Comp Price: ${avg_comp_price:,.2f}")
            st.write(f"Average Comp Cap Rate: {avg_comp_cap:.2f}%")
            if avg_comp_price > 0:
                value_comparison = (purchase_price / avg_comp_price) * 100
                st.write(f"Your Property Price as % of Avg Comp: {value_comparison:.2f}%")

            # Neighborhood Quality Metrics
            st.subheader("Neighborhood Scores (Manual Input)")
            crime_score = st.slider("Crime Score (0-100, lower better)", 0, 100, 50)
            school_score = st.slider("School Score (0-100, higher better)", 0, 100, 70)
            walkability_score = st.slider("Walkability Score (0-100, higher better)", 0, 100, 60)
            overall_location_score = (100 - crime_score) * 0.4 + school_score * 0.3 + walkability_score * 0.3
            st.metric("Overall Location Score", f"{overall_location_score:.1f}/100")

        # Area Analysis (User's Addition)
        with st.expander("Area Analysis Resources"):
            st.markdown("""
            Enter your property's address or ZIP code below to generate direct links to free resources for checking local rents, crime rates, schools, parks, walkability, etc.
            """)
            address_or_zip = st.text_input("Property Address or ZIP Code")
            if address_or_zip:
                st.subheader("Free Resources (Click to Visit)")
                st.markdown(f"- **Rents and Home Values**: [Zillow Search](https://www.zillow.com/homes/{address_or_zip}_rb/)")
                st.markdown(f"- **Walkability Rating**: [Walk Score](https://www.walkscore.com/?q={address_or_zip})")
                st.markdown(f"- **Crime Rates**: [SpotCrime](https://spotcrime.com/search?q={address_or_zip}) or [CrimeMapping](https://www.crimemapping.com/map/location/{address_or_zip})")
                st.markdown(f"- **Schools**: [GreatSchools](https://www.greatschools.org/search/search.page?search_type=0&q={address_or_zip})")
                st.markdown(f"- **Neighborhood Data (Crime, Schools, etc.)**: [AreaVibes](https://www.areavibes.com/{address_or_zip}/) or [NeighborhoodScout](https://www.neighborhoodscout.com/search?s={address_or_zip})")
                st.markdown(f"- **Cost of Living, Crime, Schools**: [BestPlaces.net](https://www.bestplaces.net/find_a_place/?q={address_or_zip})")
                st.markdown(f"- **Parks and Amenities**: Use Google Maps for '{address_or_zip}' or local city websites.")
                st.markdown(f"- **State-Wide Crime Data**: [FBI Crime Data Explorer](https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/explorer/crime/crime-trend)")
            else:
                st.info("Enter an address or ZIP to see tailored links.")

        # 3. Property-Specific Details
        with st.expander("Property-Specific Details"):
            # Inspection and CapEx Reserves
            capex_perc = st.slider("Annual CapEx (% of Gross Rent)", min_value=0.0, max_value=50.0, value=5.0, step=0.5) / 100
            annual_capex = capex_perc * gross_annual_rent
            one_time_repairs = st.number_input("One-Time Repair Costs ($)", min_value=0.0, value=0.0, step=1000.0)
            adjusted_expenses = total_annual_expenses + annual_capex
            adjusted_noi = total_annual_income - adjusted_expenses
            st.write(f"Annual CapEx Reserve: ${annual_capex:,.2f}")
            st.write(f"Adjusted NOI (with CapEx): ${adjusted_noi:,.2f}")

            # Tenant Profile and Lease Analysis
            st.subheader("Tenant Profile")
            current_occupancy = st.slider("Current Occupancy Rate (%)", min_value=0.0, max_value=100.0, value=95.0, step=5.0) / 100
            turnover_cost_per_unit = st.number_input("Turnover Cost per Unit ($)", min_value=0.0, value=1000.0, step=100.0)
            annual_turnover = (1 - current_occupancy) * num_units * turnover_cost_per_unit
            st.write(f"Estimated Annual Turnover Costs: ${annual_turnover:,.2f}")

            # Utilities and Operational Efficiency
            utilities_paid_by = st.selectbox("Utilities Paid By", ["Owner", "Tenants"])
            if utilities_paid_by == "Owner":
                efficiency_savings = st.number_input("Potential Efficiency Savings ($/year)", min_value=0.0, value=0.0)
                adjusted_utilities = annual_utilities - efficiency_savings
                st.write(f"Adjusted Annual Utilities: ${adjusted_utilities:,.2f}")

        # Renovations for Refi/HELOC (User's Addition)
        with st.expander("Renovations and Refi/HELOC Analysis"):
            reno_cost = st.number_input("Renovation Costs ($)", min_value=0.0, value=0.0, step=1000.0)
            expected_value_increase = st.number_input("Expected Value Increase from Reno ($)", min_value=0.0, value=0.0, step=1000.0)
            arv = purchase_price + expected_value_increase  # After Repair Value
            refi_ltv = st.slider("Refi Loan-to-Value Ratio (%)", min_value=0.0, max_value=100.0, value=80.0, step=5.0) / 100
            heloc_ltv = st.slider("HELOC Loan-to-Value Ratio (%)", min_value=0.0, max_value=100.0, value=80.0, step=5.0) / 100
            current_balance = loan_amount  # Approximate

            new_loan_amount = arv * refi_ltv
            cash_out_refi = new_loan_amount - current_balance - reno_cost
            st.write(f"After Repair Value (ARV): ${arv:,.2f}")
            st.write(f"Potential Cash-Out from Refi: ${cash_out_refi:,.2f} (after costs)")

            heloc_amount = arv * heloc_ltv - current_balance
            st.write(f"Potential HELOC Amount: ${heloc_amount:,.2f}")

        # 4. Risk and Legal Considerations
        with st.expander("Risk and Legal Considerations"):
            # Risk Assessment
            st.subheader("Risk Assessment (Monte Carlo Simulation)")
            num_simulations = st.number_input("Number of Simulations", min_value=100, max_value=10000, value=1000, step=100)
            rent_volatility = st.slider("Rent Volatility (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0) / 100
            expense_volatility = st.slider("Expense Volatility (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0) / 100

            sim_cash_flows = []
            for _ in range(num_simulations):
                sim_rent = gross_annual_rent * np.random.normal(1, rent_volatility)
                sim_expenses = total_annual_expenses * np.random.normal(1, expense_volatility)
                sim_noi = (sim_rent * (1 - vacancy_rate_perc)) - sim_expenses
                sim_cf = sim_noi - annual_mortgage
                sim_cash_flows.append(sim_cf)

            avg_cf = np.mean(sim_cash_flows)
            prob_positive = np.mean(np.array(sim_cash_flows) > 0) * 100
            st.write(f"Average Simulated Annual Cash Flow: ${avg_cf:,.2f}")
            st.write(f"Probability of Positive Cash Flow: {prob_positive:.2f}%")

            fig_risk = px.histogram(sim_cash_flows, nbins=50, title='Distribution of Simulated Cash Flows')
            st.plotly_chart(fig_risk)

            # Tax Implications
            tax_bracket = st.slider("Your Tax Bracket (%)", min_value=0.0, max_value=50.0, value=25.0, step=1.0) / 100
            depreciation_method = st.selectbox("Depreciation Method", ["Straight-Line (27.5 years for residential)"])
            annual_depreciation = purchase_price / 27.5  # Simplified
            tax_savings = annual_depreciation * tax_bracket
            after_tax_cf = annual_cash_flow - (annual_cash_flow * tax_bracket) + tax_savings
            st.write(f"Annual Depreciation: ${annual_depreciation:,.2f}")
            st.write(f"Estimated Tax Savings from Depreciation: ${tax_savings:,.2f}")
            st.write(f"After-Tax Annual Cash Flow: ${after_tax_cf:,.2f}")

            # Legal/Zoning Compliance
            st.subheader("Legal/Zoning Checklist")
            zoning_ok = st.checkbox("Zoning Allows Multifamily Use")
            hoa_rules_ok = st.checkbox("HOA Rules Compliant")
            landlord_laws_reviewed = st.checkbox("Local Landlord-Tenant Laws Reviewed")
            if all([zoning_ok, hoa_rules_ok, landlord_laws_reviewed]):
                st.success("All checks passed.")
            else:
                st.warning("Review flagged items.")

            # Exit Strategy
            exit_years = st.number_input("Alternative Exit Timeline (Years)", min_value=1, value=holding_period, step=1)
            exit_value = purchase_price * (1 + annual_appreciation_rate) ** exit_years
            exit_equity = exit_value - balances[exit_years * 12] if exit_years * 12 < len(balances) else exit_value
            exit_net = exit_equity - (exit_value * resale_costs_perc)
            st.write(f"Net Proceeds at Exit in {exit_years} Years: ${exit_net:,.2f}")

with tab3:
    if not st.session_state.results:
        st.warning("Please run the basic calculations first in the 'Basic Calculator' tab.")
    else:
        # Retrieve basics
        basics = st.session_state.results
        purchase_price = basics['purchase_price']
        down_payment = basics['down_payment']
        annual_cash_flow = basics['annual_cash_flow']
        noi = basics['noi']
        gross_annual_rent = basics['gross_annual_rent']
        vacancy_rate_perc = basics['vacancy_rate_perc']
        total_annual_expenses = basics['total_annual_expenses']
        annual_mortgage = basics['annual_mortgage']

        st.header("Investor Partnership Modeling")
        st.markdown("""
        This section models partnerships with investors. Configure investor types, contributions, preferred returns, equity splits, and more.
        Use sliders and inputs to simulate scenarios and see estimated returns.
        """)

        # Key Inputs for Partnership
        num_investors = st.number_input("Number of Passive Investors (LPs)", min_value=1, value=3, step=1)
        total_equity_needed = down_payment  # Assuming equity is down payment
        sponsor_equity_perc = st.slider("Sponsor (GP) Equity %", min_value=0.0, max_value=50.0, value=10.0, step=1.0) / 100
        investor_equity_perc = 1 - sponsor_equity_perc
        st.write(f"Investor (LP) Equity %: {investor_equity_perc * 100:.1f}%")

        preferred_return_perc = st.slider("Preferred Return for Investors (%)", min_value=0.0, max_value=15.0, value=8.0, step=0.5) / 100
        profit_split_investor_perc = st.slider("Investor Profit Split After Pref (%)", min_value=50.0, max_value=90.0, value=70.0, step=5.0) / 100
        profit_split_sponsor_perc = 1 - profit_split_investor_perc

        holding_period = st.number_input("Holding Period (Years)", min_value=1, value=5, step=1, key="holding_period_inv")
        annual_appreciation_rate = st.slider("Expected Annual Appreciation Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5, key="apprec_inv") / 100
        annual_rent_growth = st.slider("Annual Rent Growth Rate (%)", min_value=0.0, max_value=20.0, value=2.0, step=0.5, key="rent_growth_inv") / 100
        annual_expense_inflation = st.slider("Annual Expense Inflation Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.5, key="exp_infl_inv") / 100
        resale_costs_perc = st.slider("Resale Costs (% of Sale Price)", min_value=0.0, max_value=20.0, value=6.0, step=0.5, key="resale_inv") / 100

        # Investor Contributions (Simplified: Equal split among investors)
        investor_total_contribution = total_equity_needed * investor_equity_perc
        sponsor_contribution = total_equity_needed * sponsor_equity_perc
        per_investor_contribution = investor_total_contribution / num_investors if num_investors > 0 else 0

        st.subheader("Equity Contributions")
        st.write(f"Total Equity Needed: ${total_equity_needed:,.2f}")
        st.write(f"Sponsor Contribution: ${sponsor_contribution:,.2f} ({sponsor_equity_perc * 100:.1f}%)")
        st.write(f"Total Investor Contribution: ${investor_total_contribution:,.2f} ({investor_equity_perc * 100:.1f}%)")
        st.write(f"Per Investor Contribution: ${per_investor_contribution:,.2f}")

        # Waterfall Structure Simulation
        if st.button("Calculate Partnership Returns"):
            # Project Cash Flows Over Holding Period
            investor_cash_flows = [-per_investor_contribution] * num_investors  # List for each investor, but since equal, we can compute for one and multiply
            sponsor_cash_flows = [-sponsor_contribution]
            total_cf_years = []

            for year in range(1, holding_period + 1):
                adjusted_rent = gross_annual_rent * (1 + annual_rent_growth) ** (year - 1)
                adjusted_expenses = total_annual_expenses * (1 + annual_expense_inflation) ** (year - 1)
                adjusted_noi = (adjusted_rent * (1 - vacancy_rate_perc)) - adjusted_expenses
                adjusted_cf = adjusted_noi - annual_mortgage
                total_cf_years.append(adjusted_cf)

                # Apply Waterfall for Operating Cash Flow
                # Step 1: Preferred Return to Investors
                annual_pref_to_investors = investor_total_contribution * preferred_return_perc
                if adjusted_cf >= annual_pref_to_investors:
                    investor_year_cf = annual_pref_to_investors
                    remaining_cf = adjusted_cf - annual_pref_to_investors
                else:
                    investor_year_cf = adjusted_cf
                    remaining_cf = 0

                # Step 2: Split Remaining Profits
                investor_split = remaining_cf * profit_split_investor_perc
                sponsor_split = remaining_cf * profit_split_sponsor_perc

                # Distribute to Investors and Sponsor
                per_investor_year_cf = investor_year_cf / num_investors + investor_split / num_investors
                sponsor_year_cf = sponsor_split

                # Append to Cash Flows (for one investor and sponsor)
                investor_cash_flows[0] += per_investor_year_cf  # Track for one
                sponsor_cash_flows.append(sponsor_year_cf)

            # Exit: Return of Capital + Profits
            future_value = purchase_price * (1 + annual_appreciation_rate) ** holding_period
            net_sale_proceeds = future_value - loan_amount - (future_value * resale_costs_perc)  # Simplified, assuming loan paid off

            # Waterfall on Sale Proceeds
            # Step 1: Return of Capital
            remaining_after_capital = net_sale_proceeds - total_equity_needed

            # Step 2: Catch-up Preferred if any (simplified, assuming cumulative not modeled)
            # For simplicity, we assume prefs are paid annually, so no catch-up here

            # Step 3: Split Excess Profits
            investor_exit = (total_equity_needed * investor_equity_perc) + (remaining_after_capital * profit_split_investor_perc)
            sponsor_exit = (total_equity_needed * sponsor_equity_perc) + (remaining_after_capital * profit_split_sponsor_perc)

            per_investor_exit = investor_exit / num_investors

            # Add to Final Year
            investor_cash_flows[0] += per_investor_exit
            sponsor_cash_flows[-1] += sponsor_exit

            # Calculate IRRs
            investor_irr = npf.irr([ -per_investor_contribution ] + [per_investor_year_cf for _ in range(holding_period - 1)] + [per_investor_year_cf + per_investor_exit]) * 100
            sponsor_irr = npf.irr(sponsor_cash_flows) * 100

            # Display Results
            st.subheader("Estimated Returns")
            st.write(f"Per Investor Annual Cash Flow (Avg): ${sum(total_cf_years) / holding_period / num_investors * investor_equity_perc:,.2f}")
            st.write(f"Per Investor IRR: {investor_irr:.2f}%")
            st.write(f"Sponsor IRR (incl. Promote): {sponsor_irr:.2f}%")

            # Chart Cash Flows
            years = list(range(0, holding_period + 1))
            investor_cf_series = [-per_investor_contribution] + [per_investor_year_cf for _ in range(holding_period - 1)] + [per_investor_year_cf + per_investor_exit]
            sponsor_cf_series = sponsor_cash_flows[:holding_period] + [sponsor_cash_flows[-1]]  # Adjust length

            cf_df = pd.DataFrame({
                'Year': years,
                'Per Investor Cash Flow': investor_cf_series,
                'Sponsor Cash Flow': sponsor_cf_series
            })
            fig_cf = px.bar(cf_df, x='Year', y=['Per Investor Cash Flow', 'Sponsor Cash Flow'], title='Cash Flow Distribution Over Time')
            st.plotly_chart(fig_cf)

        st.markdown("""
        ### Notes on Partnership Modeling:
        - **Investor Types**: Modeled as passive LPs (investors) vs. active GP (sponsor/you).
        - **Preferred Return**: Annual pref paid first from cash flow.
        - **Equity Split**: Slider controls sponsor vs. investor equity; profits split after pref.
        - **Assumptions**: Equal investor contributions; simple waterfall (no catch-up, cumulative prefs approximated); consult legal/financial pros for real deals.
        - This simulates a basic syndication structure—extend for more tiers or fees.
        """)

st.markdown("""
### Overall Notes:
- This is an enhanced calculator. Consult professionals for advice.
- Assumptions: Simplified models; real scenarios vary.
""")