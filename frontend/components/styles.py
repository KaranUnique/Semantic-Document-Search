import streamlit as st


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        :root {
            --bg: #F7F7F8; --surface: #FFFFFF; --border: #EBEBED; --border-lt: #F3F3F5;
            --t1: #111318; --t2: #5C5F6A; --t3: #9EA3AF;
            --accent: #E8483A; --green: #12B76A; --green-bg: #ECFDF5;
            --amber: #F59E0B; --amber-bg: #FFFBEB; --blue: #3B82F6;
            --r-sm: 6px; --r-md: 10px; --r-lg: 14px;
            --shadow: 0 1px 4px rgba(0,0,0,0.07);
        }
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif !important;
            background: var(--bg) !important;
            color: var(--t1) !important;
        }
        #MainMenu, footer, header,
        [data-testid="stDecoration"],
        [data-testid="stToolbar"] { display: none !important; }
        .block-container { padding: 20px !important; max-width: 100% !important; }
        [data-testid="stSidebar"] {
            background: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
            min-width: 240px !important; max-width: 240px !important;
        }
        [data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
        [data-testid="stSidebar"] .block-container { padding: 0 !important; }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0 !important; padding: 18px 12px !important;
        }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none !important; }
        .sb-profile { display:flex; align-items:center; gap:10px; padding:4px 4px 16px; }
        .sb-avatar {
            width:36px; height:36px; border-radius:8px;
            background:linear-gradient(135deg,#667EEA,#764BA2);
            color:#fff; font-size:12px; font-weight:700;
            display:flex; align-items:center; justify-content:center; flex-shrink:0;
        }
        .sb-name { font-size:14px; font-weight:600; color:var(--t1); }
        .sb-caret { font-size:11px; color:var(--t3); margin-left:2px; }
        .sb-divider { height:1px; background:var(--border); margin:6px 0; }
        .sb-label {
            font-size:10.5px !important; font-weight:700 !important;
            letter-spacing:0.07em !important; color:var(--t3) !important;
            padding:12px 8px 5px !important; margin:0 !important; display:block;
        }
        [data-testid="stSidebar"] .stButton > button {
            background:transparent !important; border:none !important;
            color:var(--t2) !important; font-size:13.5px !important;
            font-weight:500 !important; text-align:left !important;
            padding:8px 10px !important; border-radius:var(--r-sm) !important;
            width:100% !important; box-shadow:none !important;
            margin-bottom:1px !important;
            transition:background 0.12s, color 0.12s !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background:var(--bg) !important; color:var(--t1) !important;
        }
        .nav-active > button {
            background:var(--t1) !important; color:#fff !important;
            font-weight:600 !important;
        }
        .nav-active > button:hover { background:#23262F !important; color:#fff !important; }
        .sb-tag {
            display:flex; align-items:center; gap:8px;
            font-size:13.5px; color:var(--t2);
            padding:7px 10px; border-radius:var(--r-sm);
        }
        .sb-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
        .sb-dot-red { background:var(--accent); }
        .sb-dot-green { background:var(--green); }
        .sb-settings {
            display:flex; align-items:center; gap:8px;
            font-size:13.5px; color:var(--t2);
            padding:7px 10px; border-radius:var(--r-sm); cursor:pointer;
        }
        .sb-settings:hover { background:var(--bg); }
        .panel {
            background:var(--surface); border:1px solid var(--border);
            border-radius:var(--r-lg); box-shadow:var(--shadow); overflow:hidden;
        }
        .panel-header {
            padding:16px 20px; border-bottom:1px solid var(--border-lt);
            font-size:14px; font-weight:600; color:var(--t1);
        }
        [data-testid="stFileUploader"] {
            border:1.5px dashed var(--border) !important;
            border-radius:var(--r-md) !important;
            background:var(--bg) !important;
            padding:20px 16px !important;
        }
        [data-testid="stFileUploader"]:hover { border-color:var(--t3) !important; }
        [data-testid="stFileUploader"] label { display:none !important; }
        .ftable { width:100%; border-collapse:collapse; }
        .ftable th {
            font-size:11px; font-weight:600; letter-spacing:0.06em;
            color:var(--t3); text-align:left;
            padding:10px 14px; border-bottom:1px solid var(--border-lt);
        }
        .ftable td {
            font-size:13.5px; color:var(--t1);
            padding:12px 14px; border-bottom:1px solid var(--border-lt);
            vertical-align:middle;
        }
        .ftable tr:last-child td { border-bottom:none; }
        .ftable tr:hover td { background:var(--bg); }
        .fname-cell { display:flex; align-items:center; gap:9px; font-weight:500; }
        .ficon {
            width:28px; height:28px; border-radius:6px;
            display:flex; align-items:center; justify-content:center;
            font-size:13px; flex-shrink:0;
        }
        .ficon-pdf  { background:#FEE2E2; }
        .ficon-docx { background:#DBEAFE; }
        .ficon-pptx { background:#FFEDD5; }
        .ficon-txt  { background:#F1F5F9; }
        .ficon-md   { background:#F1F5F9; }
        .badge {
            display:inline-flex; align-items:center;
            padding:3px 9px; border-radius:20px;
            font-size:11.5px; font-weight:600;
        }
        .badge-indexed    { background:var(--green-bg); color:#065F46; }
        .badge-processing { background:var(--amber-bg); color:#92400E; }
        .badge-error      { background:#FEE2E2; color:#991B1B; }
        .chat-ai-bubble {
            background:var(--surface); border:1px solid var(--border);
            border-radius:4px 14px 14px 14px; padding:11px 14px;
            font-size:13.5px; color:var(--t1); line-height:1.55;
            display:inline-block; max-width:85%;
        }
        .chat-user-bubble {
            background:#1C1F27; border-radius:14px 4px 14px 14px;
            padding:11px 14px; font-size:13.5px; color:#F4F5F7;
            line-height:1.55; display:inline-block; max-width:85%;
        }
        .chat-av-ai {
            width:32px; height:32px; border-radius:50%;
            background:#EBEBED; display:flex; align-items:center;
            justify-content:center; font-size:15px; flex-shrink:0;
        }
        .chat-av-user {
            width:32px; height:32px; border-radius:50%;
            background:linear-gradient(135deg,#667EEA,#764BA2);
            color:#fff; font-size:10px; font-weight:700;
            display:flex; align-items:center; justify-content:center; flex-shrink:0;
        }
        .chat-ts { font-size:10px; color:var(--t3); margin-top:4px; }
        .c-chip {
            display:inline-flex; align-items:center; gap:5px;
            background:var(--bg); border:1px solid var(--border);
            border-radius:20px; padding:2px 9px 2px 3px;
            font-size:11px; color:var(--t2); margin:2px 2px 0 0;
        }
        .c-idx {
            background:var(--blue); color:#fff;
            width:16px; height:16px; border-radius:50%;
            display:inline-flex; align-items:center; justify-content:center;
            font-size:9px; font-weight:700; flex-shrink:0;
        }
        .c-score { color:var(--green); font-weight:600; }
        [data-testid="stChatInput"] {
            border:1.5px solid var(--border) !important;
            border-radius:var(--r-md) !important;
            box-shadow:none !important;
            background:var(--surface) !important;
        }
        [data-testid="stChatInput"]:focus-within { border-color:#B0B5BF !important; }
        [data-testid="stChatInput"] textarea {
            font-family:'Inter',sans-serif !important;
            font-size:13.5px !important; color:var(--t1) !important;
        }
        .stButton > button {
            font-family:'Inter',sans-serif !important;
            font-weight:600 !important;
            border-radius:var(--r-sm) !important;
            transition:all 0.13s !important;
        }
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stTextInput"] > div > div {
            border-color:var(--border) !important;
            border-radius:var(--r-sm) !important;
            font-family:'Inter',sans-serif !important;
            font-size:13.5px !important;
        }
        [data-testid="stAlert"] { border-radius:var(--r-md) !important; font-size:13px !important; }
        ::-webkit-scrollbar { width:4px; height:4px; }
        ::-webkit-scrollbar-track { background:transparent; }
        ::-webkit-scrollbar-thumb { background:#D4D7DF; border-radius:3px; }
        [data-testid="stHorizontalBlock"] { gap:16px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
