"""集成测试包（任务 25）。

本目录下的测试以 pytest 标记 ``integration`` 区分，与单元测试隔离：

    pytest backend/tests/integration -m integration

每个测试模块通常需要：
- 端到端串联多个服务（API → Service → 客户端层）
- 仅在最外层（HTTP / 数据库 / 检索后端）打桩，业务逻辑走真实代码

具体共享 fixture 见 ``conftest.py``。
"""
