import openai

def generate_embeddings(text):
    openai.api_key = 'your-openai-api-key'
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']
