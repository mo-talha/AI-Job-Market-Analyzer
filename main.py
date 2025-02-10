import requests
import json
from bs4 import BeautifulSoup as bs


def fetch_job_descriptions():
    job_posting_ids = [
        268257,
        326866,
        235174,
        140884,
        317971
    ]

    job_despcriptions = []

    for job_id in job_posting_ids:
        job_postings_base_url = f"https://www.instahyre.com/api/v1/employer_public_jobs/{job_id}"
        payload = {}
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,en-IN;q=0.8',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
        }

        response = requests.request(
            "GET", job_postings_base_url, headers=headers, data=payload)

        if response.status_code == 200:
            job_data = response.json()
            job_despcription = job_data["description"]
            job_despcriptions.append(
                {f"job_description_{job_id}": job_despcription})
        else:
            print(response.status_code)

    print(job_despcriptions)


def extract_requirements(html):
    soup = bs(html, 'html.parser')
    requirements_heading = soup.find('strong', string='Requirements: ')
    if requirements_heading:
        requirements_list = requirements_heading.find_next('ul')
        if requirements_list:
            # Convert the list items to Markdown
            markdown_requirements = "- " + \
                "\n- ".join([li.get_text(strip=True)
                            for li in requirements_list.find_all('li')])
            return markdown_requirements
    return None


def get_requirements_from_jd():
    with open("job_descriptions.json", "r") as f:
        job_descriptions = json.load(f)

    requirements = []

    for job in job_descriptions:
        for key, html_content in job.items():
            # print(html_content)
            requirements_markdown = extract_requirements(html_content)
            requirements.append({
                "job_id": key,
                "requirements_markdown": requirements_markdown
            })
            # print(requirements_markdown)
    # soup = bs(requirments_html, 'html.parser')
    # print(requirements)
    return requirements


def create_markdown_prompt():
    requirements_markdown_list = get_requirements_from_jd()

    prompt = ""

    for markdown in requirements_markdown_list:
        markdown_text = markdown["requirements_markdown"]
        prompt += "\n Requirement: \n"
        prompt += f"{markdown_text} \n"

    # print(prompt)

    return prompt


def analyze_requirements_using_gemini():
    gemini_api_key = "AIzaSyDYqps0MVGueOodKZKl2AwbpX39KjB63KU"
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"

    prompt = """You need to analyze the give job requirements, let me know the most asked skills across the job requirements provided. """

    mark_down_requirements = create_markdown_prompt()

    prompt += f"\n {mark_down_requirements}"

    request_body = {
        "contents": [
            {
                "parts": [{
                    "text": prompt
                }]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        url=gemini_api_url, json=request_body, headers=headers)

    if response.status_code == 200:
        data = response.json()
        llm_response = data["candidates"][0]["content"]["parts"][0]["text"]

        print(llm_response)

        # return llm_response
    else:
        # Handle errors appropriately
        print(f"Error: {response.status_code} - {response.text}")
        return None

    # print(prompt)


def analyze_requirements_using_ollama():
    ollama_api_url = "http://127.0.0.1:11434/api/generate"
    prompt = """You need to analyze the give job requirements, let me know the most asked skills across the job requirements provided. """
    prompt += create_markdown_prompt()

    payload = {
        "model": "llama3.1:latest",
        "prompt": prompt,
        "stream": True
    }

    response = requests.post(ollama_api_url, json=payload)

    full_response = ""

    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            full_response += data.get("response", "")
            # print(data.get("response", ""), end="")

            # Check if the response is complete
            if data.get("done", False):
                print("\n\nFinal Response:\n", full_response)
                return full_response


def main():
    # fetch_job_descriptions()
    # get_requirements_from_jd()
    # create_markdown_prompt()
    analyze_requirements_using_ollama()
    # html = "<html><body><p><strong>Responsibilities: </strong></p><ul><li>Propose solutions to solve complex system architecture challenges and actively lead the end-to-end development of the system.</li><li>Create robust, flexible, consistent, and easy-to-use APIs.</li><li>Continuously strive for performance improvements, code reusability, and readability.</li><li>Understand the product in detail and predict potential issues in feature development.</li><li>Mentor and lead junior members of the team.</li></ul><p><br /></p><p><strong>Requirements: </strong></p><ul><li>Ability to think out of the box.</li><li>Tech or a higher degree in computer science or a related field.</li><li>1+ years of experience working on back-end development for complex distributed systems who are willing to adopt any programming language as required.</li><li>Familiarity with any of the following - Java, C++, Scala, Kotlin, and frameworks like Spring, Play, Hibernate, Django, etc.</li><li>Good understanding of Algorithms, Data Structure, OOP, Design patterns, Parallel programming, Multithreading concepts, and Event-Driven Systems.</li><li>Understanding of micro-services architecture and best practices.</li><li>Experience with Relational databases such as MySQL, PostgreSQL, Oracle, or any NoSQL database.</li><li>Familiarity with cloud platforms like AWS (Amazon Web Services), Azure, or Google Cloud.</li></ul></body></html>"
    # soup = bs(html, "html.parser")
    # requirements_heading = soup.find("strong", string='Requirements: ')
    # # print(requirements_heading)

    # requirements_list = requirements_heading.find_next('ul')
    # # print(requirements_list)

    # markdown_requirements = "- " + "\n- ".join([li.get_text(strip=True) for li in requirements_list.find_all("li")])
    # print(markdown_requirements)


if __name__ == "__main__":
    main()
