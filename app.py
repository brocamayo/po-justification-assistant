"""
PO Justification Assistant — Streamlit application entry point.
"""

import base64
import os
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from generator import generate_po_justification
from teams_sender import send_to_teams

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PO Justification Assistant",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# Styles
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        [data-testid="stAppViewContainer"] { background: #F0F4F8; }
        [data-testid="stHeader"]           { background: transparent; }
        .block-container                   { padding-top: 1.5rem; }

        .app-header {
            background: linear-gradient(135deg, #002060 0%, #0066CC 100%);
            padding: 22px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            color: white;
        }
        .app-header h1 { margin: 0; font-size: 26px; font-weight: 700; }
        .app-header p  { margin: 5px 0 0; opacity: 0.80; font-size: 13px; }


        .section-card {
            background: white;
            border-radius: 10px;
            padding: 18px 22px;
            margin-bottom: 14px;
            border-left: 4px solid #0066CC;
            box-shadow: 0 1px 3px rgba(0,0,0,0.07);
        }
        .section-card h3 {
            margin: 0 0 8px;
            color: #002060;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .section-card p {
            margin: 0;
            color: #1A1A2E;
            line-height: 1.70;
            font-size: 14.5px;
        }

        div[data-testid="stButton"] > button {
            border-radius: 6px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _build_export_text(j: dict, user_input: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    divider = "=" * 55
    thin = "-" * 30
    return "\n".join([
        "PURCHASE ORDER JUSTIFICATION",
        divider,
        f"Generated : {now}",
        f"Input     : {user_input}",
        divider,
        "",
        "WHAT",
        thin,
        j["what"],
        "",
        "WHY",
        thin,
        j["why"],
        "",
        "WHY NOW",
        thin,
        j["why_now"],
        "",
        "WHY GOOD VALUE",
        thin,
        j["why_good_value"],
        "",
    ])


def _clipboard_button(text: str) -> None:
    encoded = base64.b64encode(text.encode("utf-8")).decode()
    components.html(
        f"""
        <script>
          function doCopy() {{
            const txt = atob("{encoded}");
            navigator.clipboard.writeText(txt).then(
              () => {{
                const btn = document.getElementById("cp-btn");
                btn.innerText = "✓ Copied!";
                btn.style.background = "#28A745";
                setTimeout(() => {{
                  btn.innerText = "📋 Copy to Clipboard";
                  btn.style.background = "#6C757D";
                }}, 2200);
              }},
              () => alert("Copy failed — please use Export instead.")
            );
          }}
        </script>
        <button id="cp-btn" onclick="doCopy()"
          style="width:100%;background:#6C757D;color:white;border:none;
                 padding:8px 14px;border-radius:6px;cursor:pointer;
                 font-size:14px;font-weight:600;transition:background .2s;">
          📋 Copy to Clipboard
        </button>
        """,
        height=46,
    )


def _section_card(label: str, text: str) -> None:
    safe = text.replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(
        f'<div class="section-card"><h3>{label}</h3><p>{safe}</p></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
      <h1>📋 PO Justification Assistant</h1>
      <p>AI-powered purchase order justifications for manufacturing operations</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# API key guard
# ─────────────────────────────────────────────────────────────────────────────
if not os.getenv("ANTHROPIC_API_KEY"):
    st.error(
        "**ANTHROPIC_API_KEY is not configured.** "
        "Add it to your `.env` file and restart the app."
    )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
if "justification" not in st.session_state:
    st.session_state.justification: dict | None = None
    st.session_state.last_input: str = ""
    st.session_state.form_reset: int = 0

# ─────────────────────────────────────────────────────────────────────────────
# Single input + output layout
# ─────────────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([2, 3], gap="large")

with left_col:
    st.subheader("Describe Your Purchase")
    st.caption(
        "Include as much detail as you have — project number, part, cost, vendor, and why you need it."
    )

    with st.form(f"po_form_{st.session_state.form_reset}", border=False):
        user_input = st.text_area(
            label="Purchase details",
            label_visibility="collapsed",
            placeholder=(
                "e.g. Project 2419 — need to order a servo motor (part 4930-001-A) "
                "from Acme Corp for $4,250. It's for assembly line axis 3 which is down. "
                "We need it by end of week to hit the production milestone."
            ),
            height=220,
        )

        st.markdown("---")

        btn_col, clear_col = st.columns([3, 1])

        with btn_col:
            generate_btn = st.form_submit_button(
                "Generate Justification",
                type="primary",
                use_container_width=True,
            )

        with clear_col:
            clear_btn = st.form_submit_button("New PO", use_container_width=True)

    if clear_btn:
        st.session_state.justification = None
        st.session_state.last_input = ""
        st.session_state.form_reset += 1
        st.rerun()

with right_col:

    if generate_btn and user_input.strip():
        with st.spinner("Generating justification — this may take 10–20 seconds…"):
            try:
                result = generate_po_justification(user_input.strip())
                st.session_state.justification = result
                st.session_state.last_input = user_input.strip()
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
                st.stop()

    if st.session_state.justification:
        j = st.session_state.justification

        _section_card("What", j["what"])
        _section_card("Why", j["why"])
        _section_card("Why Now", j["why_now"])
        _section_card("Why Good Value", j["why_good_value"])

        full_text = _build_export_text(j, st.session_state.last_input)
        teams_ready = bool(os.getenv("TEAMS_WEBHOOK_URL"))

        a1, a2, a3 = st.columns(3)

        with a1:
            st.download_button(
                "⬇ Export as Text",
                data=full_text,
                file_name=f"PO_Justification_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with a2:
            _clipboard_button(full_text)

        with a3:
            teams_btn = st.button(
                "📤 Post to Teams",
                use_container_width=True,
                disabled=not teams_ready,
                help=(
                    "Set TEAMS_WEBHOOK_URL in .env to enable"
                    if not teams_ready
                    else "Post this justification to your Teams channel"
                ),
            )
            if teams_btn:
                with st.spinner("Posting to Teams…"):
                    try:
                        send_to_teams(
                            j,
                            user_input=st.session_state.last_input,
                        )
                        st.success("Posted to Teams successfully.")
                    except Exception as exc:
                        st.error(str(exc))

    else:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 20px;color:#888;">
                <div style="font-size:48px;margin-bottom:16px;">📋</div>
                <div style="font-size:16px;font-weight:600;margin-bottom:8px;">
                    Ready to generate
                </div>
                <div style="font-size:14px;">
                    Describe your purchase on the left and click
                    <strong>Generate Justification</strong>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
