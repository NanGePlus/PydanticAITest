import os
from dotenv import load_dotenv
import logfire
from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel




# 配置logfire项目的token，在logfire平台进行跟踪监测
logfire.configure(token="bbpDkqrrYp3N7j6k5t5W4jC6mSys5w2vd3tjLW0cPVy1")
# 不配置logfire，将不会发送任何信息,示例将正常运行
# logfire.configure(send_to_logfire='if-token-present')


# 加载环境变量参数
load_dotenv()


# 设置调用OpenAI Chat模型 生成内容
llm = OpenAIModel(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("OPENAI_CHAT_MODEL"),
)


# 这是一个用于测试的假数据库
class DatabaseConn:
    # 根据客户ID返回名称
    @classmethod
    async def customer_name(cls, *, id: int) -> str | None:
        if id == 123:
            return 'John'

    # 根据客户ID返回余额
    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
        if id == 123:
            return 123.45
        else:
            raise ValueError('Customer not found')


# 定义数据类
# customer_id: 客户ID
# db: 数据库连接
@dataclass
class SupportDependencies:
    customer_id: int
    db: DatabaseConn


# 定义SupportResult数据模型
class SupportResult(BaseModel):
    support_advice: str = Field(description='反馈给客户的建议')
    block_card: bool = Field(description='是否需要冻结客户卡片')
    risk: int = Field(description='查询的风险等级，范围是0-10', ge=0, le=10)


# 定义Agent
# deps_type:使用依赖注入系统为代理的系统提示、工具和结果验证器提供数据和服务
support_agent = Agent(
    llm,
    deps_type=SupportDependencies,
    result_type=SupportResult,
    system_prompt=(
        "你是银行的客服支持人员，请为客户提供支持并判断其询问的风险等级。使用客户姓名回复。"
    )
)


# 动态添加系统提示，通过RunContext访问SupportDependencies中的customer_id和db
# 从数据库获取客户名称，并返回格式化字符串
@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"客户的名字是: {customer_name!r}"


# 定义一个工具函数customer_balance，获取客户余额，并格式化为货币字符串
# 返回客户当前账户余额
@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> str:
    balance = await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )
    return f'${balance:.2f}'




if __name__ == '__main__':
    # 设置依赖项，包含customer_id和DatabaseConn实例
    deps = SupportDependencies(customer_id=123, db=DatabaseConn())

    # 运行Agent 进行测试1
    result = support_agent.run_sync('我的余额是多少?', deps=deps)
    print("result01:",result.data)

    # 运行Agent 进行测试2
    result = support_agent.run_sync('我的银行卡丢了!', deps=deps)
    print("result02:",result.data)