
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Transport Optimizer", page_icon="🚛")

st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
    }
    .stButton>button {
        background-color: #FFA500;
        color: white;
    }
    .stDownloadButton>button {
        background-color: #007acc;
        color: white;
    }
    .stNumberInput>div>div>input {
        background-color: #fff3e0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚛 Transport Route Optimizer (Cost-Based Decision)")
st.markdown("""
<div style='color:#007acc; font-size:20px;'>
Upload demand data (From, To, Demand, Company_Cost, 3PL_Cost).<br>
The app will distribute total company trucks on routes for optimal cost.
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Routes")
    st.success("✅ File loaded successfully!")
    st.dataframe(df.style.set_properties(**{'background-color': '#e3f2fd'}))

    total_trucks = st.number_input("🚛 Enter total company trucks available:", min_value=0, value=10)

    df["Cost_Diff"] = df["3PL_Cost"] - df["Company_Cost"]
    df = df.sort_values(by="Cost_Diff", ascending=False)

    trucks_left = total_trucks
    results = []

    for _, row in df.iterrows():
        demand = row["Demand"]
        use_trucks = min(demand, trucks_left)
        trucks_left -= use_trucks
        remaining = demand - use_trucks

        company_cost = use_trucks * row["Company_Cost"]
        pl3_cost = remaining * row["3PL_Cost"]
        total_cost = company_cost + pl3_cost

        decision = []
        if use_trucks > 0:
            decision.append(f"{use_trucks} trips by Company Truck")
        if remaining > 0:
            decision.append(f"{remaining} trips by 3PL")

        results.append({
            "From": row["From"],
            "To": row["To"],
            "Company_Trips": use_trucks,
            "3PL_Trips": remaining,
            "Company_Cost": company_cost,
            "3PL_Cost": pl3_cost,
            "Total_Cost": total_cost,
            "Decision": " + ".join(decision)
        })

    result_df = pd.DataFrame(results)
    
    st.subheader("📊 Optimized Distribution Result")
    st.dataframe(result_df.style.set_properties(**{'background-color': '#fffde7'}))

    st.subheader("🚦 Route Decisions")
    for _, row in result_df.iterrows():
        st.markdown(f"""<div style='background-color:#e3f2fd; padding:8px; border-radius:5px;'>
        <strong>{row['From']} ➡ {row['To']}</strong> : {row['Decision']} (Total Cost: {row['Total_Cost']} SAR)
        </div>""", unsafe_allow_html=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        result_df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="⬇️ Download Optimized Plan as Excel",
        data=output,
        file_name="Optimized_Route_Distribution.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("📌 Please upload a file to start optimization.")
