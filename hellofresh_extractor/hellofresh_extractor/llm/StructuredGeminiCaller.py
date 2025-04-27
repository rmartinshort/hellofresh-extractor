import json
from google import genai
from typing import Dict, Any, Union, List, Type
from pydantic import BaseModel
from PIL import Image
import base64
from io import BytesIO


class StructuredGeminiCaller:
    def __init__(self, api_key: str, model: str):
        """
        Initializes the GeminiCaller with an API key and model name.

        Example usage:
        gemini_caller = GeminiCaller(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model="gemini-2.5-flash-preview-04-17"
        )

        example_image = Image.open(images[0]).convert("RGB")
        user_input = [example_image, user_query]

        # Call the model with image input and structured output
        result = gemini_caller.invoke(
            system_message=system_prompt,
            input_content=user_input,
            output_schema=ExtractedMeal
        )

        Args:
            api_key (str): The API key for accessing the Gemini LLM.
            model (str): The name of the Gemini model to use.
        """
        self.api_key = api_key
        self.model_name = model
        self.client = genai.Client(api_key=api_key)

    def invoke(
        self,
        system_message: str,
        input_content: Union[str, List[Union[str, Image.Image, dict]]],
        output_schema: Type[BaseModel] = None,
        temperature: float = 0.0,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Invokes the language model to generate content based on the provided input and system template.

        Args:
            system_template (dataclass): The template containing system instructions for the model.
            input_content (Union[str, List[Union[str, Image.Image, dict]]]): The input content to be processed.
                Can be a string, an image, or a list containing strings and images.
            output_schema (Type[BaseModel], optional): Pydantic model for structured output. Defaults to None.
            temperature (float, optional): The sampling temperature for controlling randomness. Defaults to 0.0.
            max_tokens (int, optional): The maximum number of tokens to generate. Defaults to 1000.

        Returns:
            Dict[str, Any]: The response from the model. If an error occurs, an empty dictionary is returned.
        """
        try:
            # Process input content
            contents = self._prepare_contents(input_content)

            # Configure generation parameters
            config = genai.types.GenerateContentConfig(
                system_instruction=system_message,
                max_output_tokens=max_tokens,
                temperature=temperature,
                thinking_config=genai.types.ThinkingConfig(thinking_budget=0),
            )

            # Add structured output schema if provided
            if output_schema:
                config.response_mime_type = "application/json"
                config.response_schema = output_schema

            # Generate content
            res = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            # Parse the response
            res = json.loads(res.model_dump_json())

            # If using structured output, parse the response text as the Pydantic model
            if output_schema and "candidates" in res and res["candidates"]:
                if (
                    "content" in res["candidates"][0]
                    and "parts" in res["candidates"][0]["content"]
                ):
                    for part in res["candidates"][0]["content"]["parts"]:
                        if "text" in part:
                            try:
                                # Parse the JSON response into the Pydantic model
                                structured_data = output_schema.model_validate_json(
                                    part["text"]
                                )
                                # Add the structured data to the response
                                res["structured_data"] = structured_data.model_dump()
                            except Exception as e:
                                print(f"Error parsing structured output: {e}")

        except Exception as e:
            print(f"Error calling {self.model_name}: {e}")
            res = {}

        return res

    def _prepare_contents(self, input_content):
        """
        Prepares the input content for the model.

        Args:
            input_content: The input content, which can be a string, image, or list of mixed content.

        Returns:
            List: A list of content items ready for the model.
        """
        if isinstance(input_content, str):
            return [input_content]

        if isinstance(input_content, Image.Image):
            return [self._process_image(input_content)]

        if isinstance(input_content, list):
            processed_contents = []
            for item in input_content:
                if isinstance(item, str):
                    processed_contents.append(item)
                elif isinstance(item, Image.Image):
                    processed_contents.append(self._process_image(item))
                elif (
                    isinstance(item, dict)
                    and "type" in item
                    and item["type"] == "image"
                ):
                    # Handle pre-formatted image dictionaries
                    processed_contents.append(item)
                else:
                    # Try to process as regular content
                    processed_contents.append(item)
            return processed_contents

        # Default case
        return [input_content]

    def _process_image(self, image: Image.Image):
        """
        Processes an image for the model.

        Args:
            image (Image.Image): The PIL Image to process.

        Returns:
            dict: A dictionary containing the processed image data.
        """
        # For files larger than 20MB, use the File API
        if self._estimate_image_size(image) > 20 * 1024 * 1024:
            # Convert image to bytes
            buffer = BytesIO()
            image.save(buffer, format=image.format or "JPEG")
            buffer.seek(0)

            # Upload the file
            file = self.client.files.upload(
                file=buffer.read(),
                mime_type=f"image/{image.format.lower() if image.format else 'jpeg'}",
            )

            # Return the file reference
            return file

        # For smaller images, use inline data
        buffer = BytesIO()
        image.save(buffer, format=image.format or "JPEG")
        buffer.seek(0)
        image_bytes = buffer.read()

        # Return inline image data
        return {
            "inlineData": {
                "mimeType": f"image/{image.format.lower() if image.format else 'jpeg'}",
                "data": base64.b64encode(image_bytes).decode("utf-8"),
            }
        }

    def _estimate_image_size(self, image: Image.Image) -> int:
        """
        Estimates the size of an image in bytes.

        Args:
            image (Image.Image): The PIL Image to estimate.

        Returns:
            int: Estimated size in bytes.
        """
        buffer = BytesIO()
        image.save(buffer, format=image.format or "JPEG")
        return buffer.tell()

    @staticmethod
    def token_counter(model_output: Any) -> Dict[str, int]:
        """
        Counts the number of input and output tokens used by the Gemini LLM.

        Args:
            model_output (Dict[str, Any]): The output from the Gemini LLM.

        Returns:
            Dict[str, int]: A dictionary containing the number of input and output tokens.
        """
        usage_stats = model_output["usage_metadata"]
        input_tokens = usage_stats["prompt_token_count"]
        output_tokens = usage_stats["candidates_token_count"]
        return {"input_tokens": input_tokens, "output_tokens": output_tokens}
