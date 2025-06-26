import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

# Emoji-safe font
mpl.rcParams['font.family'] = 'DejaVu Sans'
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📊 WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("📁 Upload Chat File (.txt)", type=['txt'])

# -----------------------------
# Main logic
# -----------------------------
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8", errors="ignore")
    df = preprocessor.preprocess(data)
    
    st.markdown("### 🧾 Raw Chat Data")
    st.dataframe(df)

    # User selection
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Analyze chat for:", user_list)

    if st.sidebar.button("📊 Show Analysis"):
        
        # -----------------------------
        # 1. Top Stats
        # -----------------------------
        st.markdown("## 📈 Top Chat Statistics")
        num_messages, words, num_media_messages, num_links, emoji_count, chat_days = helper.fetch_stats(selected_user, df)

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)
        col1.metric("💬 Total Messages", num_messages)
        col2.metric("📝 Total Words", words)
        col3.metric("📎 Media Shared", num_media_messages)
        col4.metric("🔗 Links Shared", num_links)
        col5.metric("😀 Emojis Used", emoji_count)
        col6.metric("📆 Days Since Talking", chat_days)

        st.markdown("---")

        # 2. Wordcloud
        st.markdown("## \u2601\ufe0f Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)


        # 3. Most Common Words
        most_common_df = helper.most_common_words(selected_user, df)
        if not most_common_df.empty:
            st.markdown("## \U0001F5E3\ufe0f Most Common Words")
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(y=most_common_df[0], x=most_common_df[1], palette="magma", ax=ax)
            ax.bar_label(ax.containers[0], fmt='%d', fontsize=10)
            ax.set_xlabel("Frequency")
            ax.set_ylabel("Words")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No common words found.")

        # -----------------------------
        # 4. Emoji Analysis
        # -----------------------------
        st.markdown("## 😀 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:
            emoji_df_cleaned = emoji_df.rename(columns={0: "Emoji", 1: "Count"}).reset_index(drop=True)
            st.table(emoji_df_cleaned)  # Table with no index
        else:
            st.info("No emojis found.")

        st.markdown("---")

        # 5. Monthly Timeline
        st.markdown("## 📆 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=timeline, x='time', y='message', marker='o', color='green', ax=ax)
        ax.set_title("Messages per Month", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Message Count")
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # 6. Daily Timeline
        st.markdown("## 📅 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=daily_timeline, x='only_date', y='message', marker='o', color='black', ax=ax)
        ax.set_title("Messages per Day", fontsize=14)
        ax.set_xlabel("Date")
        ax.set_ylabel("Message Count")
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # 7. Activity Map (Weekday and Month)
        st.markdown("## 📊 Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🗓️ Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_day.index, y=busy_day.values, palette='Purples', ax=ax)
            ax.set_ylabel("Message Count")
            ax.set_title("Messages by Day of Week")
            ax.bar_label(ax.containers[0], fmt='%d')
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

        with col2:
            st.markdown("### 📅 Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_month.index, y=busy_month.values, palette='Oranges', ax=ax)
            ax.set_ylabel("Message Count")
            ax.set_title("Messages by Month")
            ax.bar_label(ax.containers[0], fmt='%d')
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

        # 8. Weekly Activity Heatmap
        st.markdown("## 🔥 Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.heatmap(user_heatmap, cmap="YlGnBu", linewidths=0.3, linecolor='gray', annot=True, fmt='.0f')
        ax.set_title("Activity Heatmap (Day vs Hour)", fontsize=14)
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Day of Week")
        st.pyplot(fig)

        # 9. Most active time period
        st.markdown("## ⏰ Most Active Time Period")
        active_period = df['period'].value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=active_period.index, y=active_period.values, palette='coolwarm', ax=ax)
        ax.set_title("Top Active Hourly Periods")
        ax.set_ylabel("Message Count")
        ax.set_xlabel("Time Interval")
        plt.xticks(rotation=45)
        st.pyplot(fig)

