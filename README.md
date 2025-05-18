# hellofresh-extractor
Codes to accompany article about using outlines and gemma3 for extraction of ingredients from images of recipe cards.

## Notebooks 

See the following notebooks examples of how to run this code

- notebooks/load_from_gsuite  
Shows how to download images that have been uploaded to google drive. In this project, we take photos of hellofresh recipe cards on a mobile device, upload them to google drive and then use this tool to fetch them for local analysis
- notebooks/run_gemini_on_files  
Shows how to run a cloud based LLM in structured output mode (Gemini) to extract recipes from the cards
- notebooks/run_local_pipe_on_files   
Shows how to run the local pipeline (Gemma3 + small text based LLM with conditional decoding with outlines) to do the same extraction locally
- notebooks/LLM_judge  
Shows how to run a comparative evaluation to see which approach generates the best result 

## Other points

Also see GeminiEmbeddings class, which can be used to generate embeddings of any text. 