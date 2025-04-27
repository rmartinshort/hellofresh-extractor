class MultiModalModel:
    def __init__(self, model_pipe):
        self.multimodal_pipe = model_pipe

    def invoke(self, system_message, user_messages, max_tokens=1000, temperature=0.1):
        input_messages = [
            {"role": "system", "content": [{"type": "text", "text": system_message}]},
            {"role": "user", "content": user_messages},
        ]

        output = self.multimodal_pipe(
            text=input_messages,
            max_new_tokens=max_tokens,
            generate_kwargs={
                "temperature": temperature,
                "do_sample": True,
            },
            return_full_text=False,
        )
        return output
