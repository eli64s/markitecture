#### Set your API key

When running `readmeai` with a third-party service, you must provide a valid API key. For example, the `OpenAI` client is set as follows:

```sh
❯ export OPENAI_API_KEY=<your_api_key>

# For Windows users:
❯ set OPENAI_API_KEY=<your_api_key>
```

<details closed><summary>Click to view environment variables for - <code>Ollama</code>, <code>Anthropic</code>, <code>Google Gemini</code></summary>
<br>
<details closed><summary>Ollama</summary>
<br>

Refer to the [Ollama documentation][ollama] for more information on setting up the Ollama server.

To start, follow these steps:

1. Pull your model of choice from the Ollama repository:

	```sh
	❯ ollama pull llama3.2:latest
	```

2. Start the Ollama server and set the `OLLAMA_HOST` environment variable:

	```sh
	❯ export OLLAMA_HOST=127.0.0.1 && ollama serve
	```

</details>
<details closed><summary>Anthropic</summary>

1. Export your Anthropic API key:

	```sh
	❯ export ANTHROPIC_API_KEY=<your_api_key>
	```

</details>
<details closed><summary>Google Gemini</summary>

1. Export your Google Gemini API key:

	```sh
	❯ export GOOGLE_API_KEY=<your_api_key
	```

</details>
</details>

---

<!-- REFERENCE LINKS -->
[ollama]: https://github.com/ollama/ollama
