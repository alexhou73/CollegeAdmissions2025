# 2025年全国大学（普通）招生情况可视化大屏

## 项目简介 (Project Introduction)

本项目是一个基于Flask + ECharts的大学招生数据可视化系统，旨在以直观的图表和地图形式展示2025年全国普通批次大学招生情况。系统提供了多维度的数据分析和交互式可视化功能，帮助用户深入了解全国各省市的大学分布情况、招生计划和院校层次分布。

This project is a university admission data visualization system based on Flask + ECharts, designed to display the 2025 national university admission situation in an intuitive chart and map format. The system provides multi-dimensional data analysis and interactive visualization features to help users understand the distribution of universities, enrollment plans, and institutional levels across provinces and cities in China.

## 主要功能 (Key Features)

### 📊 数据可视化组件
- **中国地图可视化**: 显示各省大学数量分布，支持缩放、拖拽、省份点击查看详情
- **各省大学数量环形图**: 展示各省大学数量对比和占比情况
- **大学层次占比饼图**: 显示985、211、216等不同层次大学的分布情况
- **城市级别统计**: 点击省份后显示该省内各城市的大学分布

### 📈 统计信息面板
- **综合统计**: 大学总数、985大学、双一流大学、211大学数量
- **院校性质**: 公办大学、民办大学、其他类型院校统计
- **招生计划**: 2025年计划招生总数统计
- **动态切换**: 支持全国和省份级别的统计数据切换

### 🔍 交互功能
- **地图交互**: 支持地图缩放、拖拽、省份点击查看详情
- **省份筛选**: 点击省份查看该省详细的大学分布情况
- **数据分页**: 大学详细信息表格支持分页浏览
- **实时筛选**: 支持按省份筛选大学详细信息

### 📋 详细信息表格
- **学校基本信息**: 学校代码、学校名称、层次、位置
- **招生信息**: 专业代码、2025年计划招生数、估分范围
- **页码信息**: 对应招生简章的页码范围
- **智能分页**: 每页显示10所大学，支持翻页浏览

## 技术栈 (Technology Stack)

### 后端 (Backend)
- **Flask**: Python web框架，提供RESTful API
- **pandas**: 数据处理和分析
- **openpyxl**: Excel文件读取和处理
- **flask-cors**: 跨域资源共享支持

### 前端 (Frontend)
- **HTML5/CSS3**: 现代web标准
- **JavaScript**: 交互逻辑处理
- **ECharts**: 数据可视化图表库
- **Ajax**: 异步数据请求

### 数据源 (Data Source)
- **Excel文件**: 2025.xlsx (包含普通批次大学招生数据)
- **GeoJSON**: 中国及各省份地理数据文件

## 安装说明 (Installation)

### 环境要求 (Requirements)
- Python 3.7+
- 推荐使用Anaconda或虚拟环境

### 依赖安装 (Dependencies Installation)

```bash
# 安装必要的Python包
pip install flask flask-cors pandas openpyxl

# 或者使用conda安装
conda install flask pandas openpyxl
conda install -c conda-forge flask-cors
```

### 数据文件准备 (Data Preparation)
确保项目根目录包含以下文件：
- `2025.xlsx`: 大学招生数据Excel文件
- `static/maps/china.json`: 中国地图GeoJSON文件
- `static/maps/[省份].json`: 各省份地图GeoJSON文件

## 使用方法 (Usage)

### 启动服务 (Start Service)

```bash
# 克隆项目到本地
git clone [项目地址]
cd CollegeAdmissions2025

# 启动Flask应用
python app.py
```

### 访问应用 (Access Application)

服务启动后，在浏览器中访问：
- **主页面**: http://localhost:5001/
- **健康检查**: http://localhost:5001/test
- **API测试**: http://localhost:5001/api/province_level_stats

### 操作指南 (Operation Guide)

1. **查看全国概况**: 打开主页面即可看到全国大学分布概况
2. **省份详情查看**: 点击地图上的省份，查看该省详细信息
3. **城市分布**: 在省份视图下，可以看到该省各城市的大学分布
4. **数据筛选**: 使用底部的大学详细信息表格进行数据筛选和分页浏览
5. **返回全国视图**: 点击地图外的区域或刷新页面返回全国视图

## API接口 (API Endpoints)

### 主要接口列表

| 接口路径 | 方法 | 描述 | 参数 |
|---------|------|------|------|
| `/` | GET | 主页面 | 无 |
| `/test` | GET | 服务健康检查 | 无 |
| `/api/province_level_stats` | GET | 获取省份层次统计数据 | 无 |
| `/api/city_university_stats` | GET | 获取城市大学统计 | province |
| `/api/province_level_distribution` | GET | 获取省份层次分布 | province |
| `/api/university_details` | GET | 获取大学详细信息 | page, page_size, province |
| `/api/province_stat_bar` | GET | 获取省份统计柱状图数据 | province |

### 接口示例 (API Examples)

```bash
# 获取全国统计数据
curl http://localhost:5001/api/province_level_stats

# 获取山西省城市统计
curl http://localhost:5001/api/city_university_stats?province=山西

# 获取大学详细信息（第一页）
curl http://localhost:5001/api/university_details?page=1&page_size=10
```

## 项目结构 (Project Structure)

```
CollegeAdmissions2025/
├── app.py                  # Flask主应用文件
├── 2025.xlsx              # 大学招生数据源文件
├── README.md              # 项目说明文档
├── static/                # 静态资源目录
│   ├── echarts.min.js     # ECharts库文件
│   ├── china.js           # 中国地图脚本
│   └── maps/              # 地图数据目录
│       ├── china.json     # 中国地图GeoJSON
│       └── [省份].json    # 各省份地图GeoJSON
├── templates/             # HTML模板目录
│   └── index.html         # 主页面模板
└── commands.txt           # 开发命令记录
```

## 数据说明 (Data Description)

### Excel数据结构
项目使用的Excel文件包含以下主要字段：
- **学校代码**: 大学的唯一标识代码
- **学校名称**: 大学的完整名称
- **层次**: 大学层次（985、211、216、公办、民办等）
- **位置**: 大学所在的省份和城市
- **专业代码**: 招生专业的代码
- **25计划**: 2025年计划招生人数
- **25估分**: 2025年预估录取分数
- **页码**: 在招生简章中的页码位置

### 数据处理逻辑
- **去重处理**: 相同学校名称的记录会被合并统计
- **省份提取**: 从位置信息中自动提取省份名称
- **城市识别**: 智能识别和标准化城市名称
- **数据验证**: 自动验证和清洗异常数据

## 开发说明 (Development Notes)

### 核心功能实现
1. **数据加载**: 使用pandas读取Excel文件，自动处理中文编码
2. **省份映射**: 实现了省份名称的智能提取和标准化
3. **城市识别**: 支持多种城市名称格式的自动识别
4. **地图集成**: 与ECharts地图组件深度集成，支持多级地图切换
5. **分页处理**: 实现了高效的数据分页和筛选功能

### 性能优化
- **数据缓存**: 合理使用数据缓存减少重复计算
- **分页加载**: 大数据量采用分页加载提升用户体验
- **异步请求**: 前端使用Ajax异步加载数据
- **资源压缩**: 静态资源采用压缩版本

## 故障排除 (Troubleshooting)

### 常见问题

1. **模块导入错误**
   ```bash
   ModuleNotFoundError: No module named 'flask_cors'
   ```
   解决方案：确保安装了所有依赖包
   ```bash
   pip install flask-cors
   ```

2. **端口占用**
   ```bash
   Address already in use
   ```
   解决方案：更改端口或终止占用进程
   ```bash
   lsof -i :5001
   kill -9 [PID]
   ```

3. **Excel文件读取错误**
   - 确保2025.xlsx文件存在且格式正确
   - 检查文件是否包含"普通批"工作表
   - 验证文件编码和字段名称

4. **地图显示异常**
   - 检查static/maps/目录下的GeoJSON文件是否完整
   - 确认ECharts库文件加载正常
   - 验证网络连接用于地图数据加载

## 贡献指南 (Contributing)

欢迎提交Issue和Pull Request来改进这个项目。在提交代码前，请确保：

1. 代码符合Python PEP8规范
2. 添加必要的注释（推荐使用英文）
3. 测试新功能的兼容性
4. 更新相关文档

## 许可证 (License)

本项目采用MIT许可证，详情请参见LICENSE文件。

## 联系方式 (Contact)

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本项目仅用于教育和研究目的，所有数据来源于公开资料，请遵守相关法律法规使用。
