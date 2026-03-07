# 常量定义
"""
公共常量定义
"""

# API常量
API_TITLE = "量化数据平台API"
API_VERSION = "0.1.0"
API_DESCRIPTION = "股票数据查询与分析平台"

# 响应消息
MSG_SUCCESS = "操作成功"
MSG_ERROR = "操作失败"
MSG_NOT_FOUND = "资源未找到"
MSG_INVALID_PARAMS = "参数错误"
MSG_SERVER_ERROR = "服务器内部错误"

# 股票市场
MARKET_SH = "sh"
MARKET_SZ = "sz"
MARKET_NAMES = {
    MARKET_SH: "上海证券交易所",
    MARKET_SZ: "深圳证券交易所"
}

# 股票类型
TYPE_STOCK = "stock"
TYPE_INDEX = "index"
TYPE_NAMES = {
    TYPE_STOCK: "股票",
    TYPE_INDEX: "指数"
}

# 数据格式
FORMAT_CSV = "csv"
FORMAT_JSON = "json"
FORMAT_XLSX = "xlsx"

# 缓存键前缀
CACHE_KEY_STOCK_LIST = "stock:list"
CACHE_KEY_STOCK_INFO = "stock:info:"
CACHE_KEY_KLINE = "kline:"
CACHE_KEY_SEARCH = "search:"

# 缓存时间(秒)
CACHE_TTL_SHORT = 60      # 1分钟
CACHE_TTL_MEDIUM = 300    # 5分钟
CACHE_TTL_LONG = 3600     # 1小时

# 请求限制
MAX_SEARCH_RESULTS = 100
MAX_KLINE_DAYS = 365
DEFAULT_KLINE_DAYS = 90
