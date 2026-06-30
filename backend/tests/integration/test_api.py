"""
API 集成测试
"""
import pytest
from app import create_app
from db.models import init_db, Base, engine
import json


@pytest.fixture
def client():
    """测试客户端 Fixture"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            # 重建数据库
            Base.metadata.drop_all(engine)
            init_db()
        
        yield client


class TestAuthAPI:
    """认证 API 测试"""
    
    def test_register(self, client):
        """测试用户注册"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1234',
            'username': 'TestUser'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert data['data']['email'] == 'test@example.com'
    
    def test_register_duplicate_email(self, client):
        """测试重复邮箱注册"""
        # 第一次注册
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        # 第二次注册（重复）
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['code'] == 40009
    
    def test_login(self, client):
        """测试登录"""
        # 先注册
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        # 登录
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert 'token' in data['data']
    
    def test_login_wrong_password(self, client):
        """测试错误密码登录"""
        # 先注册
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        # 错误密码登录
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] == 40001


class TestHealthAPI:
    """健康检查 API 测试"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get('/api/health')
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'services' in data
        assert 'database' in data['services']


class TestIngestAPI:
    """入库 API 测试"""
    
    def get_auth_token(self, client):
        """获取认证 Token"""
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        data = json.loads(response.data)
        return data['data']['token']
    
    def test_ingest_structured(self, client):
        """测试结构化数据入库"""
        token = self.get_auth_token(client)
        
        response = client.post('/api/ingest/structured', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'data': [
                    {
                        'title': '测试新闻',
                        'content': '这是一个测试新闻内容' * 50,  # 足够长
                        'url': 'https://example.com/news/test-1',
                        'source': '测试来源'
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        assert data['data']['total'] == 1

