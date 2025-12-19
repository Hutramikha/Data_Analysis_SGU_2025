# Customer 360 Analysis - Olist Dataset

## Tổng quan dự án

Mục tiêu của dự án là xây dựng **Customer 360 View** từ dữ liệu Olist, cung cấp cái nhìn tổng quan về vòng đời khách hàng, hành vi mua sắm, chi tiêu, đánh giá và nguy cơ rời bỏ doanh nghiệp (churn). Dự án kết hợp **phân tích dữ liệu, trực quan hóa, mô hình RFM/Clustering, dự đoán churn và NLP để phân tích sentiment bình luận khách hàng**, đồng thời triển khai các công cụ tương tác dữ liệu:

- **Streamlit App:** cho phép người dùng chọn và xem chi tiết vòng đời từng khách hàng.  
- **n8n Chatbot:** hỗ trợ chủ doanh nghiệp với **khuyến nghị hành động kinh doanh, cảnh báo tự động** và gợi ý quyết định dựa trên dữ liệu.  
- **PowerBI:** dashboard trực quan tổng hợp các insight về hành vi, phân nhóm, RFM, churn và đánh giá sentiment từ bình luận.

---

## Dataset

Sử dụng **Olist Brazilian E-Commerce dataset**:

- `customers.csv`: Thông tin khách hàng.
- `orders.csv`: Thông tin đơn hàng.
- `order_items.csv`: Chi tiết sản phẩm trong đơn.
- `products.csv`: Thông tin sản phẩm.
- `sellers.csv`: Thông tin người bán.
- `order_payments.csv`: Phương thức thanh toán, giá trị.
- `order_reviews.csv`: Đánh giá và feedback khách hàng.
- `geolocation.csv`: Thông tin địa lý.
- `product_category_name_translation.csv`: Dịch tên danh mục sản phẩm.

---

## Câu hỏi nghiên cứu (Research Questions)

### **1. Phân tích mô tả**

#### 1.1. Địa lý & Khả năng tiếp cận
**Mục tiêu**: Xác định khách hàng ở đâu và việc phục vụ họ khó khăn thế nào?
- Số lượng thành phố đóng góp 80% khách hàng? (Pie Chart, Quy tắc: 20 - 80)
- Top 10 thành phố đông khách nhất? (Bar Chart)
- Trung bình khách ở từng bang, miền phải trả bao nhiêu tiền ship & chờ bao nhiêu ngày? (Bar Chart)
> Kết hợp bảng đồ để mô tả vùng cho thực
#### 1.2. Tài chính & Chi tiêu
**Mục tiêu:** Đánh giá sức mua và độ "chịu chi" của khách
- Phân phối giá trị đơn hàng như thế nào? Đa số khách mua đơn hàng giá bao nhiêu? (Box Plot)
- Có bao nhiêu khách hàng mua đơn hàng có giá trị đột biến (cực lớn)? (Sử dụng tứ phân vị xác định 25% khách hàng mua với giá trị cao)
- Tỷ lệ phí vận chuyển trên giá trị hàng (Freight / Price) là bao nhiêu?  Khách hàng có chấp nhận mua món rẻ tiền nhưng phí ship cao không? (Histogram)

#### 1.3. Hành vi thanh toán
**Mục tiêu:** Hiểu thói quen tài chính và tín dụng (Đặc biệt quan trọng ở Brazil).
- Tỷ lệ đơn sử dụng Credit Card, Boleto (tiền mặt), Voucher, Debit Card là bao nhiêu? (Pie Chart => credit_card)
- Số kỳ trả góp phổ biến là bao nhiêu (1, 3, 6 hay 12 lần)? (Bar Chart)
- Có mối liên hệ nào giữa Giá trị đơn hàng lớn và Số kỳ trả góp không? (Mua đắt thì trả góp dài?). (Scatter Plot)

#### 1.4. Sản phẩm quan tâm
**Mục tiêu:** Xác định nhu cầu và sở thích của khách hàng.
- Những danh mục sản phẩm nào đang mang lại nhiều khách hàng nhất? (Bar Chart)
- Có tháng nào trong năm mà một danh mục `cụ thể` tăng vọt không? (Line Chart)

#### 1.5. Trải nghiệm & Sự hài lòng
**Mục tiêu:** Đo lường "Cảm xúc" của khách hàng sau khi mua.
- Điểm đánh giá trung bình (Review Score) toàn sàn là bao nhiêu? Tỷ lệ 5 sao vs 1 sao? (Bar Chart)
- Chênh lệch giữa "Ngày giao dự kiến" và "Ngày giao thực tế" là bao nhiêu? (Giao sớm hay giao trễ?). (Histogram)
- Bao nhiêu % đơn hàng bị giao trễ? Bao nhiêu % đơn hàng nhận 1 sao?

----

### **2. Phân tích khám phá**

#### 2.1. Địa lý & Vận hành
**Mục tiêu**: Tìm hiểu xem yếu tố địa lý ảnh hưởng tiêu cực/tích cực thế nào đến trải nghiệm khách hàng.
- Có mối tương quan tuyến tính nào giữa Khoảng cách địa lý (Seller đến Customer) và Phí vận chuyển không? (Hay phí ship bị ảnh hưởng bởi kích thước hàng hóa nhiều hơn?).
- Khách ở vùng xa có chịu phí cao hơn? 

#### 2.2. Phân tích Giỏ hàng
**Mục tiêu**: Dù khách mua 1 lần, nhưng ta muốn khám phá xem họ kết hợp các sản phẩm như thế nào.
- Những danh mục nào thường xuyên xuất hiện cùng nhau trong một đơn hàng? (Ví dụ: Khách mua bed_bath_table có thường mua kèm furniture_decor không?).
- Có mối liên hệ nào giữa số lượng sản phẩm (Quantity) và Giá trị trung bình mỗi món (Unit Price)? (Khách mua nhiều món thường là món rẻ, hay đại gia mua nhiều món đắt?).

#### 2.3. Động lực của Sự hài lòng
**Mục tiêu**: Tìm ra "thủ phạm" thực sự khiến khách hàng đánh giá thấp/cao.
- Biểu đồ tương quan giữa "Số ngày giao hàng" và "Review Score"? Có phải cứ giao > 10 ngày là điểm rớt xuống dưới 3 sao?
- Mối quan hệ giữa "Gap Time" (Ngày giao thực tế - Ngày giao dự kiến) và Review Score. Khách hàng ghét việc "chờ lâu" hay ghét việc "bị thất hứa" hơn?
- Liệu khách hàng có giá trị thanh toán cao (payment_value) có xu hướng cho điểm đánh giá thấp hơn do kỳ vọng dịch vụ cao hơn hay không?

-----

### **3. Phân tích chẩn đoán**
#### 3.1 Chẩn đoán "Tiếng nói khách hàng" (NLP tìm negative + AI model phân loại điểm nghẽn)
**Mục tiêu**: Giải mã lý do thực sự đằng sau các con số 1 sao, 2 sao. Dữ liệu số (Rating) chỉ cho biết mức độ, dữ liệu chữ (Comment) mới cho biết nguyên nhân.
- Có trường hợp nào khách đánh giá 1-2 sao nhưng comment tích cực không? Tại sao?
- Trong tổng số các đánh giá tiêu cực (1-2 sao), tỷ lệ phần trăm dành cho các vấn đề liên quan đến Vận Chuyển (Logistics) và các vấn đề do Người Bán (Seller) gây ra (thường liên quan đến sản phẩm) là bao nhiêu?

----

### **4. Phân tích dự đoán**
#### 4.1 Phân cụm Khách hàng (Clustering, unsupervised learning)
**Mục tiêu**: Tự động gom nhóm khách hàng có hành vi tương đồng mà không cần định nghĩa trước.

#### 4.2 Sự rời bỏ (Churn)
**Mục tiêu**: Dự đoán các tập khách đang hoạt động có thể rời bỏ sàn trong 150 ngày tới không?

---

## Triển khai

- **Streamlit App:**  
  - Cho phép người dùng chọn khách hàng và xem toàn bộ vòng đời, lịch sử giao dịch, RFM, cluster và churn score.  
  - Có nút "Gợi ý hành động" để gọi **n8n Chatbot** nhận khuyến nghị kinh doanh dựa trên dữ liệu.  

- **n8n Chatbot:**  
  - Hỗ trợ chủ doanh nghiệp với **khuyến nghị hành động**, cảnh báo tự động và gợi ý quyết định (ví dụ: restock, campaign, kiểm tra seller).  
  - Trả lời câu hỏi liên quan Customer360, KPI, trend và insight hành vi khách hàng.  

- **PowerBI:**  
  - Dashboard tổng quan, trực quan hóa RFM, phân nhóm khách hàng, churn, sentiment analysis từ bình luận. 

---

## Kết quả kỳ vọng

- Bản tổng quan **Customer 360 View** cho từng khách hàng.  
- Insight về hành vi mua hàng, giá trị khách hàng, khả năng churn.  
- Hệ thống tương tác: **click vào khách hàng → xem vòng đời → chatbot trả lời → báo cáo trực quan trên PowerBI**.  

## Cấu trúc thư mục

```text
olist-customer-lifecycle/
│
├── 📁 data
│   ├── 📁 1_raw
│   ├── 📁 2_clean
│   └── 📁 3_model
├── 📁 notebooks
│   ├── 📄 01_data_understanding.ipynb
│   ├── 📄 02_data_cleaning.ipynb
│   ├── 📄 03_EDA.ipynb
│   ├── 📄 04_feature_engineering.ipynb
│   └── 📄 05_modeling.ipynb
├── 📁 output
│   ├── 📁 image
│   ├── 📁 n8n
│   │   └── 📘 knowledege_file.docx
│   ├── 📁 powerBI
│   ├── 📁 report
│   └── 📁 streamlit
├── 📝 README.md
└── 📄 requirements.txt
```

---