import requests
from bs4 import BeautifulSoup
import os
import re

# Headers to mimic a browser visit
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}


def ensure_trailing_slash(url):
    if not url.endswith("/"):
        return url + "/"
    return url


def extract_blog_text_and_title(session, url):
    print(f"  Attempting to fetch: {url}")
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"  HTTP Error for {url}: {e.response.status_code} - {e.response.reason}")
        # For debugging, you might want to see what the server returned for errors like 403 (Forbidden)
        # if e.response.status_code == 403:
        #     print(f"  Response text snippet for 403: {response.text[:500]}")
        return (
            "Error - Page Not Found"
            if e.response.status_code == 404
            else "Error - HTTP Request Failed"
        ), ""
    except requests.exceptions.RequestException as e:
        print(f"  Request Exception for {url}: {e}")
        return "Error - Request Failed", ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title = "Untitled Article"
    # Try more specific H1 first
    h1_title_element = soup.find("h1", class_=["display-3", "entry-title"])
    if h1_title_element:
        title = h1_title_element.get_text(strip=True)
    else:  # Fallback to HTML <title> tag
        title_tag_element = soup.find("title")
        if title_tag_element:
            title = title_tag_element.get_text(strip=True)
    print(f"    Extracted title: '{title}'")

    # Locate the main content area
    content_area = None
    selector_tried = ""

    # Primary selector for NVIDIA blogs
    primary_content_selector_tag = "div"
    primary_content_selector_class = "entry-content"
    content_area = soup.find(
        primary_content_selector_tag, class_=primary_content_selector_class
    )
    selector_tried = f"'{primary_content_selector_tag}' with class '{primary_content_selector_class}'"

    if content_area:
        print(f"    Found content area using primary selector: {selector_tried}")
    else:
        print(f"    Primary content selector {selector_tried} NOT found.")

    # Extract text from relevant tags within the content area
    text_parts = []
    content_tags_to_extract = [
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "pre",
        "code",
    ]

    elements_found_in_content_area = content_area.find_all(content_tags_to_extract)

    if not elements_found_in_content_area:
        print(
            f"    Content area found, BUT NO text elements (e.g., <p>, <h2>, <li>) found within it using tags: {content_tags_to_extract}."
        )
        # Uncomment to see the HTML of the 'content_area' if no inner text elements are found
        # print(f"    HTML of found 'content_area' (first 500 chars): {content_area.prettify()[:500]}")
    else:
        print(
            f"    Found {len(elements_found_in_content_area)} potential text elements within content area. Extracting text..."
        )
        for i, element in enumerate(elements_found_in_content_area):
            element_text = ""
            if element.name in ["pre", "code"]:  # Preserve whitespace for code blocks
                element_text = element.get_text(strip=False)
            else:  # For other text, strip extra whitespace and use space as separator
                element_text = element.get_text(separator=" ", strip=True)

            if element_text:  # Only add if there's actual text extracted
                text_parts.append(element_text)
            # else:
            #     print(f"      Element {i+1} ({element.name}) yielded no text.")

    final_body_text = "\n\n".join(text_parts)

    if not final_body_text.strip() and elements_found_in_content_area:
        print(
            f"    WARNING: Text elements were found in content area, but extracted body text is empty. This might indicate the elements found did not contain direct text or were filtered out."
        )
    elif not final_body_text.strip():
        print(f"    Extracted body text is empty.")
    else:
        print(
            f"    Successfully extracted body text (length: {len(final_body_text)} chars)."
        )

    return title, final_body_text


def sanitize_filename(name):
    if not name:
        return "untitled_article"
    name = str(name)
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[-\s]+", "-", name).strip("-_")
    return name[:100] if name else "untitled_article"


# --- Main script execution ---
if __name__ == "__main__":
    blog_post_urls_input = [
        "https://resources.nvidia.com/en-us-blackwell-architecture?ncid=pa-srch-goog-775790-GenAI-Brand-Broad"
        # "https://developer.nvidia.com/blog/nvidia-blackwell-delivers-massive-performance-leaps-in-mlperf-inference-v5-0/",
        # "https://developer.nvidia.com/blog/llm-performance-benchmarking-measuring-nvidia-nim-performance-with-genai-perf/",
        # "https://developer.nvidia.com/blog/optimizing-transformer-based-diffusion-models-for-video-generation-with-nvidia-tensorrt/",
        # "https://developer.nvidia.com/blog/llm-benchmarking-fundamental-concepts/",
        # "https://developer.nvidia.com/blog/boost-llama-model-performance-on-microsoft-azure-ai-foundry-with-nvidia-tensorrt-llm/",
        # "https://developer.nvidia.com/blog/introducing-nvidia-dynamo-a-low-latency-distributed-inference-framework-for-scaling-reasoning-ai-models/",
        # "https://developer.nvidia.com/blog/nvidia-blackwell-delivers-world-record-deepseek-r1-inference-performance/",
        # "https://developer.nvidia.com/blog/optimizing-qwen2-5-coder-throughput-with-nvidia-tensorrt-llm-lookahead-decoding/",
        # "https://developer.nvidia.com/blog/applying-specialized-llms-with-reasoning-capabilities-to-accelerate-battery-research/",
        # "https://developer.nvidia.com/blog/extending-the-nvidia-agent-intelligence-toolkit-to-support-new-agentic-frameworks/",
        # "https://developer.nvidia.com/blog/revolutionizing-neural-reconstruction-and-rendering-in-gsplat-with-3dgut/",
        # "https://developer.nvidia.com/blog/concept%e2%80%91driven-ai-teaching-assistant-guides-students-to-deeper-insights/",
        # "https://developer.nvidia.com/blog/building-nemotron-cc-a-high-quality-trillion-token-dataset-for-llm-pretraining-from-common-crawl-using-nvidia-nemo-curator/",
        # "https://developer.nvidia.com/blog/llm-performance-benchmarking-measuring-nvidia-nim-performance-with-genai-perf/",
        # "https://developer.nvidia.com/blog/integrate-and-deploy-tongyi-qwen3-models-into-production-applications-with-nvidia/",
        # "https://nvda.ws/3ETayyp",
        # Add any other URLs you are testing
    ]

    blog_post_urls = [ensure_trailing_slash(url) for url in blog_post_urls_input]

    output_dir = "nvidia_blackwell_architecture"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    if not blog_post_urls:
        print("The list of blog post URLs is empty.")
    else:
        print(f"Processing {len(blog_post_urls)} blog posts...")

        with requests.Session() as session:
            session.headers.update(BASE_HEADERS)

            for i, post_url in enumerate(blog_post_urls, start=1):
                print(f"\n--- Processing article {i} of {len(blog_post_urls)} ---")

                post_title, text_content = extract_blog_text_and_title(
                    session, post_url
                )

                if post_title.startswith("Error -"):
                    print(
                        f"  Skipping file creation for {post_url} due to error: {post_title}"
                    )
                    continue

                if not text_content.strip() and (
                    not post_title or post_title == "Untitled Article"
                ):
                    print(
                        f"  No significant title or content extracted for {post_url}. Skipping file creation."
                    )
                    continue

                safe_title = sanitize_filename(post_title)
                if not safe_title or safe_title == "untitled-article":
                    url_path_part = post_url.strip("/").split("/")[-1]
                    safe_title = (
                        sanitize_filename(url_path_part)
                        if url_path_part
                        else f"article_{i}"
                    )

                filename = f"{safe_title}.txt"
                filepath = os.path.join(output_dir, filename)

                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"Title: {post_title}\n")
                        f.write(f"URL: {post_url}\n\n")
                        f.write(text_content)
                    print(f"  Successfully saved: {filepath}")
                except IOError as e:
                    print(f"  Error writing file {filepath}: {e}")
                except (
                    Exception
                ) as e:  # Catch any other unexpected errors during file write
                    print(
                        f"  An unexpected error occurred while writing file for {post_url}: {e}"
                    )

        print("\n--- Done extracting blog posts ---")
