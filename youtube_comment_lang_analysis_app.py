
import streamlit as st
from langdetect import detect, LangDetectException
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from youtube_comment_downloader import YoutubeCommentDownloader

st.set_page_config(page_title="YouTube 댓글 언어 분석기", layout="centered")

st.title("🧠 YouTube 댓글 언어 분석기")
st.write("유튜브 영상의 URL을 입력하면 댓글을 자동 수집하고 언어별 비율을 분석합니다.")

# 사용자로부터 URL 입력 받기
st.subheader("🔗 분석할 YouTube 영상 URL 입력")
video_url = st.text_input("예: https://www.youtube.com/watch?v=abcd1234")

if st.button("🔍 댓글 자동 수집 및 언어 분석"):
    if not video_url:
        st.warning("URL을 입력해주세요.")
    else:
        downloader = YoutubeCommentDownloader()
        comments = []

        with st.spinner("댓글 수집 중..."):
            try:
                for comment in downloader.get_comments_from_url(video_url, sort_by=0):  # 인기순
                    text = comment["text"].strip()
                    if text:
                        comments.append(text)
                    if len(comments) >= 300:
                        break
            except Exception as e:
                st.error(f"댓글 수집 중 오류 발생: {e}")
                comments = []

        if not comments:
            st.error("댓글 수집에 실패했거나 댓글이 없습니다.")
        else:
            languages = []
            for c in comments:
                try:
                    lang = detect(c)
                    languages.append(lang)
                except LangDetectException:
                    continue

            if not languages:
                st.error("언어를 감지할 수 있는 댓글이 없습니다.")
            else:
                lang_counts = Counter(languages)
                df = pd.DataFrame(lang_counts.items(), columns=["Language", "Count"])
                df["Percentage"] = (df["Count"] / df["Count"].sum() * 100).round(1)

                st.success("✅ 분석 완료!")
                st.dataframe(df.sort_values(by="Count", ascending=False), use_container_width=True)

                # 파이 차트
                fig, ax = plt.subplots()
                ax.pie(df["Count"], labels=df["Language"], autopct="%1.1f%%", startangle=140)
                ax.axis("equal")
                plt.title("Comment Language Distribution")
                st.pyplot(fig)

                # 다운로드 옵션
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📄 분석 결과 CSV 다운로드", csv, "comment_language_result.csv", "text/csv")
