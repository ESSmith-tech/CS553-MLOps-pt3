    def respond(self, 
                message: str, 
                history: List[Dict[str, str]], 
                gallery: Any,
                max_tokens: int, 
                temperature: float, 
                top_p: float, 
                use_local_model: bool,
                hf_token: Optional[gr.OAuthToken]) -> str:
        """Generate response to user message, using prompt from prompt_config based on gallery selection

        NOTE: This implementation consumes the model generator and returns a final string
        because Gradio expects a message (or list/dict), not a raw generator object.
        """

        # Determine selected philosopher from gallery input
        prompts = self.prompts

        selected_philosopher = None
        if gallery:
            # Gradio Gallery returns the selected image path as a string
            if isinstance(gallery, str):
                # Extract filename without extension
                selected_philosopher = os.path.splitext(os.path.basename(gallery))[0]
                
            elif isinstance(gallery, list) and len(gallery) > 0:
                # Sometimes Gallery returns a list of selected items
                item = gallery[0]
                if isinstance(item, str):
                    selected_philosopher = os.path.splitext(os.path.basename(item))[0]
                elif isinstance(item, (list, tuple)) and len(item) > 0:
                    selected_philosopher = os.path.splitext(os.path.basename(item[0]))[0]

        # Fallback: use first key in prompt_config if nothing selected
        if not selected_philosopher and prompts:
            selected_philosopher = next(iter(prompts.keys()))

        # Get introduction/system prompt
        system_prompt = ""
        if selected_philosopher and prompts and selected_philosopher in prompts:
            system_prompt = prompts[selected_philosopher].get("introduction", "")
        messages = self.build_messages(message, history, system_prompt)

        # Start metrics for this request
        REQUEST_COUNTER.inc()
        if selected_philosopher:
            try:
                PHILOSOPHER_COUNTER.labels(philosopher=selected_philosopher).inc()
            except Exception:
                # Labels may fail if invalid; ignore metric failure
                pass

        # Increment local/api specific counters and get generator
        if use_local_model:
            LOCAL_MODEL_REQUESTS.inc()
            gen = self._handle_local_model(messages, max_tokens, temperature, top_p)
        else:
            API_MODEL_REQUESTS.inc()
            gen = self._handle_api_model(messages, max_tokens, temperature, top_p, hf_token)

        # Consume generator and return final string so Gradio gets a proper message object
        chunks = []
        with REQUEST_DURATION.time():
            try:
                for chunk in gen:
                    # model yields text chunks; collect them
                    chunks.append(chunk)
                SUCCESSFUL_REQUESTS.inc()
            except Exception:
                FAILED_REQUESTS.inc()
                # propagate error so Gradio can display error
                raise

        final_text = "".join(chunks)
        return final_text
