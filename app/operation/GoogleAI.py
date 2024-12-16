import google.generativeai as genai

from app.Configuration import Config


def google_gen_AI_response(model_prompt: str, input_data_from_user: str, question: str):
    genai.configure(api_key=Config.GOOGLE_API_KEY)

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    f"{input_data_from_user}\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    f"{model_prompt}\n",
                ],
            },
        ]
    )

    response = chat_session.send_message(question)

    print(response.text)

    return response.text

# if __name__ == "__main__":
#     input_data_from_user_input = """John Doe
#     Email: john.doe@example.com | Phone: +1-123-456-7890
#     LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe
#
#     Professional Summary
#     Backend Engineer with 4+ years of experience in designing, developing, and maintaining scalable backend systems. Proficient in Python, Django, and FastAPI, with a solid understanding of databases, RESTful APIs, and cloud services. Strong problem-solving skills with a passion for improving efficiency and implementing best practices in software development.
#
#     Skills
#     Languages: Python, Java, JavaScript
#     Frameworks: Django, FastAPI, Flask, Spring Boot
#     Databases: MySQL, PostgreSQL, MongoDB
#     APIs: REST, GraphQL
#     Cloud: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes
#     Tools: Git, Jenkins, Celery, Redis
#     Other: Microservices architecture, Unit Testing, TDD, CI/CD
#     Experience
#     Backend Engineer
#     ABC Tech Solutions | New York, NY
#     June 2020 – Present
#
#     Designed and implemented RESTful APIs for various internal services using Python, Django, and FastAPI, improving response times by 20%.
#     Integrated AWS services (EC2, S3, RDS) into backend systems, reducing infrastructure costs by 15%.
#     Optimized database queries and refactored data models for a 30% improvement in API performance.
#     Led the development of a microservices-based architecture, reducing deployment time by 40% and increasing system scalability.
#     Worked closely with front-end developers to ensure seamless integration of backend APIs with front-end features.
#     Set up and managed CI/CD pipelines using Jenkins and Docker, resulting in faster and more reliable deployments.
#     Junior Backend Developer
#     XYZ Innovations | San Francisco, CA"""
#     question = "Give me skills mention in text"
#
#     model_prompt_data = "Based on the information given in Material, answer the question given in query. \\\\nYour job is to use the given material as knowledge and you should not give any generalized answer which is not present in the information given in material.If question asked for a response in table format then make sure to segregate data column wise properly and not contain any html tags and respresent it in proper tabular form. If the user question is presented in a language other than English, please answer in that specific language while maintaining the context of the conversation in English. Ensure that the response is both concise and comprehensive."
#     google_gen_AI_response(model_prompt=model_prompt_data, input_data_from_user=input_data_from_user_input,
#                            question=question)
