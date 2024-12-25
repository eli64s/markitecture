#### ![docker][docker-svg]{ width="2%" }&emsp13;Docker

Run the `readmeai` CLI in a Docker container:

```sh
❯ docker run -it --rm \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -v "$(pwd)":/app zeroxeli/readme-ai:latest \
    --repository https://github.com/eli64s/readme-ai \
    --api openai
```

---

<!-- REFERENCE LINKS -->
[docker-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/3052baaca03db99d00808acfec43a44e81ecbf7f/docs/docs/assets/svg/docker.svg
