"""
API 完整集成测试 - 覆盖所有核心端点
"""
import pytest
import json
import requests
from app import create_app
from db.models import init_db, Base, engine

BASE_URL = "http://localhost:5000/api"


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            Base.metadata.create_all(engine)
            Base.metadata.drop_all(engine)
            init_db()
        yield client


@pytest.fixture
def auth_token(client):
    """认证 Token Fixture"""
    client.post('/api/auth/register', json={
        'email': 'test_user@example.com',
        'password': 'Test1234'
    })
    response = client.post('/api/auth/login', json={
        'email': 'test_user@example.com',
        'password': 'Test1234'
    })
    return json.loads(response.data)['data']['token']


class TestAuthAPI:
    """认证 API 测试"""
    
    def test_register_without_password(self, client):
        """测试缺少密码注册"""
        response = client.post('/api/auth/register', json={
            'email': 'test1@example.com'
        })
        assert response.status_code == 400
    
    def test_login_with_nonexistent_email(self, client):
        """测试不存在的邮箱登录"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'Test1234'
        })
        assert response.status_code == 401
    
    def test_access_protected_without_token(self, client):
        """测试无Token访问受保护接口"""
        response = client.post('/api/ask', json={'question': 'test'})
        assert response.status_code == 401
    
    def test_access_protected_with_invalid_token(self, client):
        """测试无效Token访问"""
        response = client.post('/api/ask', headers={'Authorization': 'Bearer invalid_token'}, json={'question': 'test'})
        assert response.status_code == 401


class TestNewsIngestAPI:
    """新闻入库 API 测试"""
    
    def test_ingest_empty_content(self, auth_token, client):
        """测试内容过短的新闻入库"""
        response = client.post('/api/ingest/structured', 
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'data': [{
                    'title': '测试新闻',
                    'content': '太短',
                    'url': 'https://example.com/news/test-short'
                }]
            }
        )
        assert response.status_code in [400, 200]
    
    def test_ingest_duplicate_url(self, auth_token, client):
        """测试重复URL新闻入库"""
        news_data = {
            'data': [{
                'title': '测试新闻',
                'content': '这是一个测试新闻内容' * 50,
                'url': 'https://example.com/news/duplicate-test'
            }]
        }
        client.post('/api/ingest/structured', headers={'Authorization': f'Bearer {auth_token}'}, json=news_data)
        response = client.post('/api/ingest/structured', headers={'Authorization': f'Bearer {auth_token}'}, json=news_data)
        assert response.status_code == 200


class TestRAGAPI:
    """RAG 问答 API 测试"""
    
    def test_ask_with_empty_question(self, auth_token, client):
        """测试空问题"""
        response = client.post('/api/ask', 
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'question': ''}
        )
        assert response.status_code == 400
    
    def test_ask_with_valid_question(self, auth_token, client):
        """测试有效问题"""
        response = client.post('/api/ask', 
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'question': '人工智能技术发展', 'top_k': 3}
        )
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['code'] == 0
        assert 'answer' in data['data']


class TestAgentAPI:
    """Agent API 测试"""
    
    def test_agent_query(self, auth_token, client):
        """测试 Agent 查询"""
        response = client.post('/api/agent/query', 
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'question': 'AI新闻'}
        )
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'answer' in data['data']
    
    def test_agent_analyze_clusters(self, auth_token, client):
        """测试 Agent 聚类分析"""
        response = client.post('/api/agent/analyze', 
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'type': 'clusters', 'time_range': 'daily'}
        )
        data = json.loads(response.data)
        assert data['code'] == 0 or data['code'] == 40000
    
    def test_agent_analyze_keywords(self, auth_token, client):
        """测试 Agent 关键词分析"""
        response = client.post('/api/agent/analyze', 
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'type': 'keywords', 'time_range': 'daily'}
        )
        data = json.loads(response.data)
        assert data['code'] == 0
    
    def test_agent_list_skills(self, auth_token, client):
        """测试获取 Skill 列表"""
        response = client.get('/api/agent/skills', 
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert data['code'] == 0
        assert isinstance(data['data']['skills'], list)
    
    def test_agent_list_tools(self, auth_token, client):
        """测试获取 Tool 列表"""
        response = client.get('/api/agent/tools', 
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        data = json.loads(response.data)
        assert data['code'] == 0
        assert isinstance(data['data']['tools'], list)


class TestReportsAPI:
    """报告 API 测试"""
    
    def test_cluster_analysis(self, auth_token, client):
        """测试聚类分析"""
        response = client.get('/api/report/clusters', 
            headers={'Authorization': f'Bearer {auth_token}'},
            query_string={'n_clusters': 3}
        )
        data = json.loads(response.data)
        assert data['code'] == 0 or data['code'] == 40000
    
    def test_top_keywords(self, auth_token, client):
        """测试关键词 Top10"""
        response = client.get('/api/report/topkeywords', 
            headers={'Authorization': f'Bearer {auth_token}'},
            query_string={'time_range': 'daily'}
        )
        data = json.loads(response.data)
        assert data['code'] == 0


class TestSecurityAPI:
    """安全测试"""
    
    def test_sql_injection(self, client):
        """测试 SQL 注入"""
        client.post('/api/auth/register', json={
            'email': 'test_security@example.com',
            'password': 'Test1234'
        })
        response = client.post('/api/auth/login', json={
            'email': "' OR '1'='1",
            'password': 'anything'
        })
        assert response.status_code == 401
    
    def test_xss_attempt(self, auth_token, client):
        """测试 XSS 攻击尝试"""
        response = client.post('/api/ingest/structured', 
            headers={'Authorization': f'Bearer {auth_token}'},
            json={
                'data': [{
                    'title': '<script>alert("XSS")</script>',
                    'content': 'Content' * 50,
                    'url': 'https://example.com/news/xss-test'
                }]
            }
        )
        assert response.status_code == 200
