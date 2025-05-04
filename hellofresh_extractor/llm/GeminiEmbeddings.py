from google import genai
from google.genai import types


class GeminiEmbeddings:
    MAX_TOKENS = 7500

    def __init__(self, api_key, model, task_type="SEMANTIC_SIMILARITY"):
        self.api_key = api_key
        self.model_name = model
        self.task_type = task_type
        self.client = genai.Client(api_key=api_key)

    def _count_tokens(self, texts):
        # Count tokens for the batch of texts
        return self.client.models.count_tokens(
            model="gemini-2.5-flash-preview-04-17", contents=texts
        )

    def embed_list(self, text_to_embed):
        result = []
        # Simple batching: split into chunks if needed
        batch = []
        tokens_in_batch = 0

        for text in text_to_embed:
            tokens = self._count_tokens([text])
            if tokens_in_batch + tokens.total_tokens > self.MAX_TOKENS and batch:
                # Embed current batch
                embeddings = self.client.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                    config=types.EmbedContentConfig(task_type=self.task_type),
                )
                result.extend([x.values for x in embeddings.embeddings])
                batch = []
                tokens_in_batch = 0
            batch.append(text)
            tokens_in_batch += tokens.total_tokens

        # Embed any remaining texts
        if batch:
            embeddings = self.client.models.embed_content(
                model=self.model_name,
                contents=batch,
                config=types.EmbedContentConfig(task_type=self.task_type),
            )
            result.extend([x.values for x in embeddings.embeddings])

        return result
