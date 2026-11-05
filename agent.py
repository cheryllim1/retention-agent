import duckdb
from langchain_community.llms import Ollama

# Connect directly to your DuckDB database file
con = duckdb.connect("analytics.duckdb")


def get_at_risk_vip_customers():
  # Query the dbt model table for high-value churn-risk customers
  query = """
        SELECT customer_id, total_spend, days_since_last_order 
        FROM main.dim_customers 
        WHERE churn_risk_status = 'High Churn Risk'
        LIMIT 3
    """
  return con.execute(query).fetchall()


# Initialize the free local LLM running via Ollama
llm = Ollama(model="llama3")


def generate_retention_campaign(customer_id, total_spend, days_silent):
  prompt = f"""
    You are an expert MarTech Retention Specialist.
    Customer ID {customer_id} is a VIP who has spent Rs.{total_spend:.2f} but hasn't purchased in {days_silent} days.
    
    Draft a concise, compelling win-back email offering a tailored incentive 
    that feels personal and encourages them to return to our store.
    """
  return llm.invoke(prompt)


if __name__ == "__main__":
  print("--- Querying dbt Semantic Layer for Churn-Risk VIPs ---")
  vip_churns = get_at_risk_vip_customers()

  if not vip_churns:
    print(
        "No customers found matching the filter criteria. Try lowering the"
        " spend threshold."
    )
  else:
    for cust in vip_churns:
      print(f"\n[AI Agent] Generating Win-Back for Customer: {cust[0]}")
      print(f"Lifetime Spend: Rs.{cust[1]} | Days Since Last Order: {cust[2]}")
      email_draft = generate_retention_campaign(cust[0], cust[1], cust[2])
      print("\n--- Generated Email Draft ---")
      print(email_draft)
      print("-" * 40)