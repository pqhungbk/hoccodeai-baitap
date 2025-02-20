import os
import requests
import re
import subprocess
from openai import OpenAI

def get_webpage_content(url):
    bearer_token = os.getenv("BEARER_TOKEN")
    try:
        bearer_token = bearer_token
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f">>ChatBot: Lỗi khi lấy nội dung trang web: {e}")
    return response.text
def get_file_content(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        #Tách đoạn văn thành 2 câu một theo dấu "."
        sentences = re.findall(r"[^.!?]+[.!?]", text)
        content = []
        for i in range(0, len(sentences), 2):
            sentences1 = sentences[i]
            sentences2 = sentences[i+1].strip() if i+1 < len(sentences) else ""
            content.append(f"{sentences1} {sentences2}".strip())
        return content
    except FileNotFoundError:
        print(f">>ChatBot: Lỗi File '{path}' không tồn tại!")
        return []
    except Exception as e:
        print(f">>ChatBot: Lỗi khi đọc file: {e}")
        return []
def chatbot():
    api_key = os.getenv("OPENAI_API_KEY")
    print("""Xin chào! Tôi là trợ lý của bạn. Hãy trò chuyện với tôi nhé! 
    Hướng dẫn:
        - Gõ 'Bye' để thoát
        - Nếu bạn muốn tóm tắt webpage hãy nhập link website vào console.
        - Nếu bạn muốn dịch file hãy nhập "dịch" + enter để bắt đầu
        - Nếu bạn muốn bot giải toán hãy nhập "code" + enter để bắt đầu
    """)
    client = OpenAI(
        base_url="https://api.openai.com/v1",
        api_key=api_key
    )
    messages = []
    messages.append(
        {
            "role": "system",
            "content": "Your are a friendly and a good assistant"
        }
    )
    while True:
        user_input = input("\n>>Bạn: ").lower()
        url_pattern = r"https?://(?:www\.)?\S+\.\S+"
        if user_input == "bye":
            print(">>ChatBot: Tạm biệt! Hẹn gặp lại sau")
            break
        elif re.search(url_pattern, user_input):
            print(">>ChatBot: Chờ chút để tôi tóm tắt")
            messages.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )
            url = re.findall(url_pattern, user_input)[0]
            res = get_webpage_content("https://r.jina.ai/" + url)
            messages.append(
                {
                    "role": "user",
                    "content": f"""
                            I will provide the content of a webpage. Your task is to summarize its main points in Vietnamese in a clear and concise manner. Focus on key information, avoid unnecessary details, and ensure the summary is easy to understand.
                            Start the summary with "Trang web được tóm tắt như sau: " add a line break after it, and then write the summary.
                            End it with the provided link: "{url}"
                            Content of webpage: "{res}"
                        """
                }
            )
            stream = client.chat.completions.create(
                    messages = messages,
                    max_tokens=300,
                    model="gpt-4o-mini",
                    stream=True
                )
            print(">>ChatBot: ", end="")
            chat_complettion = ""
            for chunk in stream:
                print(chunk.choices[0].delta.content or "", end="")
                chat_complettion += chunk.choices[0].delta.content or ""
            messages.append(
                {
                        "role": "assistant",
                        "content": chat_complettion
                }
            )
        elif "dịch" in user_input.lower():
            print(f">>ChatBot: Nhập thông tin để tôi đọc file và dịch nhé")
            path = input("Đường dẫn file cần dịch: ")
            language = input("Ngôn ngữ cần dịch sang: ")
            output_path = input("Dường dẫn để lưu file đã dịch: ")
            print(f">>ChatBot: Chờ một chút nhé .....")
            file_content = get_file_content(path)
            file_translated_text = ""
            if file_content:
                for content in file_content:
                    message = [{
                        "role": "user",
                        "content": f"""
                                I will provide a text, and I want you to detect the source language and then translate it into {language}.
                                Steps:
                                - Detect the source language first.
                                - Translate the text accurately while ensuring natural flow and contextual appropriateness.
                                - Maintain formatting and structure as closely as possible.
                                - If the text contains idioms, cultural references, or technical terms, adapt them accordingly.
                                Only return the translated text, without any additional information or formatting
                                Here is the text to translate: "{content}"
                            """
                    }]
                    chat_complettion = client.chat.completions.create(
                        messages=message,
                        model = "gpt-4o-mini"
                    )
                    file_translated_text += chat_complettion.choices[0].message.content
                
                with open(output_path, "w", encoding="utf-8") as file:
                    file.write(file_translated_text)
                print(f">>ChatBot: Lấy file dịch ở đây nhé {output_path}")
        elif "code" in user_input.lower():
            print(f">>ChatBot: Nhập đề bài đi bạn")
            input_problem = input("\n>>Bạn: ").lower()
            print(f">>ChatBot: Chờ chút nhé ......")
            message = [{
                    "role": "user",
                    "content": f"""
                            I will provide a problem statement. Please write a Python program to solve it.
                            Requirements:
                            - Ensure the solution is correct and efficient.
                            - Use clear variable names and proper comments to explain key steps.
                            - If there are multiple ways to solve the problem, choose the most optimal approach.
                            - If necessary, include edge case handling and input validation.
                            Give me only code.
                            Here is the problem statement: {input_problem}
                        """
                }]
            chat_complettion = client.chat.completions.create(
                    messages=message,
                    model = "gpt-4o-mini"
            )
            
            with open("final.py", "w", encoding="utf-8") as file:
                file.write(chat_complettion.choices[0].message.content.replace("""```""", "").replace("python", ""))
            print(f">>ChatBot: Code được lưu ở đây nhé final.py")
            print(">>ChatBot: Run thử code >> python final.py")
            subprocess.run(["python", "final.py"])

        else:
            messages.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )
            stream = client.chat.completions.create(
                    messages = messages,
                    max_tokens=300,
                    model="gpt-4o-mini",
                    stream=True
                )
            print(">>ChatBot: ", end="")
            chat_complettion = ""
            for chunk in stream:
                print(chunk.choices[0].delta.content or "", end="")
                chat_complettion += chunk.choices[0].delta.content or ""
            messages.append(
                {
                        "role": "assistant",
                        "content": chat_complettion
                }
            )
            
if __name__ == "__main__":
    chatbot()