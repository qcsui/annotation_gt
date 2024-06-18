# Annotation of ground truth
## 文件结构
```txt
pdf_data_reviewer/
│
├── app/
│   ├── templates/
│   │   ├── base.html  # 基础HTML模板文件
│   │   ├── index.html  # 主页面HTML模板
│   │   └── review.html  # 用于显示和标注数据的页面
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css  # 存放CSS样式文件
│   │   ├── js/
│   │   │   └── script.js  # 存放JavaScript文件
│   │   └── images/  # 存放静态图片资源
│   ├── __init__.py  # 初始化Flask应用
│   ├── views.py  # 处理路由和视图函数
│   ├── models.py  # 处理数据模型（如果需要）
│   └── utils.py  # 辅助功能函数，例如文件解析
│
├── data/
│   ├── pdfs/  # 存放PDF文件
│   └── htmls/  # 存放从PDF提取的HTML数据
│
├── tests/
│   └── test_app.py  # 用于应用的单元测试
│
├── requirements.txt  # 存放所有依赖
└── run.py  # 启动Flask应用的脚本
```

