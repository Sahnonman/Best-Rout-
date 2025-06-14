
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Transport Optimizer", page_icon="🚛")

st.title("🚛 Transport Route Optimizer (with Fixed Distances)")
st.markdown("Upload your demand data file. The app will compute distances and costs automatically.")

# Fixed distances
DISTANCES = {
    ("Dammam", "Jeddah"): 1350,
    ("Jeddah", "Madinah"): 420,
    ("Jeddah", "Riyadh"): 950,
    ("Jeddah", "Tabuk"): 1020,
    ("Jeddah", "Abha"): 690,
    ("Dammam", "Abha"): 1300,
    ("Dammam", "Riyadh"): 400,
    ("Dammam", "Qassim"): 500,
    ("Jeddah", "Qassim"): 900,
    ("Dammam", "Tabuk"): 1550
}

uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Routes")
    expected_columns = ["From", "To", "Demand", "Company_Cost_per_km", "3PL_Cost_per_km"]
    if not all(col in df.columns for col in expected_columns):
        st.error(f"❌ The file must contain columns: {expected_columns}")
    else:
        st.success("✅ File loaded successfully!")
        distances = []
        company_costs = []
        pl3_costs = []

        for _, row in df.iterrows():
            route_key = (row["From"], row["To"])
            distance = DISTANCES.get(route_key, 0)
            distances.append(distance)

            company_cost = distance * row["Company_Cost_per_km"] * row["Demand"]
            pl3_cost = distance * row["3PL_Cost_per_km"] * row["Demand"]
            company_costs.append(company_cost)
            pl3_costs.append(pl3_cost)

        df["Distance_km"] = distances
        df["Company_Cost"] = company_costs
        df["3PL_Cost"] = pl3_costs

        st.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="⬇️ Download Result with Costs",
            data=output,
            file_name="Route_Costs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("📌 Please upload a file to start.")
