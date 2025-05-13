import streamlit as st
import os
import re
from datetime import datetime
import hashlib

def parse_chat(content):
    android_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}) - (.*?): (.*)")
    iphone_pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} [APMapm]{2})\] (.*?): (.*)")
    messages = []
    for match in android_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %H:%M")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except: continue
    for match in iphone_pattern.findall(content):
        try:
            dt = datetime.strptime(f"{match[0]} {match[1]}", "%d/%m/%Y %I:%M:%S %p")
            messages.append({"datetime": dt, "sender": match[2], "message": match[3]})
        except: continue
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

st.set_page_config(page_title="JC WhatsApp Chat Viewer", layout="wide")
st.markdown("""
<style>
    .fixed-header {
        position: sticky;
        top: 0;
        background: white;
        z-index: 1000;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #eee;
    }
    .message-box {
        border-radius: 10px;
        padding: 0.75rem;
        margin: 0.25rem 0;
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
        margin-bottom: 0.25rem;
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
    .chat-scroll-wrapper {
        max-height: 65vh;
        overflow-y: auto;
        padding-right: 1rem;
        margin-top: 1rem;
        border-top: 1px solid #eee;
        scrollbar-gutter: stable;
    }
    @media (max-width: 768px) {
        .chat-scroll-wrapper {
            max-height: 50vh;
            padding-right: 0.5rem;
        }
        .message-box {
            font-size: 0.88rem;
            padding: 0.6rem;
        }
        .avatar {
            width: 1.8rem;
            height: 1.8rem;
            font-size: 0.8rem;
        }
    }
    .chat-scroll-wrapper::-webkit-scrollbar {
        width: 12px;
    }
    .chat-scroll-wrapper::-webkit-scrollbar-track {
        background: #f0f0f0;
    }
    .chat-scroll-wrapper::-webkit-scrollbar-thumb {
        background-color: red;
        border-radius: 6px;
        border: 3px solid #f0f0f0;
    }
    section.main > div { padding-top: 0rem !important; }
    .block-container { padding-top: 0rem !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
  const chatArea = document.querySelector('.chat-scroll-wrapper');
  if (chatArea) {
    chatArea.addEventListener('wheel', function(e) {
      const canScroll = this.scrollHeight > this.clientHeight;
      if (canScroll) {
        e.stopPropagation();
      }
    }, { passive: true });
  }
});
</script>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='fixed-header'>", unsafe_allow_html=True)
    st.title("💬 JC WhatsApp Multi-Chat Viewer")
    chat_files = [f for f in os.listdir() if f.endswith(".txt") and f.lower() != "requirements.txt"]
    selected_file = st.selectbox("📂 Choose chat file to view:", chat_files)
    st.markdown("</div>", unsafe_allow_html=True)

if selected_file:
    with open(selected_file, "r", encoding="utf-8") as f:
        content = f.read().replace('\u202f', ' ').replace('\u200e', '')
    messages = parse_chat(content)
    if not messages:
        st.warning("No valid messages found.")
    else:
        senders = sorted(set(m['sender'] for m in messages))
        selected_senders = st.multiselect("👤 Filter senders:", senders, default=senders)
        search_term = st.text_input("🔍 Search messages:")

        filtered_messages = [
            m for m in messages
            if m['sender'] in selected_senders and search_term.lower() in m['message'].lower()
        ]

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
                        <div>
                            {sender_line}
                            <div>{m['message']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("<div style='color: gray; font-size: 0.8rem;'>-- End of Chat --</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
