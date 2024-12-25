import os
from dotenv import load_dotenv
import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any, Union

import aiomysql
import logfire
from annotated_types import MinLen
from devtools import debug
from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel




# 配置logfire项目的token，在logfire平台进行跟踪监测
logfire.configure(token="bbpDkqrrYp3N7j6k5t5W4jC6mSys5w2vd3tjLW0cPVy1")


# 从 .env 文件加载环境变量
load_dotenv()


# 初始化OpenAI模型，所需配置从环境变量中读取
llm = OpenAIModel(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("OPENAI_CHAT_MODEL"),
)


# 定义MySQL数据库表students的表格式，包括字段名称、类型和约束
DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,              
    first_name VARCHAR(50) NOT NULL,         
    gender CHAR(100) NOT NULL CHECK (gender IN ('男', '女')), 
    date_of_birth DATE NOT NULL,               
    phone_number VARCHAR(15),                
    address TEXT,                             
    grade_level SMALLINT CHECK (grade_level BETWEEN 1 AND 12), 
    gpa NUMERIC(3, 2) DEFAULT 0.0 CHECK (gpa >= 0 AND gpa <= 4.0), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   
);
"""


# Python 的 dataclasses 模块，通过装饰器 @dataclass 定义了一个数据类 Deps
# conn 是数据类的一个属性 属性类型为 aiomysql.Connection，表示一个异步的MySQL数据库连接对象，来自aiomysql库
@dataclass
class Deps:
    conn: aiomysql.Connection


# 定义了一个名为 Success 的类，继承自 pydantic 的 BaseModel，用于表示成功生成 SQL 查询后的响应数据模型
# 使用 pydantic 定义模型可以自动进行数据验证和序列化，确保输入和输出符合预期格式
class Success(BaseModel):
    # 类型为 str，用于保存生成的 SQL 查询字符串
    # 使用 Annotated 和 MinLen(1) 限制 sql_query 的最小长度为 1，确保 SQL 查询不能为空字符串
    sql_query: Annotated[str, MinLen(1)]
    # 类型为 str，保存对生成的 SQL 查询的解释
    # 默认值为空字符串 ''
    # 使用 Field 设置元数据：description 为字段添加描述，说明 explanation 的用途是以 Markdown 格式提供 SQL 查询的说明
    explanation: str = Field(
        '', description='Explanation of the SQL query, as markdown'
    )


# 定义了一个名为 InvalidRequest 的类，继承自 pydantic 的 BaseModel，用于表示生成失败后的响应数据模型
class InvalidRequest(BaseModel):
    # 类型为 str，用于保存错误消息
    # 表示在生成 SQL 查询失败的情况下，向用户提供的错误描述
    # 没有设置默认值，因此创建 InvalidRequest 实例时必须提供该字段
    error_message: str


# 使用 TypeAlias 创建 Response 类型别名，可以是 Success 或 InvalidRequest
# Union 表示 Response 类型可以是两种类型之一：Success：表示生成 SQL 查询成功的响应,InvalidRequest：表示生成 SQL 查询失败的响应
Response: TypeAlias = Union[Success, InvalidRequest]


# 创建一个Agent，结合 OpenAI 模型和上下文依赖
agent: Agent[Deps, Response] = Agent(
    # 提供了对 OpenAI Chat 模型的访问，用于生成结果
    model=llm,
    # Response 是一个类型别名，允许返回以下两种类型：Success：表示成功生成 SQL 查询的响应、InvalidRequest：表示生成 SQL 查询失败的响应
    result_type=Response,
    # 指定了 Agent 需要的上下文依赖类型为 Deps
    # Deps 是一个数据类，包含一个数据库连接属性 conn，用于在任务处理过程中提供必要的数据库操作能力
    deps_type=Deps,
)


# 定义Agent的上下文说明，包括数据库模式和示例请求
# 通过装饰器 @agent.system_prompt 注册，告诉 Agent 这是用于设置系统提示（System Prompt）的函数
# 动态适配：{DB_SCHEMA} 和 {date.today()} 的使用使提示内容可以动态适应当前数据库架构和日期
@agent.system_prompt
async def system_prompt() -> str:
    return f"""\
给定下面的MySQL数据库students表，你的任务是编写符合用户要求的 SQL 查询。

Database schema:

{DB_SCHEMA}

today's date = {date.today()}

Example
    request: 展示女性学生
    response: SELECT * FROM students WHERE gender = '女'
Example
    request: 查找 GPA 大于 3.8 的学生
    response: SELECT * FROM students WHERE gpa > 3.8
Example
    request: 查找出生日期在 2002 年之后的学生
    response: SELECT * FROM students WHERE date_of_birth > '2002-01-01'
Example
    request: 显示电话包含 138 的学生
    response: SELECT * FROM students WHERE phone_number LIKE '138%'
Example
    request: 查找所有住在北京，且 GPA 大于 3.7 的男生
    response: SELECT * FROM students WHERE address = '北京' AND gender = '男' AND gpa > 3.7  
 Example
    request: 查找所有 11 年级的女生，按 GPA 从高到低排序
    response: SELECT * FROM students WHERE grade_level = 11 AND gender = '女' ORDER BY gpa DESC     
 Example
    request: 查找最近 2 天内新建的学生
    response: SELECT * FROM students WHERE created_at >= NOW() - INTERVAL 2 DAY ORDER BY created_at DESC      
"""


# 定义一个名为 validate_result 的异步函数，用于验证 Agent 返回的结果是否符合预期，并在必要时进行处理或重试
# 通过 @agent.result_validator 装饰器将其注册为 Agent 的结果验证器
# ctx：上下文对象，类型为 RunContext[Deps]，包含依赖（如数据库连接 conn）
# result：Agent 返回的结果，类型为 Response，可以是 Success 或 InvalidRequest
# 返回值：类型为 Response，表示验证后的结果
@agent.result_validator
async def validate_result(ctx: RunContext[Deps], result: Response) -> Response:
    # 如果结果是 InvalidRequest（表示用户请求无效或输入不足），直接返回，不需要进一步验证
    if isinstance(result, InvalidRequest):
        return result

    # 大模型生成的 SQL 查询可能包含多余的反斜杠（\）
    # 通过 replace('\\', '') 去除这些字符，确保生成的 SQL 查询是有效的
    result.sql_query = result.sql_query.replace('\\', '')

    # 检查 SQL 查询是否以 SELECT 开头
    # 验证生成的查询是否是 SELECT 类型，因为此Agent仅处理读取数据的请求
    # 如果不是以 SELECT 开头，抛出 ModelRetry 异常，提示模型重新生成合适的查询
    if not result.sql_query.upper().startswith('SELECT'):
        raise ModelRetry('Please create a SELECT query')

    # 尝试执行 EXPLAIN 语句
    # 使用 MySQL 的 EXPLAIN 语句验证生成的查询语法是否有效
    # EXPLAIN 语句在 MySQL 中用于分析查询的执行计划，它不会实际执行查询，而只是生成查询计划
    # 通过 ctx.deps.conn.cursor() 执行验证，conn 是数据库连接对象，来自 Deps
    try:
        async with ctx.deps.conn.cursor() as cursor:
            await cursor.execute(f'EXPLAIN {result.sql_query}')
    except aiomysql.MySQLError as e:
        raise ModelRetry(f'Invalid query: {e}') from e

    # 如果查询验证成功（EXPLAIN 无错误），返回原始结果对象
    else:
        return result


# 数据库创建：检查数据库是否已存在，如果不存在则创建
# 表结构创建：在事务中确保表结构被创建
# 上下文管理：通过asynccontextmanager确保连接和资源的有效管理
# 定义了一个异步上下文管理器database_connect，用于管理MySQL数据库连接，并确保数据库和表结构的创建
# 返回值：AsyncGenerator[Any, None]，异步生成器类型，提供资源管理，确保连接创建和关闭
@asynccontextmanager
async def database_connect(host: str, user: str, password: str, database: str, table_name: str) -> AsyncGenerator[Any, None]:
    # 日志追踪：logfire.span('check and create DB')，用于在日志系统中创建一个 span，追踪操作
    with logfire.span('check and create DB'):
        conn = await aiomysql.connect(
            host=host, user=user, password=password
        )
        try:
            async with conn.cursor() as cursor:
                # 判断数据库是否存在
                await cursor.execute(f"SHOW DATABASES LIKE '{database}'")
                result = await cursor.fetchone()

                if not result:
                    # 如果数据库不存在，则创建
                    await cursor.execute(f"CREATE DATABASE {database}")

                await cursor.execute(f"USE {database}")

                # 日志追踪：为表结构创建添加 span
                # 事务内操作：
                # 如果数据库未创建，创建一个 log_level 枚举类型
                # 执行 DB_SCHEMA，创建 students 表结构
                with logfire.span('create table'):
                    # 判断表是否存在
                    await cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                    result = await cursor.fetchone()
                    # 如果表不存在，则创建表
                    if not result:
                        await cursor.execute(DB_SCHEMA)
                yield conn
        finally:
            conn.close()


# 主入口，接受用户输入或使用默认用户请求，运行Agent并输出结果
# 负责接受用户输入或使用默认提示，运行Agent来生成 SQL 查询，并输出结果
async def main(host, user, password, database, table_name):
    # 如果未提供额外参数（即 sys.argv 长度为 1），使用默认用户请求
    if len(sys.argv) == 1:
        prompt = '查询男性学生'
    # 如果提供了额外参数，将其作为用户的输入提示 为Agent提供一个用户请求（prompt）
    else:
        prompt = sys.argv[1]

    # 使用 database_connect（定义了异步上下文管理器）建立数据库连接
    # 自动检查并在需要时创建数据库
    # 保证上下文结束时关闭数据库连接，避免资源泄漏
    async with database_connect(
        host=host, user=user, password=password, database=database, table_name=table_name
    ) as conn:
        # 创建 Deps 对象，将数据库连接 conn 传递给Agent
        deps = Deps(conn)
        # 调用 Agent.run 方法，传入：用户输入的请求，包含依赖（数据库连接）的 deps
        result = await agent.run(prompt, deps=deps)
    # 使用 devtools 的 debug 方法输出结果内容
    # 打印调试信息，方便检查生成的 SQL 查询和附加说明
    debug(result.data)


# 异步运行主函数
if __name__ == '__main__':
    host = "139.224.72.218"
    user = "root"
    password = "Aa112233@"
    database = "test02"
    table_name = "students"
    asyncio.run(main(host, user, password, database, table_name))
