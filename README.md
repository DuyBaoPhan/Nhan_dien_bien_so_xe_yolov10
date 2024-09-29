Giới thiệu
  Dự án này triển khai hệ thống nhận diện và quản lý biển số xe bằng cách sử dụng YOLOv10 để phát hiện đối tượng và EasyOCR để nhận diện ký tự trên biển số xe. Hệ thống cung cấp giao diện đồ họa (GUI) sử dụng PyQt5, cho phép người dùng xem luồng camera theo thời gian thực, phát hiện biển số xe và quản lý kết quả. Các biển số xe được nhận diện sẽ được lưu và hiển thị trong một bảng để theo dõi việc ra vào của các phương tiện trong bãi đỗ xe.

Tính năng
  Nhận Diện Biển Số Theo Thời Gian Thực: Hiển thị luồng camera trực tiếp và nhận diện biển số xe theo thời gian thực bằng YOLOv10.
  Nhận Diện Ký Tự Biển Số: Sử dụng EasyOCR để nhận diện ký tự trên biển số xe.
  Hiển Thị Biển Số Gần Đây: Hiển thị 5 biển số xe được phát hiện gần nhất cùng với thời gian và trạng thái (ra vào).
  Quản Lý Dữ Liệu: Tự động lưu thông tin biển số xe và trạng thái ra vào vào tệp CSV mà không xóa bất kỳ bản ghi nào.
  Tìm Kiếm: Bao gồm thanh tìm kiếm để tra cứu biển số xe cụ thể.
  Đếm Số Xe: Hiển thị tổng số xe hiện tại trong bãi đỗ xe.
  Giao Diện Thân Thiện: Xây dựng với PyQt5, cung cấp giao diện dễ sử dụng cho người dùng để xem luồng camera, kết quả phát hiện và theo dõi dữ liệu.
Các Thư Viện Cần Thiết
  Python 3.x
  PyQt5
  YOLOv10 (cho việc phát hiện đối tượng)
  EasyOCR (cho việc nhận diện ký tự)
  OpenCV (cho việc xử lý video và ảnh)
  Pandas (cho việc xử lý tệp CSV)
