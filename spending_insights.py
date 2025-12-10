
import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import io
import os
from dotenv import load_dotenv
def main():
    # ---------- CONFIG ----------
    st.set_page_config(page_title="Spending Insights", page_icon="📊", layout="wide")
    load_dotenv()
    # ---- Your Gemini API Key (HARD-CODED) ----
    api_key = os.getenv("GEMINI_API_KEY")  # Replace with your key
    genai.configure(api_key=api_key)

    # ---- Custom Styling ----
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    body { cursor: url('https://cur.cursors-4u.net/cursors/cur-2/cur114.cur'), auto; }
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    h1, h2, h3 { color: gold !important; }
    </style>
    """, unsafe_allow_html=True)

    # ---- Load or Initialize Transaction Storage ----
    HISTORY_FILE = "transactions_history.csv"

    if os.path.exists(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)
    else:
        history_df = pd.DataFrame(columns=["date", "category", "amount"])

    if "transactions" not in st.session_state:
        st.session_state.transactions = []

    # ---- Page Title ----
    st.title("📊 Spending Insights")

    # ---- Transaction Input ----
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("➕ Add a Transaction")

    col1, col2, col3 = st.columns(3)
    with col1:
        t_date = st.date_input("Date", value=date.today())
    with col2:
        t_category_choice = st.selectbox("Category", ["Food", "Travel", "Entertainment", "Bills", "Shopping", "Medical", "Education", "Investments", "Insurance", "Savings", "Other"])
        if t_category_choice == "Other":
            t_category = st.text_input("Enter custom category")
        else:
            t_category = t_category_choice
    with col3:
        t_amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)

    if st.button("Add Transaction", use_container_width=True):
        if not t_category:
            st.error("Please enter a category.")
        else:
            new_entry = {
                "date": str(t_date),
                "category": t_category,
                "amount": t_amount
            }
            st.session_state.transactions.append(new_entry)

            # Save to CSV for persistence
            df_all = pd.DataFrame(st.session_state.transactions)
            df_all.to_csv(HISTORY_FILE, index=False)

            st.success(f"Transaction added — {t_category} | ₹{t_amount} | {t_date}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Show Transactions ----
    if st.session_state.transactions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📄 Current Session Transactions")
        df = pd.DataFrame(st.session_state.transactions)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- Option to View Full History ----
    if st.checkbox("📜 Show Full Transaction History"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Full Transaction History")
        st.dataframe(history_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- AI Insights Section ----
    if st.button("🔍 Generate Insights", use_container_width=True):
        if not st.session_state.transactions:
            st.error("Please add at least one transaction.")
        else:
            df = pd.DataFrame(st.session_state.transactions)

            category_sum = df.groupby("category")["amount"].sum()
            percentages = (category_sum / category_sum.sum()) * 100

            fig, ax = plt.subplots(figsize=(2.5, 2.5))  # much smaller figure
            ax.pie(
                percentages,
                labels=percentages.index,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 8}
            )
            ax.axis('equal')

            # Save as image buffer instead of letting Streamlit resize
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=300)
            buf.seek(0)

            st.subheader("📌 Category-wise Spending Breakdown")
            st.image(buf,width=400) 
            # --- 2. AI Insights for Trends & Spikes (Using Full History) ---
            prompt = f"""
            You are a personal finance assistant used in India.
            Analyze the following ENTIRE spending history:
            {history_df.to_dict(orient='records')}

            Provide:
            1. Trends compared to previous month (assume missing data if not provided)
            2. Highlight any unusual spikes
            don't give any other recommendations and only want these
            """

            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
                insights_text = response.text.strip()

                st.subheader("🤖 AI Insights & Trends")
                st.markdown(insights_text)
            except Exception as e:
                st.error(f"Error fetching insights: {e}")


if __name__ == "__main__":
    main()