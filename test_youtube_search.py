# test_youtube_search.py
from sources.video_transcript import YouTubeTranscriptManager, YouTubeSearch, YouTubeTranscriptFetcher

def test_youtube_search(search_query: str, max_results: int = 5):
    print(f"\n🔍 Searching YouTube for: '{search_query}'")

    try:
        # 1. Test YouTubeSearch directly
        searcher = YouTubeSearch(max_results=max_results)
        results = searcher.search(search_query)

        if not results:
            print("❌ No search results found.")
            return

        print(f"\n✅ Found {len(results)} search results:")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']} - {r['href']}")

        # 2. Test video ID extraction + transcript fetching
        fetcher = YouTubeTranscriptFetcher()
        transcripts = []

        for r in results:
            video_id = fetcher.extract_video_id(r["href"])
            print(f"\n🎥 Video: {r['title']}")
            print(f"   URL: {r['href']}")
            print(f"   Extracted ID: {video_id}")

            transcript_text = fetcher.fetch_transcript(r["href"])
            lang_used = getattr(fetcher, "last_lang_used", "unknown")  # get the language used
            if transcript_text:
                print(f"   ✅ Transcript fetched ({len(transcript_text)} characters) - Language: {lang_used}")
                transcripts.append(transcript_text[:200] + "...")
            else:
                print(f"   ⚠️ Transcript not available - Language tried: {lang_used}")

        # 3. Test YouTubeTranscriptManager (end-to-end)
        manager = YouTubeTranscriptManager(max_results=max_results)
        combined_transcripts = manager.get_transcripts_from_search(search_query)

        print(f"\n📜 Combined transcripts length: {len(combined_transcripts)} characters")
        preview = combined_transcripts[:500] + "..." if combined_transcripts else "No transcripts combined"
        print(f"Preview of combined transcripts:\n{preview}")

        return combined_transcripts

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    search_query = input("Enter your YouTube search query: ")
    test_youtube_search(search_query)
