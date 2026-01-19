"""
测试微博用户搜索功能
"""
import requests
import json

def test_weibo_search():
    """测试微博搜索API"""
    print("=" * 60)
    print("测试微博用户搜索API")
    print("=" * 60)
    
    keyword = "新华社"
    print(f"\n搜索关键词: {keyword}")
    
    url = 'https://weibo.com/ajax/side/search'
    params = {'q': keyword}
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://s.weibo.com',
        'referer': 'https://s.weibo.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    try:
        print("\n正在请求API...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nAPI响应成功！")
            print(f"响应数据结构: {list(data.keys())}")
            
            # 尝试解析用户信息
            if 'data' in data:
                search_data = data['data']
                print(f"\ndata字段类型: {type(search_data)}")
                
                if isinstance(search_data, list):
                    print(f"data是列表，长度: {len(search_data)}")
                    if search_data:
                        print(f"第一个元素的键: {list(search_data[0].keys())}")
                elif isinstance(search_data, dict):
                    print(f"data是字典，键: {list(search_data.keys())}")
            
            # 保存完整响应供分析
            with open('weibo_search_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("\n✓ 完整响应已保存到 weibo_search_response.json")
            
            return True
        else:
            print(f"\n✗ 请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n✗ 请求异常: {e}")
        return False

if __name__ == '__main__':
    test_weibo_search()
    
    print("\n" + "=" * 60)
    print("提示:")
    print("  - 如果请求成功，请查看 weibo_search_response.json")
    print("  - 分析响应数据结构以优化解析逻辑")
    print("=" * 60)
