## Cài đặt và khởi tạo dự án Rasa
1. Cài đặt Rasa 
```
python -m venv .venv # tạo thư mục venv để chạy môi trường ảo 
.venv\Scripts\activate # khởi động venv 
pip install rasa
```
2. Khởi tạo dự án: dùng lệnh `rasa init` để tạo một dự án chatbot đơn giản p
```
rasa init 
```
- Lệnh hỏi là muốn train model luôn không. Gõ `y` và nhấn Enter để Rasa tự động train mô hình demo 
3. Cấu trúc file 
- `data/nlu.yml`: Nơi bạn định nghĩa intents và các câu mẫu của người dùng.

- `data/rules.yml`: Nơi bạn định nghĩa các quy tắc hội thoại đơn giản.

- `data/stories.yml`: Nơi bạn định nghĩa các kịch bản hội thoại mẫu.

- `domain.yml`: Nơi bạn định nghĩa các intents, responses, entities, và actions.

- `config.yml`: Nơi bạn cấu hình các thành phần NLP và thuật toán huấn luyện.

- `actions/actions.py`: Nơi bạn viết các custom actions (hành động tùy chỉnh).

4. Chạy dự án 
```
rasa shell 
```

## Định nghĩa Intent và NLU 
1. Mở file `data/nlu.yml`: là nơi định nghĩa các ý định à các ví dụ câu nói của người dùng 
2. Intent: Mỗi intent có một tên duy nhất, và bạn phải cung cấp ít nhất 10 ví dụ về cách người dùng có thể diễn đạt ý định đó 
3. Bạn cung cấp càng nhiều ví dụ cho mỗi intent, mô hình NLU của Rasa càng chính xác hơn. 
4. Nếu có thực thể kèm theo thì bạn cần phải đánh dấu
- Entities là các thông tin quan trọng mà chatbot cần trích xuất từ câu nói của người dùng. Ví dụ: trường đại học, tên ngành, số điểm,...
- Sử dụng cú pháp [tên_thực_thể](tên_entity) để chỉ định vị trí của thực thể trong câu mẫu 
```
- intent: diem_chuan
  examples: |
    - điểm chuẩn ngành [kinh tế quốc dân](truong) là bao nhiêu?
    - cho mình xin điểm chuẩn trường [đại học y hà nội](truong)
    - điểm chuẩn [đại học bách khoa hn](truong) ngành [công nghệ thông tin](nganh)
    - điểm chuẩn ngành [công nghệ sinh học](nganh) trường [khoa học tự nhiên](truong) là bao nhiêu?
```
- Bạn cần khai báo lại Entities vào phần domain.yml để rasa hiểu 
## Định nghĩa Responses và Domain 
Sau khi định nghĩa các intent thì bạn cần cho chatbot biết nó phải phản ứng lại như thế nào
1. Mở file `domain.yml`: file đóng vai trò là "từ điển
 của chatbot, nơi bạn khai báo tất cả Intent, Responses, Actions và Entities
2. Lưu ý
- Bạn phải khai báo lại các intent đã tạo trong file nlu.yml vào đây
- Mỗi Response được đặt với tiền tốt `utter_`
- Bạn có thể cung cấp nhiều câu trả lời khác nhau cho cùng một Response để chatbot không bị lặp lại 
```
  utter_chao_hoi:
  - text: "Chào bạn, tôi có thể giúp gì cho bạn?"
  - text: "Chào, tôi là bot tư vấn tuyển sinh. Bạn muốn hỏi gì?"
```

## Định nghĩa Actions và Rules 
Bạn đã có Intents và Entites rồi! Bây giờ bạn cần tạo ra một luồng hội thoại. Bạn có thể làm điều đó bằng Rules và Actions
1. Rules
- Rules là những đoạn hội thoại ngắn, đơn giản và không có ngữ cảnh. Một Rule chỉ hoạt động khi một Intent cụ thể được kích hoạt 
```
rules:
  - rule: chào
    steps:
    - intent: chao_hoi
    - action: utter_chao_hoi
```
- Ý nghĩa: Nếu người dùng có ý định chao_hoi, chatbot sẽ thực hiện hành động utter_chao_hoi
- utter_ là tiền tố các responses mà bạn định nghĩa trong domain.yml => là loại action mặc định của Rasa

2. Định nghĩa Custom Actions 
- Với các tác vụ phức tạp hơn như tra cứu điểm chuẩn hoặc dự đoán cơ hội đỗ, bạn không thể dùng Rules và utter_ responses. Bạn cần tạo một Custom Action.
1. Mở file actions/actions.py.
2. Viết code cho Custom Action: Đây là nơi bạn sẽ lập trình logic cho chatbot của mình.
3. Lưu ý:
- `ActionDiemChuan` là một class kế thừa từ Action.
- Phương thức `name` trả về tên của action.
- Phương thức `run` chứa logic chính. Bạn sẽ dùng `tracker` để lấy các entity, xử lý dữ liệu và dùng `dispatcher` để gửi câu trả lời.

3. Cập nhật domain.yml 

## Huấn luyện và chạy thử Chatbot
1. Huấn luyện mô hình 
```
rasa train 
```
- Lệnh này sẽ xây dựng lại mô hình. Rasa đọc các file `nlu.yml`, `rules.yml`, `domain.yml` và các file khác để tạo mô hình nén
- Nếu không có lỗi thì sẽ thấy thông báo "Your Rasa model is trained and saved at 'models/...'."

2. Chạy Action Server
Nếu bạn tạo Custom Action (action_diem_chuan) thì cần một máy chủ riêng để thực thi hành động này 
2.1. Mở một Terminal mới và đi đến thư mục dự án 
2.2. Chạy lệnh
```
rasa run actions  --debug 
```
- Lệnh sẽ khởi động 1 máy chủ API nhỏ, khi Rasa cần thực thi `action_diem_chuan`, nó sẽ gửi yêu cầu đến máy chủ này 

3. Chạy Chatbot trong Shell 
Sau khi mô hình và máy chủ Action đều đang chạy, bạn có thể tương tác với chatbot
3.1. Quay lại Terminal đầu tiên (nơi chyaj rasa train)
3.2. Chạy lệnh sau để bắt đầu cuộc trò chuyện 
```
rasa shell --endpoints endpoints.yml
```

## Kết hợp mọi thứ bằng Stories
Bây giờ bạn sẽ sử dụng Stories để dạy cho chatbot cách xử lý các cuộc hội thoại phức tạp hơn, có nhiều bước và cần ghi nhớ ngữ cảnh.
1. Mở file `data/stories.yml`
File này chứa các kịch bản hội thoại mẫu. Mỗi story sẽ có một tên và một chuỗi các bước. 
2. Thêm Stories cho dự án 
```
version: "3.1"

stories:
  - story: Kịch bản hỏi điểm chuẩn
    steps:
      - intent: chao_hoi
      - action: utter_chao_hoi
      - intent: diem_chuan
        entities:
          - truong: "đại học bách khoa hn"
          - nganh: "công nghệ thông tin"
      - action: action_diem_chuan

  - story: Kịch bản hỏi cơ hội đỗ
    steps:
      - intent: co_hoi_do
        entities:
          - diem: "25"
          - nganh: "cơ khí"
          - truong: "bách khoa hn"
      - action: action_tu_van_co_hoi_do

  - story: Kịch bản hỏi thiếu thông tin
    steps:
      - intent: diem_chuan
      - action: utter_diem_chuan
      - intent: diem_chuan
        entities:
          - truong: "kinh tế quốc dân"
          - nganh: "marketing"
      - action: action_diem_chuan
```
3. Phân tích các Stories
- Kịch bản hỏi điểm chuẩn:
    - Người dùng bắt đầu bằng chao_hoi, chatbot trả lời utter_chao_hoi.
    - Sau đó người dùng hỏi về điểm chuẩn (diem_chuan) kèm theo các thực thể (truong, nganh).
    - Chatbot thực hiện action_diem_chuan (hành động tùy chỉnh mà bạn đã viết code ở Bài học 5).

- Kịch bản hỏi cơ hội đỗ:
    - Kịch bản này bắt đầu trực tiếp với ý định co_hoi_do và các thực thể cần thiết.
    - Chatbot thực hiện action_tu_van_co_hoi_do (hành động này bạn sẽ tự lập trình sau).

- Kịch bản hỏi thiếu thông tin:
    - Người dùng hỏi diem_chuan nhưng thiếu các thực thể.
    - Chatbot trả lời utter_diem_chuan ("Bạn muốn hỏi trường nào và ngành gì?").
    - Người dùng cung cấp thêm thông tin, và chatbot tiếp tục xử lý.

3. Stories khác Rules ở đâu?
- Rules được dùng cho những đoạn hội thoại ngắn, không cần ngữ cảnh, luôn luôn đúng. Ví dụ: khi người dùng chào thì bot luôn chào lại.

- Stories được dùng để huấn luyện chatbot xử lý các đoạn hội thoại nhiều bước, nơi mà thứ tự và ngữ cảnh là quan trọng. Rasa sẽ dùng Machine Learning để học các luồng này và có thể xử lý các kịch bản tương tự mà bạn chưa từng định nghĩa.

## Slots và Forms

## Pipeline và Config 

## Tích hợp và triển khai 
1. Tạo 1 server public bằng ngrok 
- Bước 1. Tải trên trang chủ của ngrok 
- Bước 2. Viết lệnh chạy trên terminal 
```
ngrok http 5006
```
- Lưu ý: 5006 là cổng mà rasa đang chạy, chạy lệnh cổng ngay trên terminal để tránh xung đột với cổng có sẵn đã chạy (phần dưới)
2. Chạy server bằng rasa
- Sau khi ngrok chạy xong thì lấy link forwarding url của ngrok và gán vào `webhook_url` trong file `credentials.yml`
```
rasa run --enable-api --cors "*" --debug -p 5006
```