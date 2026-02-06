from openai import OpenAI

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")


def detect_blog_category(title, content):
    text = f"{title}\n{content}"

    prompt = f"""
    Classify this blog into ONE category only:
    Technology, Education, Health, Travel, Business, Lifestyle, Sports, General.

    Blog:
    {text}

    Return only category name.
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output[0].content[0].text.strip()
