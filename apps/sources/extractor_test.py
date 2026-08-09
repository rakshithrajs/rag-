from extractors import extract_url


def main():
    url = "https://www.evidentlyai.com/llm-guide/rag-evaluation"
    extracted_text = extract_url(url)
    print("Extracted text from URL:")
    print(extracted_text[:500])


if __name__ == "__main__":
    main()
