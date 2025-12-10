
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
import io
import re
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from dotenv import load_dotenv
def main():
    # --- CONFIG ---
    st.set_page_config(page_title="💰 Budget Summary", page_icon="💰", layout="wide")
    load_dotenv()
    # --- Gemini API ---
    api_key = os.getenv("GEMINI_API_KEY3")  # Replace with your key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # --- Load Spending Data ---
    HISTORY_FILE = "transactions_history.csv"
    if not os.path.exists(HISTORY_FILE):
        st.error("No transaction history found. Please add transactions in Spending Insights first.")
        st.stop()

    history_df = pd.read_csv(HISTORY_FILE)

    # --- UI ---
    st.title("💰 Budget Summaries & AI Suggestions")
    st.markdown("This page analyzes your past spending and suggests ways to optimize your budget.")

    # --- User Budget Inputs ---
    total_budget = st.number_input("Enter your total monthly budget (₹)", min_value=1000, step=500)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        needs_percent = st.slider("Needs (%)", 0, 100, 50)
    with col2:
        wants_percent = st.slider("Wants (%)", 0, 100, 30)
    with col3:
        savings_percent = st.slider("Savings (%)", 0, 100, 10)
    with col4:
        investments_percent = st.slider("Investments (%)", 0, 100, 10)

    allocation_percentages = {
        "needs": needs_percent,
        "wants": wants_percent,
        "savings": savings_percent,
        "investments": investments_percent
    }
    if "percentages" not in st.session_state:
        st.session_state.percentages = None
    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None

    # --- Generate Analysis ---
    if st.button("📊 Analyze Budget & Get Suggestions", use_container_width=True):
        category_totals = history_df.groupby("category")["amount"].sum().to_dict()

        prompt = f"""
        You are a financial advisor AI.
        Categorize each category from the spending data into:
        - needs
        - wants
        - savings
        - investments

        Then:
        1. Calculate totals for each main category.
        2. Compare with the user's budget allocation.
        3. Return in **valid JSON only** with this structure:
        {{
          "summary": {{
            "needs": {{"spent": number, "limit": number, "status": "ok/exceeded"}},
            "wants": {{"spent": number, "limit": number, "status": "ok/exceeded"}},
            "savings": {{"spent": number, "limit": number, "status": "ok/exceeded"}},
            "investments": {{"spent": number, "limit": number, "status": "ok/exceeded"}}
          }},
          "advice": "Full paragraph(s) of budget optimization advice for the user."
        }}

        Spending Data: {category_totals}
        Total Monthly Budget: {total_budget}
        Allocation Percentages: {allocation_percentages}
        """

        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

            # Extract JSON in case model adds extra text
            json_match = re.search(r"\{[\s\S]*\}", raw_text)
            if json_match:
                raw_text = json_match.group()

            parsed_data = json.loads(raw_text)

            # Store in session state
            st.session_state.parsed_data = parsed_data
            # --- Display Summary ---
            st.subheader("📌 Budget Summary")
            for section, values in parsed_data["summary"].items():
                st.markdown(f"### {section.capitalize()}")
                st.markdown(f"- **Spent:** ₹{values['spent']}")
                st.markdown(f"- **Limit:** ₹{values['limit']}")
                st.markdown(f"- **Status:** {'✅ OK' if values['status']=='ok' else '⚠️ Exceeded'}")

            # --- Display Advice ---
            st.subheader("💡 Fibot Advice")
            st.markdown(parsed_data["advice"])

            # --- Pie Chart ---
            st.subheader("📊 Spending Breakdown")
            percentages = (history_df.groupby("category")["amount"].sum() /
                           history_df["amount"].sum()) * 100
            st.session_state.percentages = percentages
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(percentages, labels=percentages.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=300)
            buf.seek(0)
            st.image(buf, width=400)

        except Exception as e:
            st.error(f"Error: {e}")
            
    if st.button("📄 Download PDF Report"):
        if st.session_state.percentages is None or st.session_state.parsed_data is None:
            st.error("⚠️ Please run the analysis first before downloading the PDF.")
        else:
            try:
                percentages = st.session_state.percentages
                parsed_data = st.session_state.parsed_data

                # Save pie chart to buffer
                pie_img_buf = io.BytesIO()
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(percentages, labels=percentages.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                plt.savefig(pie_img_buf, format="PNG", dpi=300)
                pie_img_buf.seek(0)

                # Create PDF
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                width, height = letter

                # Title
                c.setFont("Helvetica-Bold", 16)
                c.drawString(200, height - 50, "Budget Summary Report")

                # Summary Section
                y_position = height - 100
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, "📌 Budget Summary")
                c.setFont("Helvetica", 10)
                y_position -= 20
                for section, values in parsed_data["summary"].items():
                    c.drawString(60, y_position, f"{section.capitalize()}:")
                    y_position -= 15
                    c.drawString(80, y_position, f"Spent: ₹{values['spent']}")
                    y_position -= 15
                    c.drawString(80, y_position, f"Limit: ₹{values['limit']}")
                    y_position -= 15
                    c.drawString(80, y_position, f"Status: {values['status']}")
                    y_position -= 20

                # Advice Section with Wrapping
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, "💡 Fibot Advice")
                y_position -= 20
                c.setFont("Helvetica", 10)
                text_object = c.beginText(60, y_position)

                max_width = 80
                wrapped_lines = []
                for line in parsed_data["advice"].split("\n"):
                    wrapped_lines.extend(wrap(line, width=max_width))
                for wl in wrapped_lines:
                    text_object.textLine(wl)
                c.drawText(text_object)

                # New Page for Pie Chart
                c.showPage()
                img_width = 300
                img_height = 300
                x_pos = (width - img_width) / 2
                y_pos = (height - img_height) / 2
                c.drawImage(ImageReader(pie_img_buf), x_pos, y_pos, width=img_width, height=img_height)

                # Save PDF
                c.save()
                pdf_buffer.seek(0)

                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_buffer,
                    file_name="budget_summary_report.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error generating PDF: {e}")


if __name__ == "__main__":
    main()