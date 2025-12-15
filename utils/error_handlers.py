import functools
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def tool_error_handler(func):
    """
    工具函数的错误处理装饰器
    捕获并记录工具调用过程中的异常，返回友好的错误消息
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"工具调用错误 - {func.__name__}: {str(e)}")
            return f"工具调用错误 ({func.__name__}): {str(e)}. 请检查输入参数或稍后重试。"
    return wrapper