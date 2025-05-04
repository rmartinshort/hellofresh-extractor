import base64
from io import BytesIO
from typing import Any, Dict, List, Type, Union
from pydantic import BaseModel
from PIL import Image
import anthropic


class StructuredClaudeCaller:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model_name = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def invoke(
        self,
        system_message: str,
        input_content: Union[str, List[Union[str, Image.Image, dict]]],
        output_schema: Type[BaseModel] = None,
        temperature: float = 0.0,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Calls Claude with structured output and multimodal support.
        """
        try:
            messages = self._prepare_messages(input_content, output_schema)
            response = self.client.messages.create(
                system=system_message,
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
            )
            # Claude returns response.content as a list of content blocks
            text_response = self._extract_text_response(response)
            result = {"raw_response": text_response}

            # Parse as structured output if schema is provided
            if output_schema:
                try:
                    structured_data = output_schema.model_validate_json(text_response)
                    result["structured_data"] = structured_data.model_dump()
                except Exception as e:
                    print(f"Error parsing structured output: {e}")
            return result
        except Exception as e:
            print(f"Error calling Claude: {e}")
            return {}

    def _prepare_messages(
        self,
        input_content: Union[str, List[Union[str, Image.Image, dict]]],
        output_schema: Type[BaseModel] = None,
    ) -> List[Dict[str, Any]]:
        """
        Prepares the message list for Claude's API.
        """
        user_content = self._prepare_content_blocks(input_content)
        prompt = []
        # Instruct Claude to return JSON if a schema is provided
        if output_schema:
            user_content.append(
                {
                    "type": "text",
                    "text": (
                        "Respond ONLY in JSON matching this schema:\n"
                        f"{output_schema.schema_json(indent=2)}"
                    ),
                }
            )
        prompt.append({"role": "user", "content": user_content})
        return prompt

    def _prepare_content_blocks(
        self, input_content: Union[str, List[Union[str, Image.Image, dict]]]
    ) -> List[Dict[str, Any]]:
        """
        Converts input content into Claude-compatible content blocks.
        """
        if isinstance(input_content, str):
            return [{"type": "text", "text": input_content}]
        if isinstance(input_content, Image.Image):
            return [self._image_block(input_content)]
        if isinstance(input_content, list):
            blocks = []
            for item in input_content:
                if isinstance(item, str):
                    blocks.append({"type": "text", "text": item})
                elif isinstance(item, Image.Image):
                    blocks.append(self._image_block(item))
                elif isinstance(item, dict) and item.get("type") == "image":
                    blocks.append(item)
                else:
                    blocks.append({"type": "text", "text": str(item)})
            return blocks
        return [{"type": "text", "text": str(input_content)}]

    def _image_block(self, image: Image.Image) -> Dict[str, Any]:
        """
        Encodes a PIL image for Claude's API.
        """
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64_data,
            },
        }

    def _extract_text_response(self, response: Any) -> str:
        """
        Extracts the text portion from Claude's response.
        """
        # Claude's response.content is a list of blocks (type: text/image)
        return "".join(
            block.text
            for block in getattr(response, "content", [])
            if block.type == "text"
        )
