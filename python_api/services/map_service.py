import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv
import math
import asyncio
from functools import lru_cache
import hashlib

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class MapService:
    """地图服务类"""
    
    def __init__(self):
        self.amap_key = os.getenv('AMAP_API_KEY')  # 高德地图API密钥
        self.amap_base_url = "https://restapi.amap.com/v3"
        self._last_request_time = 0  # 上次请求时间
        self._min_request_interval = 0.2  # 最小请求间隔（秒）
        self._request_cache = {}  # 请求缓存
        self._cache_ttl = 300  # 缓存有效期（秒）
        
        if not self.amap_key:
            logger.warning("高德地图API密钥未配置，地图功能将使用模拟数据")
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 排除key参数，避免泄露API密钥
        cache_params = {k: v for k, v in params.items() if k != 'key'}
        cache_data = f"{endpoint}:{json.dumps(cache_params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_time: float) -> bool:
        """检查缓存是否有效"""
        return time.time() - cache_time < self._cache_ttl
    
    async def _wait_for_rate_limit(self):
        """等待满足频率限制"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            wait_time = self._min_request_interval - time_since_last
            logger.debug(f"频率控制：等待 {wait_time:.2f} 秒")
            await asyncio.sleep(wait_time)
        
        self._last_request_time = time.time()
    
    def _cleanup_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, (data, cache_time) in self._request_cache.items():
            if current_time - cache_time >= self._cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._request_cache[key]
        
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送HTTP请求到高德地图API"""
        start_time = time.time()
        request_id = f"map_req_{int(time.time() * 1000)}"
        
        # 生成缓存键
        cache_key = self._get_cache_key(endpoint, params)
        
        # 检查缓存
        if cache_key in self._request_cache:
            cached_data, cache_time = self._request_cache[cache_key]
            if self._is_cache_valid(cache_time):
                logger.info(f"[{request_id}] 使用缓存数据: {endpoint}")
                return cached_data
            else:
                # 清理过期缓存
                del self._request_cache[cache_key]
        
        # 频率控制
        await self._wait_for_rate_limit()
        
        # 添加API密钥到参数
        params['key'] = self.amap_key
        params['output'] = 'json'
        
        url = f"{self.amap_base_url}/{endpoint}"
        
        logger.info(f"[{request_id}] 开始调用地图API: {endpoint}")
        logger.debug(f"[{request_id}] 请求参数: {params}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                response_data = response.json()
                
                response_time = time.time() - start_time
                logger.info(f"[{request_id}] 地图API调用成功 - 响应时间: {response_time:.2f}s")
                logger.debug(f"[{request_id}] 响应状态: {response_data.get('status', 'unknown')}")
                
                if response_data.get('status') != '1':
                    error_info = response_data.get('info', 'unknown error')
                    logger.warning(f"[{request_id}] API返回错误: {error_info}")
                    
                    # 对特定错误提供更详细的日志
                    if error_info == 'ENGINE_RESPONSE_DATA_ERROR':
                        logger.warning(f"[{request_id}] 引擎响应数据错误，可能是查询参数不支持或数据不存在")
                    elif error_info == 'INVALID_PARAMS':
                        logger.warning(f"[{request_id}] 参数无效，请检查传入的参数格式和内容")
                    elif error_info == 'CUQPS_HAS_EXCEEDED_THE_LIMIT':
                        logger.warning(f"[{request_id}] API调用频率超限，建议稍后重试")
                        # 频率超限时增加等待时间
                        self._min_request_interval = min(self._min_request_interval * 2, 2.0)
                        logger.info(f"[{request_id}] 调整请求间隔为: {self._min_request_interval:.2f}s")
                else:
                    # 成功时缓存结果
                    self._request_cache[cache_key] = (response_data, time.time())
                    logger.debug(f"[{request_id}] 结果已缓存")
                
                return response_data
                
            except httpx.HTTPStatusError as e:
                response_time = time.time() - start_time
                logger.error(f"[{request_id}] 地图API请求失败 - 状态码: {e.response.status_code}, 响应时间: {response_time:.2f}s")
                logger.error(f"[{request_id}] 错误详情: {e.response.text}")
                raise
            except httpx.RequestError as e:
                response_time = time.time() - start_time
                logger.error(f"[{request_id}] 地图API网络请求错误 - 响应时间: {response_time:.2f}s, 错误: {str(e)}")
                raise
    
    def _normalize_country_to_city(self, address: str) -> str:
        """将国家名称映射为主要城市"""
        country_to_city_mapping = {
            '日本': '东京',
            '韩国': '首尔',
            '泰国': '曼谷',
            '新加坡': '新加坡',
            '马来西亚': '吉隆坡',
            '印度尼西亚': '雅加达',
            '菲律宾': '马尼拉',
            '越南': '河内',
            '柬埔寨': '金边',
            '老挝': '万象',
            '缅甸': '仰光',
            '印度': '新德里',
            '美国': '纽约',
            '英国': '伦敦',
            '法国': '巴黎',
            '德国': '柏林',
            '意大利': '罗马',
            '西班牙': '马德里',
            '俄罗斯': '莫斯科',
            '澳大利亚': '悉尼',
            '加拿大': '多伦多',
            '巴西': '圣保罗',
            '阿根廷': '布宜诺斯艾利斯',
            '埃及': '开罗',
            '南非': '开普敦'
        }
        
        # 检查是否为国家名称
        for country, city in country_to_city_mapping.items():
            if country in address:
                logger.info(f"将国家名称 '{address}' 映射为主要城市 '{city}'")
                return city
        
        return address
    
    async def geocode(self, address: str, city: str = None) -> Optional[Dict[str, Any]]:
        """地理编码：将地址转换为经纬度"""
        if not self.amap_key:
            return self._get_fallback_geocode(address, city)
        
        # 处理国家名称映射
        normalized_address = self._normalize_country_to_city(address)
        
        try:
            params = {
                'address': normalized_address
            }
            if city:
                params['city'] = city
            
            response_data = await self._make_request('geocode/geo', params)
            
            if response_data.get('status') == '1' and response_data.get('geocodes'):
                geocode = response_data['geocodes'][0]
                location = geocode['location'].split(',')
                
                return {
                    'address': geocode.get('formatted_address', normalized_address),
                    'longitude': float(location[0]),
                    'latitude': float(location[1]),
                    'level': geocode.get('level', ''),
                    'province': geocode.get('province', ''),
                    'city': geocode.get('city', ''),
                    'district': geocode.get('district', '')
                }
            else:
                # 如果地理编码失败，尝试使用备用数据或国际城市坐标
                logger.warning(f"地理编码失败: {normalized_address}")
                if normalized_address != address:
                    # 如果是映射后的城市名，尝试使用国际城市坐标
                    fallback_result = self._get_international_city_coords(normalized_address)
                    if fallback_result:
                        return fallback_result
                return self._get_fallback_geocode(address, city)
                
        except Exception as e:
            logger.error(f"地理编码请求失败: {str(e)}")
            return self._get_fallback_geocode(address, city)
    
    async def reverse_geocode(self, longitude: float, latitude: float) -> Optional[Dict[str, Any]]:
        """逆地理编码：将经纬度转换为地址"""
        if not self.amap_key:
            return self._get_fallback_reverse_geocode(longitude, latitude)
        
        try:
            params = {
                'location': f"{longitude},{latitude}"
            }
            
            response_data = await self._make_request('geocode/regeo', params)
            
            if response_data.get('status') == '1' and response_data.get('regeocode'):
                regeocode = response_data['regeocode']
                address_component = regeocode.get('addressComponent', {})
                
                return {
                    'formatted_address': regeocode.get('formatted_address', ''),
                    'province': address_component.get('province', ''),
                    'city': address_component.get('city', ''),
                    'district': address_component.get('district', ''),
                    'township': address_component.get('township', ''),
                    'neighborhood': address_component.get('neighborhood', {}).get('name', ''),
                    'building': address_component.get('building', {}).get('name', '')
                }
            else:
                logger.warning(f"逆地理编码失败: {longitude}, {latitude}")
                return self._get_fallback_reverse_geocode(longitude, latitude)
                
        except Exception as e:
            logger.error(f"逆地理编码请求失败: {str(e)}")
            return self._get_fallback_reverse_geocode(longitude, latitude)
    
    def _validate_and_normalize_keyword(self, keyword: str, city: str = None) -> str:
        """验证和标准化搜索关键词"""
        if not keyword or keyword.strip() == '':
            # 如果关键词为空，使用默认关键词
            default_keywords = ['景点', '旅游', '餐厅', '酒店', '购物']
            if city:
                return f"{city}景点"
            return default_keywords[0]
        
        # 清理关键词
        cleaned_keyword = keyword.strip()
        
        # 如果关键词太短，添加通用后缀
        if len(cleaned_keyword) < 2:
            if city:
                return f"{city}景点"
            return "景点"
        
        return cleaned_keyword
    
    async def search_poi(self, keyword: str, city: str = None, poi_type: str = None, 
                        page_size: int = 20) -> List[Dict[str, Any]]:
        """搜索兴趣点(POI)"""
        if not self.amap_key:
            return self._get_fallback_poi_search(keyword, city)
        
        # 清理过期缓存
        self._cleanup_expired_cache()
        
        # 验证和标准化关键词
        validated_keyword = self._validate_and_normalize_keyword(keyword, city)
        
        if validated_keyword != keyword:
            logger.info(f"关键词已标准化: '{keyword}' -> '{validated_keyword}'")
        
        # 频率超限重试机制
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                params = {
                    'keywords': validated_keyword,
                    'offset': page_size
                }
                if city:
                    params['city'] = city
                if poi_type:
                    params['types'] = poi_type
                
                response_data = await self._make_request('place/text', params)
                
                # 检查是否频率超限
                if response_data.get('info') == 'CUQPS_HAS_EXCEEDED_THE_LIMIT':
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = self._min_request_interval * (2 ** retry_count)
                        logger.warning(f"POI搜索频率超限，第{retry_count}次重试，等待{wait_time:.2f}秒")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"POI搜索频率超限，重试{max_retries}次后仍失败，使用备用数据")
                        return self._get_fallback_poi_search(validated_keyword, city)
                
                break  # 成功或其他错误时跳出循环
                
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"POI搜索请求失败，第{retry_count}次重试: {str(e)}")
                    await asyncio.sleep(1)
                else:
                    logger.error(f"POI搜索请求失败: {str(e)}")
                    return self._get_fallback_poi_search(validated_keyword, city)
        
        try:
            
            if response_data.get('status') == '1' and response_data.get('pois'):
                pois = []
                for poi in response_data['pois']:
                    location = poi.get('location', '').split(',')
                    if len(location) == 2:
                        # 解析坐标信息
                        location_str = poi.get('location', '')
                        coordinates = None
                        if location_str:
                            try:
                                lng, lat = location_str.split(',')
                                coordinates = {'lat': float(lat), 'lng': float(lng)}
                            except (ValueError, IndexError):
                                coordinates = None
                        
                        poi_data = {
                            'name': poi.get('name', ''),
                            'formatted_address': poi.get('address', ''),  # 映射为formatted_address
                            'address': poi.get('address', ''),  # 保留原字段
                            'location': poi.get('location', ''),
                            'coordinates': coordinates,  # 添加结构化坐标
                            'type': poi.get('type', ''),
                            'typecode': poi.get('typecode', ''),
                            'tel': poi.get('tel', ''),
                            'distance': poi.get('distance', ''),
                            'business_area': poi.get('business_area', ''),
                            'citycode': poi.get('citycode', ''),
                            'adcode': poi.get('adcode', '')
                        }
                        pois.append(poi_data)
                
                return pois
            else:
                error_info = response_data.get('info', 'unknown error')
                logger.warning(f"POI搜索失败: {validated_keyword}, 错误: {error_info}")
                
                # 对特定错误提供降级方案
                if error_info in ['INVALID_PARAMS', 'ENGINE_RESPONSE_DATA_ERROR']:
                    logger.info(f"使用备用POI数据: {validated_keyword}")
                    return self._get_fallback_poi_search(validated_keyword, city)
                
                return self._get_fallback_poi_search(validated_keyword, city)
                
        except Exception as e:
            logger.error(f"POI搜索请求失败: {str(e)}")
            return self._get_fallback_poi_search(validated_keyword, city)
    
    async def get_route(self, origin: Tuple[float, float], destination: Tuple[float, float], 
                       strategy: str = '0') -> Optional[Dict[str, Any]]:
        """获取路线规划
        
        Args:
            origin: 起点坐标 (longitude, latitude)
            destination: 终点坐标 (longitude, latitude)
            strategy: 路径策略 ('0': 速度优先, '1': 费用优先, '2': 距离优先, '3': 不走高速)
        """
        if not self.amap_key:
            return self._get_fallback_route(origin, destination)
        
        try:
            params = {
                'origin': f"{origin[0]},{origin[1]}",
                'destination': f"{destination[0]},{destination[1]}",
                'strategy': strategy,
                'extensions': 'all'
            }
            
            response_data = await self._make_request('direction/driving', params)
            
            if response_data.get('status') == '1' and response_data.get('route'):
                route = response_data['route']
                paths = route.get('paths', [])
                
                if paths:
                    path = paths[0]  # 取第一条路径
                    return {
                        'distance': int(path.get('distance', 0)),  # 距离（米）
                        'duration': int(path.get('duration', 0)),  # 时间（秒）
                        'tolls': int(path.get('tolls', 0)),  # 过路费（元）
                        'toll_distance': int(path.get('toll_distance', 0)),  # 收费路段距离（米）
                        'traffic_lights': int(path.get('traffic_lights', 0)),  # 红绿灯个数
                        'steps': self._parse_route_steps(path.get('steps', [])),
                        'formatted_distance': self._format_distance(int(path.get('distance', 0))),
                        'formatted_duration': self._format_duration(int(path.get('duration', 0)))
                    }
                else:
                    logger.warning("路线规划返回空路径")
                    return self._get_fallback_route(origin, destination)
            else:
                logger.warning(f"路线规划失败: {response_data.get('info', 'unknown error')}")
                return self._get_fallback_route(origin, destination)
                
        except Exception as e:
            logger.error(f"路线规划请求失败: {str(e)}")
            return self._get_fallback_route(origin, destination)
    
    async def get_distance_matrix(self, origins: List[Tuple[float, float]], 
                                 destinations: List[Tuple[float, float]]) -> List[List[Dict[str, Any]]]:
        """获取距离矩阵"""
        if not self.amap_key:
            return self._get_fallback_distance_matrix(origins, destinations)
        
        try:
            origins_str = '|'.join([f"{lon},{lat}" for lon, lat in origins])
            destinations_str = '|'.join([f"{lon},{lat}" for lon, lat in destinations])
            
            params = {
                'origins': origins_str,
                'destinations': destinations_str,
                'type': '1'  # 驾车
            }
            
            response_data = await self._make_request('distance', params)
            
            if response_data.get('status') == '1' and response_data.get('results'):
                results = response_data['results']
                matrix = []
                
                for i, result in enumerate(results):
                    row = []
                    for j, dest in enumerate(destinations):
                        if i < len(results):
                            row.append({
                                'distance': int(result.get('distance', 0)),
                                'duration': int(result.get('duration', 0)),
                                'formatted_distance': self._format_distance(int(result.get('distance', 0))),
                                'formatted_duration': self._format_duration(int(result.get('duration', 0)))
                            })
                        else:
                            row.append({'distance': 0, 'duration': 0})
                    matrix.append(row)
                
                return matrix
            else:
                logger.warning("距离矩阵计算失败")
                return self._get_fallback_distance_matrix(origins, destinations)
                
        except Exception as e:
            logger.error(f"距离矩阵请求失败: {str(e)}")
            return self._get_fallback_distance_matrix(origins, destinations)
    
    def _parse_route_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析路线步骤"""
        parsed_steps = []
        for step in steps:
            parsed_steps.append({
                'instruction': step.get('instruction', ''),
                'road': step.get('road', ''),
                'distance': int(step.get('distance', 0)),
                'duration': int(step.get('duration', 0)),
                'action': step.get('action', ''),
                'assistant_action': step.get('assistant_action', '')
            })
        return parsed_steps
    
    def _format_distance(self, distance_meters: int) -> str:
        """格式化距离显示"""
        if distance_meters < 1000:
            return f"{distance_meters}米"
        else:
            km = distance_meters / 1000
            return f"{km:.1f}公里"
    
    def _format_duration(self, duration_seconds: int) -> str:
        """格式化时间显示"""
        if duration_seconds < 60:
            return f"{duration_seconds}秒"
        elif duration_seconds < 3600:
            minutes = duration_seconds // 60
            return f"{minutes}分钟"
        else:
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            if minutes > 0:
                return f"{hours}小时{minutes}分钟"
            else:
                return f"{hours}小时"
    
    def _calculate_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """计算两点间距离（米）"""
        # 使用Haversine公式计算球面距离
        R = 6371000  # 地球半径（米）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _get_international_city_coords(self, city_name: str) -> Optional[Dict[str, Any]]:
        """获取国际主要城市坐标"""
        international_cities = {
            '东京': {'longitude': 139.6917, 'latitude': 35.6895},
            '首尔': {'longitude': 126.9780, 'latitude': 37.5665},
            '曼谷': {'longitude': 100.5018, 'latitude': 13.7563},
            '新加坡': {'longitude': 103.8198, 'latitude': 1.3521},
            '吉隆坡': {'longitude': 101.6869, 'latitude': 3.1390},
            '雅加达': {'longitude': 106.8451, 'latitude': -6.2088},
            '马尼拉': {'longitude': 120.9842, 'latitude': 14.5995},
            '河内': {'longitude': 105.8542, 'latitude': 21.0285},
            '金边': {'longitude': 104.9160, 'latitude': 11.5564},
            '万象': {'longitude': 102.6000, 'latitude': 17.9667},
            '仰光': {'longitude': 96.1951, 'latitude': 16.8661},
            '新德里': {'longitude': 77.1025, 'latitude': 28.7041},
            '纽约': {'longitude': -74.0060, 'latitude': 40.7128},
            '伦敦': {'longitude': -0.1276, 'latitude': 51.5074},
            '巴黎': {'longitude': 2.3522, 'latitude': 48.8566},
            '柏林': {'longitude': 13.4050, 'latitude': 52.5200},
            '罗马': {'longitude': 12.4964, 'latitude': 41.9028},
            '马德里': {'longitude': -3.7038, 'latitude': 40.4168},
            '莫斯科': {'longitude': 37.6173, 'latitude': 55.7558},
            '悉尼': {'longitude': 151.2093, 'latitude': -33.8688},
            '多伦多': {'longitude': -79.3832, 'latitude': 43.6532},
            '圣保罗': {'longitude': -46.6333, 'latitude': -23.5505},
            '布宜诺斯艾利斯': {'longitude': -58.3816, 'latitude': -34.6037},
            '开罗': {'longitude': 31.2357, 'latitude': 30.0444},
            '开普敦': {'longitude': 18.4241, 'latitude': -33.9249}
        }
        
        if city_name in international_cities:
            coords = international_cities[city_name]
            logger.info(f"使用国际城市坐标: {city_name} -> {coords}")
            return {
                'address': city_name,
                'longitude': coords['longitude'],
                'latitude': coords['latitude'],
                'level': '城市',
                'province': '',
                'city': city_name,
                'district': ''
            }
        
        return None
    
    def _get_fallback_geocode(self, address: str, city: str = None) -> Dict[str, Any]:
        """获取备用地理编码数据"""
        # 一些主要地点的坐标
        locations = {
            '天安门': {'longitude': 116.3974, 'latitude': 39.9093},
            '故宫': {'longitude': 116.3972, 'latitude': 39.9180},
            '长城': {'longitude': 116.5704, 'latitude': 40.4319},
            '外滩': {'longitude': 121.4906, 'latitude': 31.2397},
            '东方明珠': {'longitude': 121.5067, 'latitude': 31.2397}
        }
        
        for key, coords in locations.items():
            if key in address:
                return {
                    'address': address,
                    'longitude': coords['longitude'],
                    'latitude': coords['latitude'],
                    'level': '景点',
                    'province': '',
                    'city': city or '',
                    'district': ''
                }
        
        # 默认返回北京坐标
        return {
            'address': address,
            'longitude': 116.4074,
            'latitude': 39.9042,
            'level': '城市',
            'province': '',
            'city': city or '',
            'district': ''
        }
    
    def _get_fallback_reverse_geocode(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """获取备用逆地理编码数据"""
        return {
            'formatted_address': f'经度{longitude}, 纬度{latitude}附近',
            'province': '',
            'city': '',
            'district': '',
            'township': '',
            'neighborhood': '',
            'building': ''
        }
    
    def _get_fallback_poi_search(self, keyword: str, city: str = None) -> List[Dict[str, Any]]:
        """获取备用POI搜索数据"""
        return [
            {
                'id': f'fallback_{keyword}_1',
                'name': f'{keyword}（示例1）',
                'type': '旅游景点',
                'address': f'{city or "北京"}市示例地址1',
                'longitude': 116.4074,
                'latitude': 39.9042,
                'tel': '',
                'distance': '1000',
                'business_area': '',
                'rating': '4.5',
                'cost': ''
            },
            {
                'id': f'fallback_{keyword}_2',
                'name': f'{keyword}（示例2）',
                'type': '旅游景点',
                'address': f'{city or "北京"}市示例地址2',
                'longitude': 116.4174,
                'latitude': 39.9142,
                'tel': '',
                'distance': '2000',
                'business_area': '',
                'rating': '4.3',
                'cost': ''
            }
        ]
    
    def _get_fallback_route(self, origin: Tuple[float, float], 
                           destination: Tuple[float, float]) -> Dict[str, Any]:
        """获取备用路线数据"""
        distance = self._calculate_distance(origin[0], origin[1], destination[0], destination[1])
        duration = int(distance / 10)  # 假设平均速度10m/s
        
        return {
            'distance': int(distance),
            'duration': duration,
            'tolls': 0,
            'toll_distance': 0,
            'traffic_lights': 5,
            'steps': [
                {
                    'instruction': '从起点出发',
                    'road': '起点道路',
                    'distance': int(distance / 2),
                    'duration': duration // 2,
                    'action': '直行',
                    'assistant_action': ''
                },
                {
                    'instruction': '到达终点',
                    'road': '终点道路',
                    'distance': int(distance / 2),
                    'duration': duration // 2,
                    'action': '到达',
                    'assistant_action': ''
                }
            ],
            'formatted_distance': self._format_distance(int(distance)),
            'formatted_duration': self._format_duration(duration)
        }
    
    def _get_fallback_distance_matrix(self, origins: List[Tuple[float, float]], 
                                     destinations: List[Tuple[float, float]]) -> List[List[Dict[str, Any]]]:
        """获取备用距离矩阵数据"""
        matrix = []
        for origin in origins:
            row = []
            for destination in destinations:
                distance = self._calculate_distance(origin[0], origin[1], destination[0], destination[1])
                duration = int(distance / 10)
                row.append({
                    'distance': int(distance),
                    'duration': duration,
                    'formatted_distance': self._format_distance(int(distance)),
                    'formatted_duration': self._format_duration(duration)
                })
            matrix.append(row)
        return matrix

# 创建全局实例
map_service = MapService()