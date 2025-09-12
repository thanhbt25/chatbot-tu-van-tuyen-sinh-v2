import os 
from dotenv import load_dotenv
import google.generativeai as genai

# Đọc file .dotenv
load_dotenv()

# Lấy giá trị biến môi trường
gemini_key = os.getenv("GEMINI_API_KEY")

# Khởi tạo Gemini 
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel("gemini-1.5-flash") # flash nhanh và free 

def paraphrase_response(user_question, bot_answer):
    promt = f"""
    Người dùng hỏi: {user_question}
    Bot trả lời: {bot_answer}

    Hãy trả lời bằng tiếng Việt thật tự nhiên, thân thiện giống như một cố vấn tuyển sinh, giải thích ngắn gọn và khuyến khích người dùng.
    """

    response = model.generate_content(promt)
    return response.text 

print(paraphrase_response('hom nay la ngay may', 'hom nay la ngay 30'))

