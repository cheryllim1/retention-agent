import duckdb
import requests
import streamlit as st

# Set page layout
st.set_page_config(
    page_title="Autonomous Retention Operations", layout="wide"
)

st.title("⚡ MarTech Autonomous Retention & ERP Agent")
st.caption(
    "Prototype by CHERYL LIM"
)


# Cache DB connection and auto-initialize table if missing on Cloud
@st.cache_resource
def get_db_connection():
    con = duckdb.connect("analytics.duckdb")
    
    # Check if dim_customers exists; if not, build it from the CSV on the fly
    tables = [row[0] for row in con.execute("SHOW TABLES").fetchall()]
    if "dim_customers" not in tables:
        con.execute("""
            CREATE TABLE IF NOT EXISTS main.dim_customers AS 
            SELECT 
                User_ID AS customer_id,
                COUNT(*) AS total_orders,
                SUM("Final_Price(Rs.)") AS total_spend,
                CAST(date_diff('day', MAX(CAST(Purchase_Date AS DATE)), CURRENT_DATE) AS INTEGER) AS days_since_last_order,
                CASE 
                    WHEN date_diff('day', MAX(CAST(Purchase_Date AS DATE)), CURRENT_DATE) > 90 THEN 'High Churn Risk'
                    WHEN date_diff('day', MAX(CAST(Purchase_Date AS DATE)), CURRENT_DATE) > 30 THEN 'Medium Churn Risk'
                    ELSE 'Active'
                END AS churn_risk_status
            FROM read_csv_auto('ecommerce_dataset_updated.csv', header=True)
            GROUP BY User_ID
        """)
    return con

con = get_db_connection()


# Function to query Groq's free cloud API
def generate_with_cloud_ai(prompt):
    # Retrieve the API key from Streamlit secrets securely
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return "Error: GROQ_API_KEY not found in Streamlit Secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-20b",  # Blazing fast, free-tier friendly model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"API Error: {response.text}"
    except Exception as e:
        return f"Connection Error: {e}"


# Sidebar Filters
st.sidebar.header("Customer Segmentation Filters")
risk_filter = st.sidebar.selectbox(
    "Churn Risk Status", ["High Churn Risk", "Medium Churn Risk", "Active"]
)
min_spend = st.sidebar.number_input("Minimum Total Spend (Rs.)", value=0.0)

# Query semantic layer
query = f"""
    SELECT customer_id, total_orders, total_spend, days_since_last_order, churn_risk_status 
    FROM main.dim_customers 
    WHERE churn_risk_status = '{risk_filter}' AND total_spend >= {min_spend}
    LIMIT 10
"""
df = con.execute(query).df()

st.subheader("At-Risk Customer Segment")
st.dataframe(df, width="stretch")

if not df.empty:
    st.subheader("Trigger Agentic Retention Campaign")
    selected_customer = st.selectbox(
        "Select Customer ID to Target", df["customer_id"]
    )
    
    cust_data = df[df["customer_id"] == selected_customer].iloc[0]

    if st.button("Generate Personalized Win-Back Email"):
        with st.spinner("Generating AI retention copy via Groq..."):
            prompt = f"""
                You are an expert MarTech Retention Specialist. Write a short win-back email for Customer {cust_data['customer_id']} 
                who has spent Rs.{cust_data['total_spend']:.2f} and been inactive for {cust_data['days_since_last_order']} days. 
                Include a 15% discount code VIP15. Keep it concise and end email with a CTA.
            """
            email_copy = generate_with_cloud_ai(prompt)

        st.success("Campaign Drafted!")
        st.text_area("Generated Campaign Copy", email_copy, height=300)