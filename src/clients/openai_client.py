import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OpenAIClient:
    """
    A client for interacting with the OpenAI API to generate responses using a specified model.
    """

    def __init__(self, model, temperature, max_completion_tokens):
        """
        Initialize the OpenAIClient with API key, model, temperature, and max tokens.

        Args:
            api_key (str): The OpenAI API key.
            model (str): The OpenAI model to use.
            temperature (float): The sampling temperature.
            max_completion_tokens (int): The maximum number of tokens to generate.
        """
        try:
            self.client = OpenAI()
            self.model = model
            self.temperature = temperature
            self.max_completion_tokens = max_completion_tokens
            logging.info(
                "OpenAI client initialized successfully, "
                "Model: %s, temperature: %s, max tokens: %s",
                self.model,
                self.temperature,
                self.max_completion_tokens
            )
        except Exception as e:
            logging.error("Error initializing OpenAI client: %s", e)
            raise

    def generate_response(self, prompt, stream=False):
        """
        Generate a response from the OpenAI model based on the given prompt.

        Args:
            prompt (str): The prompt to send to the OpenAI API.
            stream (bool): If True, streams the tokens as they are generated.

        Returns:
            str or generator: If `stream` is False, returns the generated response as a string.
                              If `stream` is True, yields tokens as they are generated.

        Raises:
            Exception: If there is an error generating the response.
        """
        try:
            logging.info("Generating response from OpenAI model with streaming=%s.", stream)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "You are an expert Developer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_completion_tokens=self.max_completion_tokens,
                stream=stream
            )

            if stream:
                # Stream tokens as they are generated
                for chunk in response:
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        yield chunk["choices"][0]["delta"].get("content", "")
            else:
                # Return the complete response as a single string
                logging.info("Response generated successfully.")
                return response.choices[0].message.content
        except Exception as e:
            logging.error("Error generating response from OpenAI model: %s", e)
            raise
