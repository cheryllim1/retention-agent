import duckdb
import requests
import streamlit as st

# Set page layout
st.set_page_config(
    page_title="Autonomous Retention Operations", layout="wide"
)

st.title("⚡ MarTech Autonomous Retention & ERP Agent")
st.caption(
    "Powered by DuckDB Semantic Layer, dbt, and Local Llama 3 Inference"
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
                customer_id,
                COUNT(order_id) AS total_orders,
                SUM(amount) AS total_spend,
                CAST(date_diff('day', MAX(order_date), CURRENT_DATE) AS INTEGER) AS days_since_last_order,
                CASE 
                    WHEN date_diff('day', MAX(order_date), CURRENT_DATE) > 90 THEN 'High Churn Risk'
                    WHEN date_diff('day', MAX(order_date), CURRENT_DATE) > 30 THEN 'Medium Churn Risk'
                    ELSE 'Active'
                END AS churn_risk_status
            FROM 'ecommerce_dataset_updated.csv'
            GROUP BY customer_id
        """)
    return con

con = get_db_connection()


# Direct function to query local Ollama server (Super fast, no hanging)
def generate_with_ollama(prompt):
  url = "http://localhost:11434/api/generate"
  payload = {"model": "llama3", "prompt": prompt, "stream": False}
  try:
    response = requests.post(url, json=payload, timeout=160)
    if response.status_code == 200:
      return response.json().get("response", "Error parsing response.")
    else:
      return f"Ollama Error: {response.text}"
  except Exception as e:
    return (
        f"Connection Error: Could not connect to Ollama. Is it running? ({e})"
    )


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
  st.subheader("🤖 Trigger Agentic Retention Campaign")
  selected_customer = st.selectbox(
      "Select Customer ID to Target", df["customer_id"]
  )

  cust_data = df[df["customer_id"] == selected_customer].iloc[0]

  if st.button("Generate Personalized Win-Back Email"):
    with st.spinner("Local Llama 3 LLM drafting retention copy..."):
      prompt = f"""
            You are an expert MarTech Retention Specialist. Write a short win-back email for VIP Customer {cust_data['customer_id']} 
     who has spent Rs.{cust_data['total_spend']:.2f} and been inactive for {cust_data['days_since_last_order']} days. 
     Include a 15% discount code VIP15. Keep it concise and end email with a CTA.
            """
      email_copy = generate_with_ollama(prompt)

    st.success("Campaign Drafted!")
    st.text_area("Generated Campaign Copy", email_copy, height=300)