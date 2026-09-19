class PospalAuthApi:
    """银豹后台登录接口。银豹后台通过 Session Cookie 维持登录态。"""

    SIGN_IN_PATH = "/account/SignIn?noLog="

    def __init__(self, client):
        self.client = client

    def sign_in(self, username, password, return_url="", screen_size="1470*923"):
        return self.client.post(
            self.SIGN_IN_PATH,
            data={
                "userName": username,
                "password": password,
                "returnUrl": return_url,
                "screenSize": screen_size,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        )

    @staticmethod
    def assert_success(response):
        assert response.status_code == 200, (
            f"银豹登录 HTTP 状态异常：{response.status_code}，响应：{response.text}"
        )
        data = response.json()
        assert data.get("successed") is True, f"银豹登录失败：{data}"
        return data
