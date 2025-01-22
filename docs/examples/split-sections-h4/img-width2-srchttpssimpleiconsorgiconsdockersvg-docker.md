#### <img width="2%" src="https://simpleicons.org/icons/docker.svg">&emsp13;Docker

Run the `readmeai` CLI in a Docker container:

```sh
❯ docker run -it --rm \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -v "$(pwd)":/app zeroxeli/readme-ai:latest \
    --repository https://github.com/eli64s/readme-ai \
    --api openai
```

<!-- #### ![streamlit][streamlit-svg]{ width="2%" }&emsp13;Streamlit -->

---

<!-- REFERENCE LINKS -->
[streamlit-svg]: https://simpleicons.org/icons/streamlit.svg
