# Reference-style links

Reference-style links are a way to keep the text of your Markdown file clean and readable. They are especially useful for long URLs or when you want to reuse the same link in multiple places.


The converter will:
1. Find all markdown links in the file
2. Convert them to reference-style links
3. Add a reference section at the bottom of the file
4. Handle both regular links and image links
5. Generate unique reference IDs
6. Preserve the original content structure

## Example

1. Convert links in a file (modifies in place)

    ```sh
    splitme-ai --reflinks.input README.md
    ```
2. Convert links and save to a new file

    ```sh
    splitme-ai --reflinks.input README.md --reflinks.output README-with-refs.md
    ```

---
