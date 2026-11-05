MarTech Autonomous Retention & ERP Agent

An enterprise-grade, $0-stack customer churn prediction and automated retention marketing prototype combining data engineering, semantic layers, and local generative AI.

Tech Stack
Data Storage & Modeling: DuckDB & dbt-core
Cloud LLM: Groq API (`openai/gpt-oss-20b`)
Interactive UI: Stramlit
Language: Python

Architecture
Semantic Layer: Queries cleaned customer dimensions and churn risk status from DuckDB
Agentic Layer: Dynamically injects customer lifetime spend and inactivity metrics into prompt templates
Execution Layer: Triggers local Llama 3 generation to output personalised win-back email copy with discount incentives with a CTA at the end of the email. 
