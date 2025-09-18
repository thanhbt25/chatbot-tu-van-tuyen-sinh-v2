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
    Các câu hỏi có năm thì từ 2025 trở về thì không phải là dự kiến, hay dự đoán mà là chắc chắn, từ 2026 trở đi mới là dự kiến, nên bạn cân nhắc từ ngữ. 
    Đây là câu trả lời cuối cùng để đưa cho người dùng rồi nên bạn hãy viết cẩn thận hơn, ngoài ra phải cung cấp đẩy đủ thông tin mà truy vấn đưa ra, không được lược bớt. 
    Trình bày chúng dưới dạng câu văn bình thường, không dùng ký hiệu * hoặc gạch đầu dòng.
    """

    response = model.generate_content(promt)
    return response.text 

def major_info_answer(major: str, user_question):
    promt = f"""
    Người dùng hỏi: {user_question}
    Ngành nghề cần tư vấn: {major}

    Đây là câu hỏi tư vấn nghề nghiệp. 
    Hãy trả lời bằng tiếng Việt thật tự nhiên, thân thiện như một cố vấn tuyển sinh, giải thích ngắn gọn và cần phải chọn lọc thông tin thật chắc chắn, hãy tìm hiểu kĩ và có nguồn cẩn thận trước khi đưa ra câu trả lời.
    Có thể chèn đường link (bạn chèn) vào để người dùng tìm hiểu thêm.
    Đây là câu trả lời cuối cùng để đưa cho người dùng rồi nên bạn hãy viết cẩn thận, không được đưa thông tin sai lệch. 
    Trình bày chúng dưới dạng câu văn bình thường, không dùng ký hiệu * để in đậm hay gạch đầu dòng.
    """

    response = model.generate_content(promt)
    return response.text

def get_admission_proposal(school, user_question):
    promt = f"""
    Người dùng hỏi: {user_question}
    Trường mà người dung hỏi: {school}
    Đây là câu hỏi hỏi đề án tuyển sinh của trường. 
    Bạn hãy lấy năm tuyển sinh mới nhất và ghi rõ năm ra, nếu người dùng muốn năm mà vẫn chưa có thông tin thì ghi là không có dữ liệu.
    Bạn hãy trả lời bằng tiếng Việt thật tự nhiên, thân thiện như một cố vấn tuyển sinh, giải thích ngắn gọn và cần phải chọn lọc thông tin sao cho thật chắc chắn, tìm hiểu kĩ và có nguồn cẩn thận trước khi đưa ra câu trả lời. 
    Đây là câu trả lời cuối cùng để đưa cho người dùng rồi nên bạn hãy viết cẩn thận, không được đưa thông tin sai lệch, đừng viết là cần điền cái gì vào, do đây là câu hỏi cuối rồi nên phải đầy đủ thông tin. 
    Có thể chèn đường link (bạn chèn) vào để người dùng tìm hiểu thêm. 
    Trình bày chúng dưới dạng câu văn bình thường, không dùng ký hiệu * để in đậm hay gạch đầu dòng.
    """

    response = model.generate_content(promt)
    return response.text 

def get_chitchat_answer(user_messenge):
    promt = f"""
    Người dùng hỏi: {user_messenge}
    Đây là những câu hỏi ngoài phạm vi trả lời của chatbot. 
    Bạn hãy phải nhắc nhở người dùng rằng "đây không phải phạm vi trả lời của chatbot, bạn có thể tra cứu trên mạng" 
    Hãy trả lời một cách tự nhiên bằng tiếng Việt, thân thiện như một cố vấn tuyển sinh, và cần phải chọn lọc thông tin sao cho thật chắc chắn, tìm hiểu kĩ và có nguồn cẩn thận trước khi đưa ra câu trả lời. 
    Trình bày chúng dưới dạng câu văn bình thường, không dùng ký hiệu * để in đập hay gạch đầu dòng.
    """

    response = model.generate_content(promt)
    return response.text

def get_major_comparision_answer(user_question):
    promt = f"""
    Người dùng hỏi: {user_question}
    Đây là câu hỏi so sánh 2 ngành học với nhau, bạn nên đưa ra ưu nhược điểm của cả 2 ngành, và mỗi ngành phù hợp với người có tính cách như thế nào, tài chính ra sao, các môn học giỏi là các môn nào. 
    Hãy trả lời tự nhiên bằng tiếng việt như một tư vấn tuyển sinh, trả lời đầy đủ thông tin. Đừng viết là tôi cần điền link vào nhé mà bạn trực tiếp chèn vào đường link.
    Trình bày chúng dưới dạng câu văn bình thường, không dùng ký hiệu * để in đập hay gạch đầu dòng.
    """

    response = model.generate_content(promt)
    return response.text




