1️⃣ Vấn đề dữ liệu ngành trùng lặp

Trong CSV bạn có ten_nganh, nhưng mỗi trường đặt tên hơi khác nhau (ví dụ: “Công nghệ thông tin”, “Kỹ thuật phần mềm”, “Hệ thống thông tin” → đều thuộc nhóm CNTT).
👉 Bạn cần một bước chuẩn hóa ngành (major normalization):

Cách đơn giản (manual mapping): tạo 1 file mapping nganh_chuan.csv gồm:

ten_nganh_raw,major
An toàn không gian số - Cyber Security (CT tiên tiến),Công nghệ thông tin
Chương trình tiên tiến Kỹ thuật Thực phẩm,Kỹ thuật Thực phẩm
Hệ thống nhúng thông minh và IoT,Công nghệ thông tin
Kỹ thuật Hóa dược,Hóa dược
...


Cách nâng cao (sau này): dùng NLP fuzzy matching (fuzzywuzzy hoặc rapidfuzz) để gom ngành theo từ khóa.

2️⃣ Chuẩn bị dữ liệu training cho content-based matching

Từ CSV diem_chuan_dai_hoc.csv, bạn tạo bảng majors, ví dụ dạng:

major	avg_score	needed_subjects	avg_fee
Công nghệ thông tin	27.5	{"Toán": 10, "Lý": 8, "Hóa": 2}	37,000,000
Kỹ thuật Thực phẩm	21.5	{"Toán": 7, "Hóa": 9, "Sinh": 6}	35,000,000
Hóa dược	22.0	{"Toán": 6, "Hóa": 10, "Sinh": 5}	35,000,000

👉 Trong đó:

avg_score: lấy trung bình theo nhiều trường.

needed_subjects: đếm tần suất xuất hiện của môn trong các tổ hợp xét tuyển (A00, A01, B00,…). Ví dụ A00 = Toán, Lý, Hóa, thì bạn cộng +1 cho mỗi môn. Môn nào xuất hiện nhiều → trọng số cao.

avg_fee: trung bình học phí.

📌 Pandas có thể lưu dictionary trong 1 cell (cột object) nhưng khó query trực tiếp.
➡️ Giải pháp tốt hơn:

Lưu needed_subjects thành chuỗi JSON (vd: '{"Toán": 10, "Lý": 8, "Hóa": 2}').

Khi load thì dùng json.loads() để chuyển lại dict.

3️⃣ Tính điểm phù hợp (matching score)

Cho mỗi major, bạn tính compatibility score dựa trên input user:

Ví dụ công thức đơn giản (có thể mở rộng sau):

score = w1 * score_fit + w2 * subject_fit + w3 * finance_fit


score_fit: mức độ phù hợp giữa user_score và avg_score.
Ví dụ: 1 - abs(user_score - avg_score)/max_score

subject_fit: so khớp giữa liked_subject, disliked_subject với needed_subjects.

Nếu user thích môn nào → cộng theo trọng số frequency.

Nếu user ghét môn nào → trừ theo trọng số.

finance_fit: nếu finance_requirement >= avg_fee → 1, ngược lại giảm điểm.

4️⃣ Gợi ý ngành

Sau khi tính score cho tất cả majors → sort giảm dần → lấy top N ngành.

Ví dụ output:

[
  {"major": "Công nghệ thông tin", "match_score": 0.87},
  {"major": "Kỹ thuật Thực phẩm", "match_score": 0.75},
  {"major": "Hóa dược", "match_score": 0.65}
]