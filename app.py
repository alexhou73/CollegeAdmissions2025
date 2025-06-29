from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 读取Excel数据
def load_data():
    df = pd.read_excel('2025.xlsx', sheet_name='普通批')
    # 不再只保留三列，直接返回全部列
    def extract_province(loc):
        if isinstance(loc, str):
            if loc.startswith('内蒙古'):
                return '内蒙古'
            if loc.startswith('黑龙江'):
                return '黑龙江'
            return loc[:2]
        return loc
    df['省份'] = df['位置'].apply(extract_province)
    return df

def get_province_level_stats():
    df = load_data()
    # 统计每省每层次的不同学校数量
    stats = df.groupby(['省份', '层次'])['学校名称'].nunique().reset_index().rename(columns={'学校名称': '数量'})
    # 统计每省不同学校总数
    province_total = df.groupby('省份')['学校名称'].nunique().reset_index().rename(columns={'学校名称': '总数'})
    # 统计层次总数
    level_total = df.groupby('层次')['学校名称'].nunique().reset_index().rename(columns={'学校名称': '总数'})
    # 招生总数：每所大学的第一行且只统计浅蓝色背景（假设为每所学校首次出现）
    first_rows = df.drop_duplicates(subset=['学校名称'], keep='first')
    # 只统计'25\n计划'为数字的行
    plan_col = '25\n计划' if '25\n计划' in df.columns else '25计划'
    first_rows = first_rows[~pd.isna(pd.to_numeric(first_rows[plan_col], errors='coerce'))]
    total_enroll = first_rows[plan_col].astype(float).sum()
    # 总大学数
    total_univ = df['学校名称'].nunique()
    # 985、211、216数量
    count_985 = df[df['层次'] == '985']['学校名称'].nunique()
    count_211 = df[df['层次'] == '211']['学校名称'].nunique()
    count_216 = df[df['层次'] == '216']['学校名称'].nunique()
    # 公办、民办大学数量（需要根据实际数据列来判断）
    # 假设有专门的列来标识公办/民办，如果没有则设为0
    try:
        public_count = df[df['性质'] == '公办']['学校名称'].nunique() if '性质' in df.columns else 0
        private_count = df[df['性质'] == '民办']['学校名称'].nunique() if '性质' in df.columns else 0
    except:
        public_count = 0
        private_count = 0
    # 其它 = 总数-985-211-216-公办-民办
    other_count = total_univ - (count_985 + count_211 + count_216 + public_count + private_count)
    return stats, province_total, level_total, int(total_enroll), public_count, private_count, other_count

def extract_city(loc):
    """
    Extract city name from location string, e.g. '江苏省南京市' -> '南京市', '江苏南京' -> '南京'。
    If not found, return None.
    """
    if isinstance(loc, str):
        # 处理格式：省份+城市，如"江苏南京"、"江苏省南京市"
        # 先尝试匹配"省+市"格式
        for suffix in ['市', '地区', '盟', '自治州', '区', '县']:
            idx = loc.find(suffix)
            if idx > 1:
                # 找到后缀，提取城市名
                city_part = loc[:idx+1]
                # 如果城市名以省份开头，去掉省份部分
                for province in ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', 
                               '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', 
                               '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', 
                               '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']:
                    if city_part.startswith(province):
                        city_part = city_part[len(province):]
                        break
                return city_part if city_part else None
        
        # 如果没有找到后缀，尝试从省份后提取城市名
        for province in ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', 
                       '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', 
                       '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', 
                       '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']:
            if loc.startswith(province):
                city_part = loc[len(province):]
                return city_part if city_part else None
    return None

def normalize_city_name(city):
    if not isinstance(city, str) or city in [None, 'None', 'nan', '']:
        return city
    # 如果已以市/区/县/盟/自治州/地区结尾，保持不变
    for suffix in ['市', '区', '县', '盟', '自治州', '地区']:
        if city.endswith(suffix):
            return city
    # 否则加"市"
    return city + '市'

@app.route('/')
def index():
    print("访问首页路由")
    return render_template('index.html')

@app.route('/api/province_level_stats')
def api_province_level_stats():
    print("访问API路由")
    stats, province_total, level_total, total_enroll, public_count, private_count, other_count = get_province_level_stats()
    print('province_total:', province_total)
    return jsonify({
        'province_level': stats.to_dict(orient='records'),
        'province_total': province_total.to_dict(orient='records'),
        'level_total': level_total.to_dict(orient='records'),
        'total_enroll': total_enroll,
        'public_count': public_count,
        'private_count': private_count,
        'other_count': other_count
    })

@app.route('/api/city_university_stats')
def api_city_university_stats():
    province = request.args.get('province')
    if not province:
        return jsonify({'error': 'Missing province param'}), 400
    try:
        province = province.encode('latin1').decode('utf8')
    except:
        pass
    print(f"Requested province: {province}")
    print(f"Requested province bytes: {province.encode()}")
    df = load_data()
    available_provinces = df['省份'].unique().tolist()
    print(f"Available provinces: {available_provinces}")
    print(f"Available provinces bytes: {[p.encode() for p in available_provinces[:3]]}")
    df = df[df['省份'] == province]
    print(f"Filtered data count: {len(df)}")
    if len(df) == 0:
        return jsonify({
            'city_stats': [],
            'province_count': 0,
            'city_list': [],
            'error': f'No data found for province: {province}',
            'available_provinces': available_provinces,
            'requested_province': province
        })
    df['城市'] = df['位置'].apply(extract_city)
    # 统一加"市"后缀
    df['城市'] = df['城市'].apply(normalize_city_name)
    print(f"Sample locations: {df['位置'].head().tolist()}")
    print(f"Sample cities: {df['城市'].head().tolist()}")
    city_stats = df.groupby('城市')['学校名称'].nunique().reset_index().rename(columns={'学校名称': '数量'})
    province_count = df[df['城市'].isna()]['学校名称'].nunique()
    city_list = [c for c in city_stats['城市'].dropna().unique().tolist() if c not in [None, 'None', 'nan']]
    print(f"City stats: {city_stats.to_dict(orient='records')}")
    print(f"Province count: {province_count}")
    print(f"City list: {city_list}")
    return jsonify({
        'city_stats': city_stats.to_dict(orient='records'),
        'province_count': int(province_count),
        'city_list': city_list,
        'sample_locations': df['位置'].head().tolist(),
        'sample_cities': df['城市'].head().tolist(),
        'total_records': len(df)
    })

@app.route('/api/province_level_distribution')
def api_province_level_distribution():
    """Get level distribution for a specific province"""
    province = request.args.get('province')
    if not province:
        return jsonify({'error': 'Missing province param'}), 400
    try:
        province = province.encode('latin1').decode('utf8')
    except:
        pass
    
    df = load_data()
    df = df[df['省份'] == province]
    
    if len(df) == 0:
        return jsonify({
            'level_stats': [],
            'error': f'No data found for province: {province}'
        })
    
    # Get level distribution for this province
    level_stats = df.groupby('层次')['学校名称'].nunique().reset_index().rename(columns={'学校名称': '数量'})
    
    return jsonify({
        'level_stats': level_stats.to_dict(orient='records'),
        'province': province
    })

@app.route('/api/university_details')
def api_university_details():
    """Get university details with pagination and province filter"""
    province = request.args.get('province')  # Optional province filter
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))  # Changed to 10
    
    df = load_data()
    
    # Apply province filter if provided
    if province:
        try:
            province = province.encode('latin1').decode('utf8')
        except:
            pass
        df = df[df['省份'] == province]
    
    # Get unique universities (first occurrence of each university)
    unique_universities = df.drop_duplicates(subset=['学校名称'], keep='first').copy()
    
    # Add city information for sorting
    unique_universities['城市'] = unique_universities['位置'].apply(extract_city)
    unique_universities['城市'] = unique_universities['城市'].apply(normalize_city_name)
    
    # Sort by city (handle None values)
    unique_universities = unique_universities.sort_values('城市', na_position='last')
    
    # Calculate total count
    total_count = len(unique_universities)
    
    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_data = unique_universities.iloc[start_idx:end_idx]
    
    # Prepare response data
    universities = []
    for _, row in paginated_data.iterrows():
        # Get all records for this university to calculate total enrollment
        univ_records = df[df['学校名称'] == row['学校名称']]
        
        # Calculate total enrollment (sum of 25计划 column)
        plan_col = '25\n计划' if '25\n计划' in df.columns else '25计划'
        total_enrollment = 0
        try:
            total_enrollment = univ_records[plan_col].astype(float).sum()
        except:
            pass
        
        # Get 2025年估分 from '25估分' column
        score_col = '25估分' if '25估分' in df.columns else '估分'
        score_range = ""
        try:
            scores = univ_records[score_col].dropna()
            if len(scores) > 0:
                # Check if it's already a range (contains '-')
                score_values = []
                for score in scores:
                    if isinstance(score, str) and '-' in score:
                        score_values.append(score)
                    else:
                        try:
                            score_values.append(float(score))
                        except:
                            pass
                
                if score_values:
                    # If we have range strings, use them directly
                    range_strings = [s for s in score_values if isinstance(s, str)]
                    if range_strings:
                        score_range = range_strings[0]  # Use first range
                    else:
                        # Calculate range from numeric values
                        numeric_scores = [s for s in score_values if isinstance(s, (int, float))]
                        if numeric_scores:
                            min_score = min(numeric_scores)
                            max_score = max(numeric_scores)
                            if min_score == max_score:
                                score_range = f"{int(min_score)}"
                            else:
                                score_range = f"{int(min_score)}-{int(max_score)}"
        except:
            pass
        
        # Get 专业代码 - collect all unique codes for this university
        major_codes = ""
        try:
            codes = univ_records['专业代码'].dropna()
            if len(codes) > 0:
                # Convert to numeric and collect unique values
                unique_codes = []
                for code in codes:
                    try:
                        # Convert to int to remove decimal points if it's a float
                        numeric_code = int(float(code))
                        if numeric_code not in unique_codes:
                            unique_codes.append(numeric_code)
                    except:
                        # Skip non-numeric values like "专业代码" header
                        continue
                
                if unique_codes:
                    # Sort the codes and join with comma
                    unique_codes.sort()
                    major_codes = ','.join([str(code) for code in unique_codes])
        except:
            pass

        # Get 页码范围 from '页码' column
        page_col = '页码' if '页码' in df.columns else '页码范围'
        page_range = ""
        try:
            pages = univ_records[page_col].dropna()
            if len(pages) > 0:
                # Check if it's already a range (contains '-')
                page_values = []
                for page_val in pages:
                    if isinstance(page_val, str) and '-' in page_val:
                        page_values.append(page_val)
                    else:
                        try:
                            page_values.append(float(page_val))
                        except:
                            pass
                
                if page_values:
                    # If we have range strings, use them directly
                    range_strings = [p for p in page_values if isinstance(p, str)]
                    if range_strings:
                        page_range = range_strings[0]  # Use first range
                    else:
                        # Calculate range from numeric values
                        numeric_pages = [p for p in page_values if isinstance(p, (int, float))]
                        if numeric_pages:
                            min_page = min(numeric_pages)
                            max_page = max(numeric_pages)
                            if min_page == max_page:
                                page_range = f"{int(min_page)}"
                            else:
                                page_range = f"{int(min_page)}-{int(max_page)}"
        except:
            pass
        
        university_info = {
            '学校代码': row.get('学校代码', ''),
            '学校名称': row.get('学校名称', ''),
            '层次': row.get('层次', ''),
            '位置': row.get('位置', ''),
            '专业代码': major_codes,  # Use the collected and deduplicated major codes
            '2025年计划招生总数': int(total_enrollment) if total_enrollment > 0 else 0,
            '2025年估分': score_range,
            '页码范围': page_range
        }
        universities.append(university_info)
    
    return jsonify({
        'universities': universities,
        'total_count': total_count,
        'current_page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'province': province if province else None
    })

@app.route('/test')
def test():
    return "Flask服务正常运行！"

@app.route('/api/province_stat_bar')
def api_province_stat_bar():
    province = request.args.get('province')
    df = load_data()
    if province:
        try:
            province = province.encode('latin1').decode('utf8')
        except:
            pass
        df = df[df['省份'] == province]
    # 统计
    total = df['学校名称'].nunique()
    # 层次字段是数字类型，需要转换为数字进行比较
    df['层次_数字'] = pd.to_numeric(df['层次'], errors='coerce')
    count_985 = df[df['层次_数字'] == 985]['学校名称'].nunique()
    count_211 = df[df['层次_数字'].isin([211, 985])]['学校名称'].nunique()
    count_216 = df[df['层次_数字'].isin([216, 985, 211])]['学校名称'].nunique()
    count_public = df[df['层次'] == '公办']['学校名称'].nunique()
    count_private = df[df['层次'] == '民办']['学校名称'].nunique()
    count_other = df[~df['层次'].isin(['公办','民办']) & ~df['层次_数字'].isin([985, 211, 216])]['学校名称'].nunique()
    # 招生总数：只统计每所大学的第一行
    plan_col = '25\n计划' if '25\n计划' in df.columns else '25计划'
    first_rows = df.drop_duplicates(subset=['学校名称'], keep='first')
    # 修正linter错误：pd.to_numeric返回Series才有notnull
    plan_numeric = pd.to_numeric(first_rows[plan_col], errors='coerce')
    first_rows = first_rows[~plan_numeric.isnull()]
    total_enroll = first_rows[plan_col].astype(float).sum()
    return jsonify({
        'total': int(total),
        '985': int(count_985),
        '211': int(count_211),
        '216': int(count_216),
        'public': int(count_public),
        'private': int(count_private),
        'other': int(count_other),
        'total_enroll': int(total_enroll)
    })

if __name__ == '__main__':
    print("启动Flask应用...")
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True) 