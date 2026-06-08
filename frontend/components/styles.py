import streamlit as st

def inject_premium_styles():
    """Injects comprehensive professional CSS styles into the Streamlit session."""
    st.markdown(
        """
        <style>
        /* Import outfit font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Outfit', sans-serif;
        }

        /* Gradient header card styling */
        .brand-header-card {
            background: linear-gradient(135deg, #1E3A8A 0%, #0D9488 100%);
            padding: 30px;
            border-radius: 16px;
            color: white;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .brand-header-card h1 {
            color: #FFFFFF !important;
            font-size: 32px !important;
            font-weight: 700 !important;
            margin-bottom: 5px !important;
        }
        
        .brand-header-card p {
            font-size: 16px;
            font-weight: 300;
            opacity: 0.9;
            margin: 0;
        }

        /* Glassmorphism card dashboard KPIs */
        .kpi-card {
            background-color: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            text-align: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .kpi-title {
            color: #64748B;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .kpi-value {
            color: #1E293B;
            font-size: 28px;
            font-weight: 700;
        }

        /* Citation Badge styling */
        .citation-chip {
            display: inline-flex;
            align-items: center;
            background-color: #F1F5F9;
            color: #1E293B;
            border: 1px solid #E2E8F0;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-weight: 500;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: background-color 0.2s ease;
        }
        
        .citation-chip:hover {
            background-color: #E2E8F0;
            cursor: pointer;
        }

        .citation-idx {
            background-color: #2563EB;
            color: white;
            border-radius: 50%;
            width: 16px;
            height: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 700;
            margin-right: 6px;
        }
        
        .citation-score {
            color: #0D9488;
            font-weight: 600;
            margin-left: 6px;
            font-size: 10px;
            background-color: #F0FDFA;
            padding: 1px 4px;
            border-radius: 4px;
            border: 1px solid #CCFBF1;
        }

        /* Beautiful sidebar tweak */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #F8FAFC !important;
        }
        
        /* Sidebar active link / sidebar buttons */
        [data-testid="stSidebar"] button {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #F8FAFC !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-color: #6366F1 !important;
        }

        /* Custom buttons styling */
        .stButton>button {
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            font-weight: 500 !important;
        }
        
        /* Secondary action buttons */
        .stButton>button[kind="secondary"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            color: #475569 !important;
        }
        .stButton>button[kind="secondary"]:hover {
            border-color: #6366F1 !important;
            color: #6366F1 !important;
        }

        /* Card blocks */
        .library-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #E2E8F0;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }

        /* Styled scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #F1F5F9;
        }
        ::-webkit-scrollbar-thumb {
            background: #CBD5E1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94A3B8;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
