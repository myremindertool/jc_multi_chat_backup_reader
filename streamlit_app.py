import streamlit as st
import os
import re
from datetime import datetime
import hashlib

# ----------- Message Parser -----------
def parse_chat(content):
    android_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}) - (.*?): (.*)")
    iphone_pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} [APMapm]{2})\] (.*?): (.*)")
    messages = []
    for match in android_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %H:%M")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except:
            continue
    for match in iphone_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %I:%M:%S %p")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except:
            continue
    return sorted(messages, key=lambda x: x["datetime"], reverse=True)

def sender_color(sender):
    clean_sender = sender.strip().lower()
    if "reshmi" in clean_sender:
        return "#ffffcc"
    colors = ["#f0f8ff", "#e6ffe6", "#fff0f5", "#fffdd0", "#e0ffff", "#f5f5dc"]
    idx = int(hashlib.sha256(sender.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]

def get_initials(name):
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][0].upper()

# ----------- Page Config -----------
st.set_page_config(page_title="JC WhatsApp Chat Viewer", layout="wide")

# ----------- Custom CSS -----------
st.markdown("""
<style>
.block-container { padding-top: 0.5rem !important; }
.fixed-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 1000;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #eee;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiselect"] label,
div[data-testid="stTextInput"] label {
    margin-bottom: 0.25rem;
    font-weight: 500;
}
.message-box {
    border-radius: 10px;
    padding: 0.75rem;
    margin: 0.4rem 0;
    display: flex;
    align-items: flex-start;
    font-size: 0.95rem;
    border-left: 5px solid #ccc;
    width: 100%;
    word-break: break-word;
}
.sender-header {
    font-weight: 600;
    color: #333;
    margin-bottom: 0.2rem;
}
.timestamp {
    font-size: 0.75rem;
    color: #888;
    margin-left: 0.5rem;
}
.avatar {
    min-width: 2.2rem;
    height: 2.2rem;
    border-radius: 50%;
    background: #ccc;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    flex-shrink: 0;
}
.message-text {
    word-break: break-word;
    white-space: pre-wrap;
    font-size: 0.9rem;
    margin-top: 0.25rem;
    color: #222;
}
.chat-scroll-wrapper {
    max-height: 65vh;
    overflow-y: auto;
    padding-right: 1rem;
    margin-top: 1rem;
    border-top: 1px solid #eee;
}
.footer {
    text-align: center;
    color: #888;
    font-size: 0.8rem;
    padding-top: 1rem;
}
@media (max-width: 768px) {
    .message-box { flex-direction: column; padding: 0.6rem; }
    .avatar { width: 2rem; height: 2rem; font-size: 0.8rem; margin-bottom: 0.4rem; }
    .message-text { font-size: 0.85rem; margin-left: 0.2rem; }
}
</style>
""", unsafe_allow_html=True)

# ----------- Header & File Picker -----------
with st.container():
    st.markdown("<div class='fixed-header'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0.5rem;'>💬 JC WhatsApp Multi-Chat Viewer</h3>", unsafe_allow_html=True)

    chat_files = [f for f in os.listdir() if f.endswith(".txt") and f.lower() != "requirements.txt"]
    selected_file = st.selectbox("📂 **Choose chat file to view** _(select backup chat)_", chat_files)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Load Messages -----------
if selected_file:
    with open(selected_file, "r", encoding="utf-8") as f:
        content = f.read().replace('\u202f', ' ').replace('\u200e', '')
    messages = parse_chat(content)

    if not messages:
        st.warning("No valid messages found.")
    else:
        senders = sorted(set(m['sender'] for m in messages))
        selected_senders = st.multiselect("👤 **Filter senders**", senders, default=senders)
        search_term = st.text_input("🔍 **Search messages** (type to filter)", "")
        limit = st.slider("🔢 **Max messages to display**", 100, 20000, 1000, step=100)

        filtered_messages = [
            m for m in messages
            if m['sender'] in selected_senders and search_term.lower() in m['message'].lower()
        ][:limit]

        st.info(f"Parsed {len(messages)} messages. Showing {len(filtered_messages)} after filters.")
        st.markdown("<div class='chat-scroll-wrapper'>", unsafe_allow_html=True)

        if not filtered_messages:
            st.markdown("<p style='color:gray'>No messages match filters or search.</p>", unsafe_allow_html=True)
        else:
            last_date = ""
            for m in filtered_messages:
                date_str = m['datetime'].strftime('%d %b %Y')
                if date_str != last_date:
                    st.markdown(f"### 📅 {date_str}")
                    last_date = date_str

                initials = get_initials(m['sender'])
                avatar = f"<div class='avatar'>{initials}</div>"
                color = sender_color(m['sender'])
                sender_line = f"<span class='sender-header'>{m['sender']}<span class='timestamp'> &nbsp;&nbsp;{m['datetime'].strftime('%I:%M %p')}</span></span>"
                
                st.markdown(f"""
                    <div class='message-box' style='background-color: {color};'>
                        {avatar}
                        <div style='flex:1; min-width: 0;'>
                            {sender_line}
                            <div class='message-text'>{m['message']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='color: gray; font-size: 0.8rem;'>-- End of Chat --</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # Close scroll wrapper
        st.markdown("<div class='footer'>✅ Developed by <strong>JC</strong></div>", unsafe_allow_html=True)
