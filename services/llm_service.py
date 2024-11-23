import zhipuai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.client = zhipuai.ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY'))
        
    def get_major_qa(self, major_info):
        prompt = f"""
        请你作为一个专业的教育顾问，为以下专业提供详细的问答信息：

        专业名称：{major_info['major_name']}
        学科类别：{major_info['subject_name']}
        门类：{major_info['category_name']}

        请提供以下方面的信息：
        1. 这个专业主要学什么？
        2. 这个专业的主要课程有哪些？
        3. 这个专业的就业方向有哪些？
        4. 这个专业需要什么特质或能力？
        5. 这个专业的发展前景如何？

        请用清晰的问答格式回答。
        """

        response = self.client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        return response.choices[0].message.content