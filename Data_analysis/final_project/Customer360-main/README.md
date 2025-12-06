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

1. **Tổng quan khách hàng**
   - Khách hàng tập trung ở vùng nào và đóng góp bao nhiêu vào doanh thu?  
   - Tổng số đơn hàng, tổng chi tiêu trung bình theo vùng hoặc danh mục sản phẩm.  

2. **Hành vi mua hàng (RFM)**
   - Khách hàng nào là VIP, khách hàng at-risk, khách mới có tiềm năng?  
   - Có outlier về tần suất mua hoặc giá trị đơn hàng cần lưu ý không?  

3. **Lịch sử đơn hàng & sản phẩm**
   - Khách hàng thường mua sản phẩm nào?  
   - Sản phẩm/danh mục nào bán chạy hoặc có biến động bất thường?  
   - Sản phẩm nào có nguy cơ hết hàng (dựa trên bán trung bình và tồn kho)?  

4. **Đánh giá & Feedback**
   - Khách hàng nào đánh giá thấp hoặc có sentiment tiêu cực?  
   - Thời gian giao hàng ảnh hưởng đến rating và khả năng churn như thế nào?  

5. **Phân nhóm khách hàng & risk**
   - Cluster khách hàng thành nhóm VIP, trung bình, at-risk — nhóm nào quan trọng nhất?  
   - Nhóm khách nào dễ churn hoặc cần chiến dịch giữ chân?  

6. **Customer Churn & Retention**
   - Khách hàng nào có nguy cơ rời đi cao?  
   - Đặc điểm (recency, frequency, rating, delivery) nào liên quan mạnh đến churn?  
   - Hệ thống có thể gợi ý chiến dịch retention hiệu quả cho từng nhóm khách.  

7. **Khuyến nghị hành động kinh doanh**
   - Nên gửi voucher, flash sale hay chiến dịch marketing cho nhóm nào để tăng LTV?  
   - Sản phẩm/danh mục nào cần nhập thêm, tăng quảng cáo hoặc điều chỉnh tồn kho?  
   - Seller nào cần kiểm tra hoặc tối ưu vận hành để giảm giao trễ?  

8. **Tổng quan Customer 360**
   - Tạo bảng tổng hợp theo `customer_id` với RFM, lịch sử đơn, chi tiêu, đánh giá, cluster, churn score và các khuyến nghị hành động.  
   - Cung cấp dữ liệu trực quan và actionable insights cho chủ doanh nghiệp. 

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