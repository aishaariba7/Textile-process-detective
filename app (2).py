import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(
    page_title="Textile Process Detective",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Textile Process Detective")
st.caption("Investigating Hidden Production Costs, Fabric Yields & Profit Margins")

# Sidebar - Detective Control Panel
st.sidebar.header("🕵️ Case Parameters")
order_qty = st.sidebar.number_input("Order Quantity (Units)", min_value=1, value=5000, step=500)
currency_symbol = st.sidebar.selectbox("Select Currency", ["USD ($)", "EUR (€)", "PKR (₨)", "INR (₹)"])
curr_code = currency_symbol.split(" ")[0]

target_profit = st.sidebar.slider("Target Profit Margin (%)", min_value=1.0, max_value=50.0, value=25.0, step=0.5)

# Tabs
tab_spec, tab_cost, tab_analytics, tab_export = st.tabs([
    "🔍 1. Material Evidence", 
    "💸 2. Cost Investigation", 
    "📈 3. Margin Clues", 
    "📋 4. Final Verdict"
])

# --- TAB 1: MATERIAL EVIDENCE ---
with tab_spec:
    st.subheader("Fabric & Construction Specifications")
    col1, col2 = st.columns(2)
    
    with col1:
        fabric_type = st.selectbox("Fabric Type", ["Single Jersey (T-Shirt)", "Fleece (Hoodie)", "Pique (Polo)", "Denim", "Custom"])
        gsm = st.number_input("Fabric Weight (GSM - g/m²)", min_value=50, max_value=500, value=180, step=10)
        garment_area = st.number_input("Garment Surface Area Estimate (m²)", min_value=0.1, max_value=3.0, value=1.2, step=0.1)
    
    with col2:
        yarn_loss = st.number_input("Process Loss / Wastage (%)", min_value=0.0, max_value=20.0, value=7.5, step=0.5)
        calculated_weight = (gsm * garment_area) / 1000
        st.info(f"💡 **Estimated Net Fabric Consumption:** {calculated_weight:.3f} Kg / piece")

# --- TAB 2: COST INVESTIGATION ---
with tab_cost:
    st.subheader("Operational & Direct Cost Evidence")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### 🧶 Raw Material & Knitting")
        yarn_cost_kg = st.number_input("Yarn Cost / Kg", min_value=0.0, value=4.80, step=0.10)
        knitting_cost_kg = st.number_input("Knitting / Weaving / Kg", min_value=0.0, value=0.90, step=0.05)
    
    with c2:
        st.markdown("### 🎨 Wet Processing & Print")
        dyeing_cost_kg = st.number_input("Dyeing & Finishing / Kg", min_value=0.0, value=1.60, step=0.10)
        print_embroidery = st.number_input("Print / Embroidery per Unit", min_value=0.0, value=0.75, step=0.05)

    with c3:
        st.markdown("### ✂️ CMT & Overheads")
        cmt_unit = st.number_input("Stitching (CMT) per Unit", min_value=0.0, value=2.50, step=0.10)
        trims_unit = st.number_input("Trims & Packaging per Unit", min_value=0.0, value=0.80, step=0.05)
        overhead_pct = st.number_input("Factory Overhead Allowance (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.5)

# --- CALCULATIONS ---
gross_fabric_weight = calculated_weight * (1 + (yarn_loss / 100))
fabric_cost_per_kg = yarn_cost_kg + knitting_cost_kg + dyeing_cost_kg
fabric_cost_unit = gross_fabric_weight * fabric_cost_per_kg

direct_unit_cost = fabric_cost_unit + print_embroidery + cmt_unit + trims_unit
total_unit_cost = direct_unit_cost * (1 + (overhead_pct / 100))

fob_price = total_unit_cost / (1 - (target_profit / 100))
profit_per_unit = fob_price - total_unit_cost

total_order_cost = total_unit_cost * order_qty
total_order_revenue = fob_price * order_qty
total_order_profit = profit_per_unit * order_qty

# --- TAB 3: MARGIN CLUES ---
with tab_analytics:
    st.subheader("Financial Unit Breakdown")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fabric Cost / Unit", f"{curr_code} {fabric_cost_unit:.2f}")
    m2.metric("Total Cost / Unit", f"{curr_code} {total_unit_cost:.2f}")
    m3.metric("FOB Price / Unit", f"{curr_code} {fob_price:.2f}")
    m4.metric("Profit / Unit", f"{curr_code} {profit_per_unit:.2f}")
    
    st.markdown("---")
    chart_col, data_col = st.columns([3, 2])
    
    df_cost = pd.DataFrame({
        "Cost Component": ["Raw Fabric", "Print/Embroidery", "CMT (Stitching)", "Trims & Packaging", "Factory Overhead"],
        "Amount": [fabric_cost_unit, print_embroidery, cmt_unit, trims_unit, total_unit_cost - direct_unit_cost]
    })
    
    with chart_col:
        fig = px.pie(df_cost, names="Cost Component", values="Amount", title="Cost Allocation Breakdown", hole=0.5)
        st.plotly_chart(fig, use_container_width=True)
        
    with data_col:
        st.write("### Detailed Cost Breakdown")
        df_cost["Percentage"] = (df_cost["Amount"] / total_unit_cost) * 100
        df_cost["Amount"] = df_cost["Amount"].apply(lambda x: f"{curr_code} {x:.2f}")
        df_cost["Percentage"] = df_cost["Percentage"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_cost, hide_index=True, use_container_width=True)

# --- TAB 4: FINAL VERDICT ---
with tab_export:
    st.subheader("Order Level Verdict & Export")
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Order Cost", f"{curr_code} {total_order_cost:,.2f}")
    s2.metric("Total Revenue", f"{curr_code} {total_order_revenue:,.2f}")
    s3.metric("Net Projected Profit", f"{curr_code} {total_order_profit:,.2f}")
    
    summary_export = pd.DataFrame([{
        "Order Quantity": order_qty,
        "Fabric Type": fabric_type,
        "GSM": gsm,
        "Unit Cost": round(total_unit_cost, 2),
        "FOB Price/Unit": round(fob_price, 2),
        "Total Revenue": round(total_order_revenue, 2),
        "Total Profit": round(total_order_profit, 2)
    }])
    
    st.markdown("---")
    csv = summary_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Case Report (CSV)",
        data=csv,
        file_name=f"textile_detective_report_{order_qty}_units.csv",
        mime="text/csv"
    )