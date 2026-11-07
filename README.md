MarTech Autonomous Retention & ERP Agent <br>
<br>
An enterprise-grade, $0-stack customer churn prediction and automated retention marketing prototype combining data engineering, semantic layers, and local generative AI. <br>
<br>
Tech Stack <br>
Data Storage & Modeling: DuckDB & dbt-core <br>
Cloud LLM: Groq API (`openai/gpt-oss-20b`) <br>
Interactive UI: Stramlit <br>
Language: Python <br>
<br>
Architecture <br>
Semantic Layer: Queries cleaned customer dimensions and churn risk status from DuckDB <br>
Agentic Layer: Dynamically injects customer lifetime spend and inactivity metrics into prompt templates <br>
Execution Layer: Triggers local Llama 3 generation to output personalised win-back email copy with discount incentives with a CTA at the end of the email. <br>
<br>
Access Streamlit  here: https://retention-agent-e4sryf9l7z6nzzvus9soym.streamlit.app/
