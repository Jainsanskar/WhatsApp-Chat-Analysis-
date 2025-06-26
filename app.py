import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=['txt'])
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8", errors="ignore")
    df = preprocessor.preprocess(data)
    st.dataframe(df)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        # Stats Area
        num_messages, words, num_media_messages, num_links, emoji_count, chat_days = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)

        with col4:
            st.header("Links Shared")
            st.title(num_links)

        with col5:
            st.header("Total Emojis")
            st.title(emoji_count)

        with col6:
            st.header("Days Since Talking")
            st.title(chat_days)

         # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')

            x, new_df = helper.most_busy_users(df)

            # Use seaborn styling
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.set_style("whitegrid")

            col1, col2 = st.columns(2)

            with col1:
                sns.barplot(x=x.index, y=x.values, palette='Reds_r', ax=ax)

                # Display count labels on top of bars
                for i, v in enumerate(x.values):
                    ax.text(i, v + 1, str(v), ha='center', fontweight='bold', fontsize=9)

                ax.set_title("Top Active Users", fontsize=14)
                ax.set_xlabel("User", fontsize=12)
                ax.set_ylabel("Message Count", fontsize=12)
                plt.xticks(rotation=45)
                st.pyplot(fig)

            with col2:
                st.subheader("Message % Breakdown")
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most common words
        most_common_df = helper.most_common_words(selected_user, df)

        if not most_common_df.empty:
            st.title('Most Common Words')

            fig, ax = plt.subplots(figsize=(8, 5))
            sns.set_style("whitegrid")

            # Plot horizontal bar chart
            sns.barplot(
                y=most_common_df[0],
                x=most_common_df[1],
                palette="magma",
                ax=ax
            )

            ax.set_xlabel("Frequency", fontsize=12)
            ax.set_ylabel("Words", fontsize=12)
            ax.set_title("Top 20 Most Common Words", fontsize=14)
            ax.bar_label(ax.containers[0], fmt='%d', label_type='edge', fontsize=10)
            plt.tight_layout()

            st.pyplot(fig)
        else:
            st.write("No words to display.")
