# 1、介绍
## 1.1 主要内容                      
PydanticAI开源框架介绍及使用PydanticAI实现Text2SQL生成SQL语句应用                                                                        
本次应用案例实现功能为:在线客服支持、基于PostgreSQL数据库的Text2SQL生成SQL语句，基于MySQL数据库的Text2SQL生成SQL语句                                       

## 1.2 PydanticAI框架
PydanticAI是基于Pydantic构建的一个扩展框架，专注于增强AI模型的易用性，提供模型验证和数据验证功能                  
Pydantic是一个用于数据验证和设置的Python库，其核心功能是通过Python的类型注解、实现高效的数据验证和解析。它以简单、直观的方式定义数据模型，广泛用于构建API、处理配置和验证复杂数据结构                           
官方网址:https://ai.pydantic.dev/                                                                                          
Github地址:https://github.com/pydantic/pydantic-ai                                                          
**官方推荐理由，为什么使用PydanticAI**                              
(1)由Pydantic团队打造                              
(2)支持OpenAI、Anthropic、Gemini、Ollama、Groq 和 Mistral，并有一个简单的接口来实现对其他模型的支持                                          
(3)提供类型检查确保类型安全                                  
(4)以python为中心的设计，利用Python熟悉的控制流和Agent来构建人工智能驱动的项目                  
(5)结构化响应输出，利用 Pydantic 的强大功能来验证和构建模型输出，确保各次运行的响应是一致的                     
(6)提供可选的依赖注入系统，为Agent的系统提示、工具和结果验证器提供数据和服务。这对于测试和评估驱动的迭代开发非常有用                                    
(7)提供连续流式LLM输出的能力，可立即进行验证，确保快速、准确地得出结果                                      
**核心功能**                   
**Agents:** Agent是PydanticAI与LLM交互的主要接口，具体相关属性可查看官网文档介绍                      
**Models:** PydanticAI与模型无关，内置了对以下模型提供商的支持:OpenAI、Anthropic、Gemini、Ollama、Groq 和 Mistral等                         
**Dependencies:** 提供可选的依赖注入系统，为Agent的系统提示、工具和结果验证器提供数据和服务                   
**Function Tools:** 提供给LLM可调用的外部工具                               
**Results:** 结果是运行Agent时返回的最终值。结果值封装在RunResult和StreamedRunResult中                                              
**Logfire:** 一个可观察性平台，由创建和维护 Pydantic 和 PydanticAI 的团队开发，https://pydantic.dev/               


# 2、前期准备工作
## 2.1 开发环境搭建:anaconda、pycharm
anaconda:提供python虚拟环境，官网下载对应系统版本的安装包安装即可                                      
pycharm:提供集成开发环境，官网下载社区版本安装包安装即可                                               
**可参考如下视频:**                      
集成开发环境搭建Anaconda+PyCharm                                                          
https://www.bilibili.com/video/BV1q9HxeEEtT/?vd_source=30acb5331e4f5739ebbad50f7cc6b949                             
https://youtu.be/myVgyitFzrA          

## 2.2 大模型相关配置
(1)GPT大模型使用方案(第三方代理方式)                               
(2)非GPT大模型(阿里通义千问、讯飞星火、智谱等大模型)使用方案(OneAPI方式)                         
(3)本地开源大模型使用方案(Ollama方式)                                             
**可参考如下视频:**                                   
提供一种LLM集成解决方案，一份代码支持快速同时支持gpt大模型、国产大模型(通义千问、文心一言、百度千帆、讯飞星火等)、本地开源大模型(Ollama)                       
https://www.bilibili.com/video/BV12PCmYZEDt/?vd_source=30acb5331e4f5739ebbad50f7cc6b949                 
https://youtu.be/CgZsdK43tcY           


# 3、项目初始化
## 3.1 下载源码
GitHub或Gitee中下载工程文件到本地，下载地址如下：                
https://github.com/NanGePlus/PydanticAITest                                                               
https://gitee.com/NanGePlus/PydanticAITest                                     

## 3.2 构建项目
使用pycharm构建一个项目，为项目配置虚拟python环境                       
项目名称：PydanticAITest                          
虚拟环境名称保持与项目名称一致                                       

## 3.3 将相关代码拷贝到项目工程中           
将下载的代码文件夹中的文件全部拷贝到新建的项目根目录下                             

## 3.4 安装项目依赖                            
新建命令行终端，在终端中运行 pip install -r requirements.txt 安装依赖                                                      
**注意:** 建议先使用要求的对应版本进行本项目测试，避免因版本升级造成的代码不兼容。测试通过后，可进行升级测试                                                                           


# 4、功能测试 
### (1)测试脚本                                                          
这里为大家演示3个测试用例，在根目录下                              
basic_support.py:实现在线客服支持                      
postgresql_gen_execute.py:实现基于PostgreSQL数据库的Text2SQL，生成SQL语句                     
mysql_gen_execute.py:实现基于MySQL数据库的Text2SQL，生成SQL语句                                 
### (2)大模型准备                                    
**gpt大模型(使用代理方案):**                            
OPENAI_BASE_URL=https://yunwu.ai/v1                         
OPENAI_API_KEY=sk-jbwlXGjutkupIpiN7A7tlstXiifAuKrYag9iSVGdv4THnDvi                          
OPENAI_CHAT_MODEL=gpt-4o-mini                                              
**非gpt大模型(使用OneAPI方案):**                                   
OPENAI_BASE_URL=http://139.224.72.218:3000/v1                              
OPENAI_API_KEY=sk-Rg0ETo4QXdunA5ET926e31De120b4905Bf8f9fCc4945E3Fb                                       
OPENAI_CHAT_MODEL=qwen-plus                               
### (3)logfire项目创建                                               
打开如下链接地址进行注册和登录，登录成功后进行项目创建并生成token                         
https://logfire.pydantic.dev/nangeplus/-/projects                  
### (4-1)测试basic_support.py              
打开命令行终端，进入脚本所在目录，运行 python basic_support.py 命令                                
### (4-2)测试postgresql_gen_execute.py                  
首先，使用docker部署和启动PostgreSQL数据库，运行的指令为:      
docker run --rm -e POSTGRES_PASSWORD=postgres -p 54320:5432 postgres                            
对于docker的使用，这里不做详细的赘述了，大家可以去看我这期视频，里面有对于docker非常详细的讲解，从安装部署到使用                      
https://www.bilibili.com/video/BV1LhUAYFEku/?vd_source=30acb5331e4f5739ebbad50f7cc6b949                           
https://youtu.be/hD09V7jaXSo                       
打开命令行终端，进入脚本所在目录，运行 python postgresql_gen_execute.py 命令  
然后，打开数据库客户端软件对生成的SQL语句进行测试，在运行脚本之前，可以写一些假数据进行测试，运行如下SQL脚本                                            
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                       
    VALUES ('张三丰', '男', '2001-06-15', '13861456189', '武当山', 12, 3.75);                        
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                       
    VALUES ('李白', '男', '2002-09-23', '13865432187', '长安', 11, 3.8);                       
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                 
    VALUES ('王小明', '男', '2000-12-01', '13867923456', '北京', 12, 3.9);                          
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)            
    VALUES ('张晓华', '女', '2003-07-19', '13868901234', '上海', 9, 3.6);                      
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)              
    VALUES ('王小丽', '女', '2002-02-05', '13869876543', '深圳', 11, 3.7);                      
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)               
    VALUES ('赵明哲', '男', '2001-03-18', '13861324567', '广州', 12, 3.9);                   
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                 
    VALUES ('陈静', '女', '2000-11-20', '13863457892', '杭州', 9, 3.8);                  
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)              
    VALUES ('李娜', '女', '2003-08-30', '13865678901', '杭州', 9, 3.7);                    
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                  
    VALUES ('张伟', '男', '2001-05-27', '13868902345', '天津', 12, 3.85);                         
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                      
    VALUES ('刘芳', '女', '2002-04-14', '13869786543', '武汉', 11, 3.9);                    
最后，打开命令行终端，进入脚本所在目录，运行脚本进行测试                  
python postgresql_gen_execute.py "查找所有9年级的女生"                          
python postgresql_gen_execute.py "查找所有9年级的女生，家住在杭州，按GPA分数从小到大排序"                         
python postgresql_gen_execute.py "查找9到11年级的学生，按GPA分数从大到小排序"                          
python postgresql_gen_execute.py "查找出生日期在2001年4月以后的学生，按GPA分数从大到小排序"                          
### (4-3)测试mysql_gen_execute.py                         
首先，这里可以使用docker部署和启动MySQL数据库，也可以使用自己远程部署的数据库，这里我以阿里云部署的数据库为例                     
打开命令行终端，进入脚本所在目录，运行 python mysql_gen_execute.py 命令                  
然后，打开数据库客户端软件对生成的SQL语句进行测试，在运行脚本之前，可以写一些假数据进行测试，运行如下SQL脚本                                             
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                        
    VALUES ('张三丰', '男', '2001-06-15', '13861456189', '武当山', 12, 3.75);                        
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                       
    VALUES ('李白', '男', '2002-09-23', '13865432187', '长安', 11, 3.8);                       
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                 
    VALUES ('王小明', '男', '2000-12-01', '13867923456', '北京', 12, 3.9);                          
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)            
    VALUES ('张晓华', '女', '2003-07-19', '13868901234', '上海', 9, 3.6);                      
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)              
    VALUES ('王小丽', '女', '2002-02-05', '13869876543', '深圳', 11, 3.7);                      
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)               
    VALUES ('赵明哲', '男', '2001-03-18', '13861324567', '广州', 12, 3.9);                   
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                 
    VALUES ('陈静', '女', '2000-11-20', '13863457892', '杭州', 9, 3.8);                  
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)              
    VALUES ('李娜', '女', '2003-08-30', '13865678901', '杭州', 9, 3.7);                    
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                  
    VALUES ('张伟', '男', '2001-05-27', '13868902345', '天津', 12, 3.85);                         
INSERT INTO students (first_name, gender, date_of_birth, phone_number, address, grade_level, gpa)                      
    VALUES ('刘芳', '女', '2002-04-14', '13869786543', '武汉', 11, 3.9);                    
最后，打开命令行终端，进入脚本所在目录，运行脚本进行测试                  
python mysql_gen_execute.py "查找所有9年级的女生"                          
python mysql_gen_execute.py "查找所有9年级的女生，家住在杭州，按GPA分数从小到大排序"                         
python mysql_gen_execute.py "查找9到11年级的学生，按GPA分数从大到小排序"                          
python mysql_gen_execute.py "查找出生日期在2001年4月以后的学生，按GPA分数从大到小排序"                      












