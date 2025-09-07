import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class WeatherService:
    """天气服务类"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geocoding_url = "https://api.openweathermap.org/geo/1.0"
        
        if not self.api_key:
            logger.warning("OpenWeatherMap API密钥未配置，天气功能将使用模拟数据")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送HTTP请求"""
        start_time = time.time()
        request_id = f"weather_req_{int(time.time() * 1000)}"
        
        # 添加API密钥到参数
        params['appid'] = self.api_key
        params['units'] = 'metric'  # 使用摄氏度
        params['lang'] = 'zh_cn'    # 中文描述
        
        logger.info(f"[{request_id}] 开始调用天气API: {url}")
        logger.debug(f"[{request_id}] 请求参数: {params}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                response_data = response.json()
                
                response_time = time.time() - start_time
                logger.info(f"[{request_id}] 天气API调用成功 - 响应时间: {response_time:.2f}s")
                logger.debug(f"[{request_id}] 响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                return response_data
                
            except httpx.HTTPStatusError as e:
                response_time = time.time() - start_time
                logger.error(f"[{request_id}] 天气API请求失败 - 状态码: {e.response.status_code}, 响应时间: {response_time:.2f}s")
                logger.error(f"[{request_id}] 错误详情: {e.response.text}")
                raise
            except httpx.RequestError as e:
                response_time = time.time() - start_time
                logger.error(f"[{request_id}] 天气API网络请求错误 - 响应时间: {response_time:.2f}s, 错误: {str(e)}")
                raise
    
    async def get_coordinates(self, city_name: str) -> Optional[Dict[str, float]]:
        """根据城市名称获取经纬度"""
        if not self.api_key:
            return self._get_fallback_coordinates(city_name)
        
        try:
            url = f"{self.geocoding_url}/direct"
            params = {
                'q': city_name,
                'limit': 1
            }
            
            response_data = await self._make_request(url, params)
            
            if response_data and len(response_data) > 0:
                location = response_data[0]
                return {
                    'lat': location['lat'],
                    'lon': location['lon'],
                    'name': location.get('local_names', {}).get('zh', location['name'])
                }
            else:
                logger.warning(f"未找到城市 {city_name} 的坐标信息")
                return self._get_fallback_coordinates(city_name)
                
        except Exception as e:
            logger.error(f"获取城市坐标失败: {str(e)}")
            return self._get_fallback_coordinates(city_name)
    
    async def get_current_weather(self, city_name: str) -> Dict[str, Any]:
        """获取当前天气"""
        if not self.api_key:
            return self._get_fallback_current_weather(city_name)
        
        try:
            # 先获取坐标
            coordinates = await self.get_coordinates(city_name)
            if not coordinates:
                return self._get_fallback_current_weather(city_name)
            
            url = f"{self.base_url}/weather"
            params = {
                'lat': coordinates['lat'],
                'lon': coordinates['lon']
            }
            
            response_data = await self._make_request(url, params)
            
            return {
                'city': city_name,
                'temperature': round(response_data['main']['temp']),
                'feels_like': round(response_data['main']['feels_like']),
                'humidity': response_data['main']['humidity'],
                'pressure': response_data['main']['pressure'],
                'description': response_data['weather'][0]['description'],
                'icon': response_data['weather'][0]['icon'],
                'wind_speed': response_data.get('wind', {}).get('speed', 0),
                'visibility': response_data.get('visibility', 10000) / 1000,  # 转换为公里
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取当前天气失败: {str(e)}")
            return self._get_fallback_current_weather(city_name)
    
    async def get_forecast(self, city_name: str, days: int = 5) -> List[Dict[str, Any]]:
        """获取天气预报"""
        if not self.api_key:
            return self._get_fallback_forecast(city_name, days)
        
        try:
            # 先获取坐标
            coordinates = await self.get_coordinates(city_name)
            if not coordinates:
                return self._get_fallback_forecast(city_name, days)
            
            url = f"{self.base_url}/forecast"
            params = {
                'lat': coordinates['lat'],
                'lon': coordinates['lon']
            }
            
            response_data = await self._make_request(url, params)
            
            # 处理预报数据，按天分组
            daily_forecasts = {}
            for item in response_data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        'date': date.isoformat(),
                        'temperatures': [],
                        'descriptions': [],
                        'humidity': [],
                        'wind_speed': []
                    }
                
                daily_forecasts[date]['temperatures'].append(item['main']['temp'])
                daily_forecasts[date]['descriptions'].append(item['weather'][0]['description'])
                daily_forecasts[date]['humidity'].append(item['main']['humidity'])
                daily_forecasts[date]['wind_speed'].append(item.get('wind', {}).get('speed', 0))
            
            # 计算每日平均值
            forecast_list = []
            for date, data in list(daily_forecasts.items())[:days]:
                forecast_list.append({
                    'date': data['date'],
                    'max_temp': round(max(data['temperatures'])),
                    'min_temp': round(min(data['temperatures'])),
                    'avg_temp': round(sum(data['temperatures']) / len(data['temperatures'])),
                    'description': max(set(data['descriptions']), key=data['descriptions'].count),
                    'humidity': round(sum(data['humidity']) / len(data['humidity'])),
                    'wind_speed': round(sum(data['wind_speed']) / len(data['wind_speed']), 1)
                })
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"获取天气预报失败: {str(e)}")
            return self._get_fallback_forecast(city_name, days)
    
    async def get_weather_for_travel(self, city_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取旅行期间的天气信息"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
            days = (end - start).days + 1
            
            current_weather = await self.get_current_weather(city_name)
            forecast = await self.get_forecast(city_name, min(days, 5))
            
            # 分析天气趋势
            weather_analysis = self._analyze_weather_for_travel(forecast)
            
            return {
                'city': city_name,
                'travel_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days
                },
                'current_weather': current_weather,
                'forecast': forecast,
                'analysis': weather_analysis,
                'recommendations': self._get_weather_recommendations(forecast)
            }
            
        except Exception as e:
            logger.error(f"获取旅行天气信息失败: {str(e)}")
            return {
                'city': city_name,
                'error': '天气信息获取失败，请稍后重试',
                'recommendations': ['建议关注当地天气预报', '准备适合当季的衣物']
            }
    
    def _analyze_weather_for_travel(self, forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析旅行期间的天气趋势"""
        if not forecast:
            return {'summary': '天气数据不足'}
        
        temps = [day['avg_temp'] for day in forecast]
        descriptions = [day['description'] for day in forecast]
        
        return {
            'summary': f"平均气温 {round(sum(temps) / len(temps))}°C",
            'temp_range': f"{min([day['min_temp'] for day in forecast])}°C - {max([day['max_temp'] for day in forecast])}°C",
            'weather_pattern': max(set(descriptions), key=descriptions.count),
            'rainy_days': len([d for d in descriptions if '雨' in d]),
            'sunny_days': len([d for d in descriptions if '晴' in d or '多云' in d])
        }
    
    def _get_weather_recommendations(self, forecast: List[Dict[str, Any]]) -> List[str]:
        """根据天气预报生成建议"""
        if not forecast:
            return ['建议关注当地天气预报']
        
        recommendations = []
        
        # 温度建议
        temps = [day['avg_temp'] for day in forecast]
        avg_temp = sum(temps) / len(temps)
        
        if avg_temp < 10:
            recommendations.append('气温较低，建议携带厚外套和保暖衣物')
        elif avg_temp > 30:
            recommendations.append('气温较高，建议携带防晒用品和轻薄衣物')
        else:
            recommendations.append('气温适宜，建议携带适中厚度的衣物')
        
        # 降雨建议
        rainy_days = len([d for d in forecast if '雨' in d['description']])
        if rainy_days > 0:
            recommendations.append('预计有降雨，建议携带雨具')
        
        # 风力建议
        high_wind_days = len([d for d in forecast if d['wind_speed'] > 5])
        if high_wind_days > 0:
            recommendations.append('部分时间风力较大，注意保暖和安全')
        
        return recommendations
    
    def _get_fallback_coordinates(self, city_name: str) -> Dict[str, float]:
        """获取备用坐标数据"""
        # 一些主要城市的坐标
        city_coords = {
            '北京': {'lat': 39.9042, 'lon': 116.4074, 'name': '北京'},
            '上海': {'lat': 31.2304, 'lon': 121.4737, 'name': '上海'},
            '广州': {'lat': 23.1291, 'lon': 113.2644, 'name': '广州'},
            '深圳': {'lat': 22.5431, 'lon': 114.0579, 'name': '深圳'},
            '杭州': {'lat': 30.2741, 'lon': 120.1551, 'name': '杭州'},
            '成都': {'lat': 30.5728, 'lon': 104.0668, 'name': '成都'},
            '西安': {'lat': 34.3416, 'lon': 108.9398, 'name': '西安'},
            '南京': {'lat': 32.0603, 'lon': 118.7969, 'name': '南京'}
        }
        
        return city_coords.get(city_name, {'lat': 39.9042, 'lon': 116.4074, 'name': city_name})
    
    def _get_fallback_current_weather(self, city_name: str) -> Dict[str, Any]:
        """获取备用当前天气数据"""
        return {
            'city': city_name,
            'temperature': 22,
            'feels_like': 24,
            'humidity': 65,
            'pressure': 1013,
            'description': '多云',
            'icon': '02d',
            'wind_speed': 3.5,
            'visibility': 10.0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_fallback_forecast(self, city_name: str, days: int) -> List[Dict[str, Any]]:
        """获取备用天气预报数据"""
        forecast = []
        base_date = datetime.now().date()
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            forecast.append({
                'date': date.isoformat(),
                'max_temp': 25 + (i % 3),
                'min_temp': 18 + (i % 2),
                'avg_temp': 22 + (i % 2),
                'description': ['多云', '晴', '小雨'][i % 3],
                'humidity': 60 + (i % 20),
                'wind_speed': 2.5 + (i % 3)
            })
        
        return forecast

# 创建全局实例
weather_service = WeatherService()