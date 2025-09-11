import pandas as pd
import numpy as np
import re
import os
import unidecode

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
SCORE_2023_CSV_PATH = os.path.join(BASE_DIR, '../public/diem_thi_thpt_2023.csv') 
SCORE_2024_CSV_PATH = os.path.join(BASE_DIR, '../public/diem_thi_thpt_2024.csv') 
SCORE_2025_CSV_PATH = os.path.join(BASE_DIR, '../public/diem_thi_thpt_2025.csv') 
SCORE_TEST_CSV_PATH = os.path.join(BASE_DIR, '../public/test.csv') 
SUBJECT_COMBINATION_PATH = os.path.join(BASE_DIR, '../public/tohopmon.csv')

class TinhDiemToHop:
    def __init__(self, data_path, subject_combination_path):
        """
        Khởi tạo lớp TinhDiemToHop

        Args:
            data_path (str): đường dẫn CSV chứa điểm thi (cột ví dụ: toan, van, ly, hoa, ngoai_ngu, ma_ngoai_ngu, ...)
            subject_combination_path (str): đường dẫn CSV chứa tổ hợp môn (cột ví dụ: ma_to_hop, mon1, mon2, mon3)
        """
        self.data_path = data_path
        self.subject_combination_path = subject_combination_path
        self.score_df = None
        self.subject_combination_df = None

        # Ánh xạ mã ngoại ngữ (ma_ngoai_ngu) -> tên môn chuẩn (dùng để so sánh)
        # Ví dụ: 'N1' => 'tieng_anh'
        self.ngoai_ngu_map = {
            'N1': 'tieng_anh',
            'N2': 'tieng_nga',
            'N3': 'tieng_phap',
            'N4': 'tieng_trung',
            'N5': 'tieng_duc',
            'N6': 'tieng_nhat'
        }

    def load_data(self):
        """
        Tải dữ liệu điểm thi và dữ liệu tổ hợp môn từ file CSV.
        Trả về True nếu load thành công, False nếu có lỗi.
        """
        try:
            self.score_df = pd.read_csv(self.data_path)
            self.subject_combination_df = pd.read_csv(self.subject_combination_path)
            return True
        except FileNotFoundError as e:
            print(f"Lỗi: không tìm thấy tệp. Chi tiết: {e}")
            # khởi tạo rỗng để tránh lỗi khi gọi hàm khác
            if self.score_df is None:
                self.score_df = pd.DataFrame()
            if self.subject_combination_df is None:
                self.subject_combination_df = pd.DataFrame()
            return False

    def get_subject_column_name(self, subject_name: str) -> str:
        """
        Chuẩn hóa tên môn từ file tohop để khớp với cột trong file điểm.
        - Nếu là môn ngoại ngữ (ví dụ: 'tiếng anh', 'tieng_anh') -> trả về 'tieng_anh' (chuẩn)
        - Các môn khác: chuyển về dạng không dấu, replace khoảng trắng bằng '_', ví dụ 'Toán' -> 'toan'
        """
        if not isinstance(subject_name, str):
            return ""

        s = subject_name.strip().lower()
        s_ascii = unidecode.unidecode(s)  # bỏ dấu
        s_ascii = re.sub(r'\s+', ' ', s_ascii).strip()  # chuẩn hóa khoảng trắng
        s_ascii = s_ascii.replace(' ', '_')

        # Danh sách tên ngoại ngữ chuẩn (sau unidecode)
        lang_list = ['tieng_anh', 'tieng_nga', 'tieng_phap', 'tieng_trung', 'tieng_duc', 'tieng_nhat']
        if s_ascii in lang_list or s_ascii.startswith('tieng_'):
            # trả về tên ngoại ngữ chính thức (ví dụ 'tieng_anh')
            return s_ascii

        # Các thay thế phổ biến (nếu cần)
        s_ascii = s_ascii.replace('lí', 'li')  # dự phòng nếu chưa unidecode
        # một số map bổ sung (nếu tên môn trong file có dạng khác)
        s_ascii = s_ascii.replace('toan', 'toan').replace('ly', 'li').replace('hoa', 'hoa') \
                         .replace('dia', 'dia').replace('su', 'su').replace('van', 'van') \
                         .replace('tin', 'tin_hoc')  # ví dụ nếu bạn muốn map 'tin' -> 'tin_hoc'

        return s_ascii

    def calculate_combined_scores(self):
        """
        Tính và thêm các cột điểm tổ hợp (ví dụ diem_A00) vào self.score_df.
        Nguyên tắc:
          - Với môn ngoại ngữ: file điểm chỉ có 2 cột liên quan: 'ngoai_ngu' (điểm) và 'ma_ngoai_ngu' (N1..N6)
            -> ta so sánh mã qua self.ngoai_ngu_map để lấy đúng hàng có ngoại ngữ tương ứng.
          - Với môn thông thường: cộng trực tiếp từ cột tương ứng.
          - Nếu một môn trong tổ hợp không tồn tại trong file điểm -> bỏ toàn bộ tổ hợp (in warning).
        """
        if self.score_df is None or self.subject_combination_df is None:
            print("Lỗi: dữ liệu chưa được tải. Gọi load_data() trước.")
            return None

        # đảm bảo các cột cần thiết tồn tại (phòng khi tên cột khác)
        # file điểm phải có cột 'ngoai_ngu' và 'ma_ngoai_ngu' nếu có ngoại ngữ
        has_ngoaingu_cols = ('ngoai_ngu' in self.score_df.columns) and ('ma_ngoai_ngu' in self.score_df.columns)
        if not has_ngoaingu_cols:
            # cảnh báo nhưng vẫn tiếp tục (có thể không có tổ hợp ngoại ngữ)
            print("Warning: file điểm không có cột 'ngoai_ngu' hoặc 'ma_ngoai_ngu'. Tổ hợp ngoại ngữ sẽ không được tính.")

        for _, row in self.subject_combination_df.iterrows():
            ma_to_hop = row.get('ma_to_hop') or row.get('ma') or row.get('code')  # linh hoạt tên cột
            mon_list = [row.get('mon1'), row.get('mon2'), row.get('mon3')]

            # bỏ qua tổ hợp không có mã
            if not ma_to_hop:
                print("Warning: tìm thấy tổ hợp không có 'ma_to_hop', bỏ qua.")
                continue

            # khởi tạo series tổng điểm (float) cho toàn bộ thí sinh
            total_score = pd.Series(0.0, index=self.score_df.index, dtype=float)

            is_valid_combination = True  # nếu có môn thiếu -> false

            for mon in mon_list:
                if not isinstance(mon, str) or not mon.strip():
                    # nếu thiếu môn trong tohop (NaN...), coi tổ hợp không hợp lệ
                    print(f"Warning: Tổ hợp {ma_to_hop} thiếu môn (mon={mon}). Bỏ tổ hợp.")
                    is_valid_combination = False
                    break

                mon_col = self.get_subject_column_name(mon)  # như 'toan', 'tieng_anh',...

                # Nếu là môn ngoại ngữ (tên giống 'tieng_xxx'), xử lý bằng ma_ngoai_ngu
                if mon_col.startswith('tieng_'):
                    if not has_ngoaingu_cols:
                        print(f"Warning: file điểm không có cột ngoại ngữ, không thể tính {mon} cho tổ hợp {ma_to_hop}")
                        is_valid_combination = False
                        break

                    # tạo mask: những hàng mà mã ngoại ngữ mapping thành cùng mon_col
                    # (ví dụ ma_ngoai_ngu 'N1' -> 'tieng_anh' so sánh với mon_col)
                    mapped_lang = self.score_df['ma_ngoai_ngu'].map(self.ngoai_ngu_map)
                    mask = mapped_lang == mon_col

                    # lấy điểm ngoại ngữ cho những hàng đó, convert số an toàn
                    s = pd.Series(0.0, index=self.score_df.index, dtype=float)
                    if mask.any():
                        s.loc[mask] = pd.to_numeric(self.score_df.loc[mask, 'ngoai_ngu'], errors='coerce').fillna(0.0)
                    # cộng vào tổng
                    total_score = total_score.add(s, fill_value=0.0)

                else:
                    # môn thông thường: phải có cột tương ứng trong file điểm
                    if mon_col in self.score_df.columns:
                        vals = pd.to_numeric(self.score_df[mon_col], errors='coerce').fillna(0.0)
                        total_score = total_score.add(vals, fill_value=0.0)
                    else:
                        print(f"Warning: không tìm thấy cột '{mon_col}' trong file điểm cho tổ hợp '{ma_to_hop}'. Bỏ tổ hợp.")
                        is_valid_combination = False
                        break

            # Sau khi duyệt hết 3 môn: nếu hợp lệ thì gán cột diem_{ma_to_hop}
            if is_valid_combination:
                col_name = f"diem_{ma_to_hop}"
                # convert lại thành float, tránh index alignment issues
                self.score_df[col_name] = total_score.astype(float).values
                print(f"Đã thêm cột '{col_name}' cho tổ hợp {ma_to_hop}: môn {mon_list}")
            else:
                print(f"Tổ hợp {ma_to_hop} không hợp lệ, đã bỏ.")

        return self.score_df

    def save_output(self, output_path):
        """
        Lưu DataFrame đã thêm điểm tổ hợp ra CSV.
        """
        if self.score_df is not None and not self.score_df.empty:
            self.score_df.to_csv(output_path, index=False)
            print(f"Đã lưu kết quả vào: {output_path}")
        else:
            print("Không có DataFrame để lưu. Hãy chạy calculate_combined_scores() trước.")

tinhDiemToHOp = TinhDiemToHop(SCORE_2025_CSV_PATH,SUBJECT_COMBINATION_PATH)
tinhDiemToHOp.load_data()
tinhDiemToHOp.calculate_combined_scores()
tinhDiemToHOp.save_output(os.path.join(BASE_DIR, '../public/diem_thi_thpt_2025_to_hop.csv'))

    

    

 