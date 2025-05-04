import outlines


class StructuredOutputModel:
    def __init__(self, model, outputmodel, structure_mode="json"):
        self.model = model
        self.structure_generator = self.set_up_structured_caller(
            mode=structure_mode, outputmodel=outputmodel
        )
        self.structure_mode = structure_mode
        self.output_model = outputmodel

    def create_prompt_template(self, user_message: str, system_message: str):
        return self.model.tokenizer.tokenizer.apply_chat_template(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            tokenize=False,
            add_bos=True,
            add_generation_prompt=True,
        )

    def set_up_structured_caller(
        self,
        outputmodel,
        mode="json",
        sampler=outlines.samplers.multinomial(temperature=0.5),
    ):
        if mode == "json":
            structure_generator = outlines.generate.json(
                self.model, outputmodel, sampler=sampler
            )
        else:
            raise NotImplementedError("Only supports mode='json' but could be extended")

        return structure_generator

    def invoke(self, system_message, user_query, text_to_extract):
        extraction_user_message = f"""

        You have been asked to perform the following task:

        {user_query}

        The text you must parse to perform this task is here:

        {text_to_extract}
        """

        assembled_prompt = self.create_prompt_template(
            user_message=extraction_user_message, system_message=system_message
        )

        structured_result = self.structure_generator(assembled_prompt)
        return structured_result
