import streamlit as st
from urllib.parse import urlencode
import budget_summaries
import spending_insights
import NLU_Analysis
import rag_granite_finance
import about_fibot
st.set_page_config(page_title="Fibot - Financial Advice Assistant", page_icon="💰", layout="wide")

# Custom CSS + Animation
st.markdown("""
    <style>
    body {
        background-color: #0E0E0F;
        color: white;
        font-family: "Segoe UI", sans-serif;
    }
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 20px 60px;
    }
    .fibot-name {
        font-size: 2.2em;
        font-weight: bold;
        color: white;
        margin-left: -20px;
    }
    .top-right {
        text-align: right;
        margin-right: -20px;
    }
    .login-btn {
        background-color: #0E0E0F;
        color: white;
        border: 1px solid white;
        padding: 6px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9em;
    }
    .nav-links {
        margin-top: 8px;
    }
    .nav-links a {
        color: #ccc;
        text-decoration: none;
        margin-left: 15px;
        font-size: 0.85em;
    }
    .center-section {
        text-align: center;
        padding-top: 4vh;
        padding-bottom: 5vh;
    }
    .headline {
        font-size: 2.3em;
        font-weight: bold;
        line-height: 1.2;
    }
    .subhead {
        font-size: 1.5em;
        color: #aaa;
        margin-top: 12px;
        margin-bottom: 25px;
    }
    .btn-primary {
        background-color: white;
        color: blue;
        border: none;
        padding: 10px 20px;
        border-radius: 24px;
        font-size: 1em;
        cursor: pointer;
        margin-right: 15px;
    }
    .btn-link {
        color: #0E6FFF;
        background: none;
        border: none;
        font-size: 1em;
        cursor: pointer;
        text-decoration: underline;
    }
    .scroll-row {
        display: flex;
        overflow: hidden;
        white-space: nowrap;
        background-color: #0E0E0F;
        padding: 10px 0;
    }
    .scroll-content {
        display: inline-flex;
        animation: scroll-left 25s linear infinite;
    }
    .scroll-content-reverse {
        display: inline-flex;
        animation: scroll-right 25s linear infinite;
    }
    @keyframes scroll-left {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }
    @keyframes scroll-right {
        0% { transform: translateX(-50%); }
        100% { transform: translateX(0); }
    }
    .question-card {
        display: inline-block;
        background-color: #1A1A1B;
        color: white;
        padding: 10px 16px;
        margin: 0 8px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 0.95em;
        border: 1px solid #333;
        transition: background 0.2s;
    }
    .question-card:hover {
        background-color: #2C2C2E;
    }
    </style>
""", unsafe_allow_html=True)
if "show_sip" not in st.session_state:
    st.session_state.show_sip = False
if "show_swp" not in st.session_state:
    st.session_state.show_swp = False

col1, col2, col3 = st.columns([8, 1, 1])
with col1:
    st.title("Fibot")
with col2:
    if st.button("SIP"):
        st.session_state.show_sip = True
with col3:
    if st.button("SWP"):
        st.session_state.show_swp = True
@st.dialog("SIP Calculator")
def sip_modal():
    monthly_investment = st.number_input("Monthly Investment (₹)", value=5000)
    annual_rate = st.number_input("Expected Annual Return (%)", value=12.0)
    years = st.number_input("Investment Duration (Years)", value=10)
    if st.button("Calculate SIP Returns"):
        r = annual_rate / 12 / 100
        months = years * 12
        maturity_value = monthly_investment * (((1 + r)**months - 1) / r) * (1 + r)
        st.success(f"Maturity Value: ₹{maturity_value:,.2f}")
@st.dialog("SWP Calculator")
def swp_modal():
    initial_investment = st.number_input("Initial Investment (₹)", value=1000000)
    withdrawal_amount = st.number_input("Monthly Withdrawal (₹)", value=10000)
    annual_rate = st.number_input("Expected Annual Return (%)", value=8.0)
    years = st.number_input("Withdrawal Duration (Years)", value=10)
    if st.button("Calculate SWP Balance"):
        r = annual_rate / 12 / 100
        months = years * 12
        balance = initial_investment
        for _ in range(months):
            balance = balance * (1 + r) - withdrawal_amount
            if balance < 0:
                balance = 0
                break
        st.success(f"Final Balance: ₹{balance:,.2f}")
# Open dialogs
if st.session_state.show_sip:
    sip_modal()
    st.session_state.show_sip = False
if st.session_state.show_swp:
    swp_modal()
    st.session_state.show_swp = False
# Function to build navigation links
def nav_link(label, page):
    query_params = urlencode({"page": page})
    return f'<a href="?{query_params}" target="_self" style="color:#ccc; text-decoration:none; margin-left:15px;">{label}</a>'

# 🔹 UPDATED: Navigation links placed below buttons in pure Streamlit instead of HTML block
st.markdown(
    f"""
    <div class="nav-links" style="text-align:right; margin-top:5px;">
        {nav_link("Finance Chatbot", "chatbot")}
        {nav_link("Budget Summary", "budget")}
        {nav_link("Spending Insights", "spending")}
        {nav_link("NLU Analysis", "nlu")}
        {nav_link("Home", "home")}
    </div>
    """,
    unsafe_allow_html=True
)

# --- PAGE LOADING ---
params = st.query_params
page = params.get("page", "home")
if page == "chatbot" or page=="try":
    rag_granite_finance.main()
elif page == "budget":
    budget_summaries.main()
elif page == "spending":
    spending_insights.main()
elif page == "nlu":
    NLU_Analysis.main()
elif page == "know":
    about_fibot.main()
else: 
 # Default to home page
# Center section
    st.markdown(f"""
    <div class="center-section">
        <div class="headline">Financial freedom is not a dream, it's a plan.</div>
        <div class="subhead">Your personal financial advice assistant</div>
        <button class="btn-primary">
            {nav_link("Try Fibot", "try")}
        </button>
        <button class="btn-link">
            {nav_link("Know More", "know")}
        </button>
    </div>
    """, unsafe_allow_html=True)
    # Scrollable row of questions
    # Questions
    questions_row1 = [
        "How can I save more each month?",
        "What's the best way to invest ₹10,000?",
        "How to create a budget?",
        "Tips to pay off debt faster?",
    ]
    questions_row2 = [
        "Should I start a SIP now?",
        "How to improve my credit score?",
        "Best tax saving options in India?",
        "How to plan for retirement?",
    ]

    def render_row(questions, reverse=False):
        content_class = "scroll-content-reverse" if reverse else "scroll-content"
        html = f'<div class="scroll-row"><div class="{content_class}">'
        for q in questions * 2:
            # Escape single quotes to prevent JavaScript errors
            escaped_q = q.replace("'", "\\'")
            html += f'<div class="question-card" onclick="setQuestion(\'{escaped_q}\')">{q}</div>'
        html += "</div></div>"
        return html

    st.markdown(render_row(questions_row1), unsafe_allow_html=True)
    st.markdown(render_row(questions_row2, reverse=True), unsafe_allow_html=True)

    # JavaScript to set chat input
    st.markdown("""
    <script>
    function setQuestion(q) {
        const input = window.parent.document.querySelector('textarea[aria-label="Chat input"]');
        if(input){
            input.value = q;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    </script>
    """, unsafe_allow_html=True)