import React from 'react';
import { Cloud, Sun, CloudRain, CloudSnow, Wind, Thermometer, Droplets } from 'lucide-react';

interface WeatherData {
  current?: {
    temperature?: number;
    description?: string;
    humidity?: number;
    wind_speed?: number;
  };
  forecast?: Array<{
    date: string;
    temp_max?: number;
    temp_min?: number;
    description?: string;
    weather?: string;
  }>;
  analysis?: {
    summary?: string;
  };
  recommendations?: string[];
}

interface WeatherInfoProps {
  weatherData?: WeatherData;
  className?: string;
}

interface DayWeatherProps {
  date: string;
  weatherData?: WeatherData;
  className?: string;
}

// 获取天气图标
const getWeatherIcon = (description: string) => {
  const desc = description.toLowerCase();
  if (desc.includes('晴') || desc.includes('sunny') || desc.includes('clear')) {
    return <Sun className="w-4 h-4 text-yellow-500" />;
  } else if (desc.includes('雨') || desc.includes('rain')) {
    return <CloudRain className="w-4 h-4 text-blue-500" />;
  } else if (desc.includes('雪') || desc.includes('snow')) {
    return <CloudSnow className="w-4 h-4 text-gray-400" />;
  } else if (desc.includes('云') || desc.includes('cloud')) {
    return <Cloud className="w-4 h-4 text-gray-500" />;
  } else {
    return <Sun className="w-4 h-4 text-yellow-500" />;
  }
};

// 整体天气概览卡片
export const WeatherOverview: React.FC<WeatherInfoProps> = ({ weatherData, className = '' }) => {
  if (!weatherData) {
    return (
      <div className={`bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-4 border border-blue-100 ${className}`}>
        <div className="flex items-center space-x-2 mb-2">
          <Cloud className="w-5 h-5 text-gray-400" />
          <span className="font-semibold text-gray-600">天气信息</span>
        </div>
        <p className="text-sm text-gray-500">暂无天气数据</p>
      </div>
    );
  }

  const { current, analysis, recommendations } = weatherData;

  return (
    <div className={`bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-4 border border-blue-100 ${className}`}>
      <div className="flex items-center space-x-2 mb-3">
        <Thermometer className="w-5 h-5 text-blue-600" />
        <span className="font-semibold text-gray-800">天气概览</span>
      </div>
      
      {current && (
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            {getWeatherIcon(current.description || '')}
            <span className="text-sm text-gray-700">{current.description || '晴朗'}</span>
          </div>
          <div className="text-right">
            {current.temperature && (
              <div className="text-lg font-bold text-gray-800">{Math.round(current.temperature)}°C</div>
            )}
            <div className="flex items-center space-x-3 text-xs text-gray-600">
              {current.humidity && (
                <div className="flex items-center space-x-1">
                  <Droplets className="w-3 h-3" />
                  <span>{current.humidity}%</span>
                </div>
              )}
              {current.wind_speed && (
                <div className="flex items-center space-x-1">
                  <Wind className="w-3 h-3" />
                  <span>{current.wind_speed}m/s</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {analysis?.summary && (
        <div className="text-sm text-gray-700 mb-2">
          <span className="font-medium">趋势：</span>{analysis.summary}
        </div>
      )}
      
      {recommendations && recommendations.length > 0 && (
        <div className="text-xs text-gray-600">
          <span className="font-medium">建议：</span>
          {recommendations.slice(0, 2).join('，')}
        </div>
      )}
    </div>
  );
};

// 单日天气信息组件
export const DayWeather: React.FC<DayWeatherProps> = ({ date, weatherData, className = '' }) => {
  if (!weatherData?.forecast) {
    return (
      <div className={`flex items-center space-x-1 text-gray-400 ${className}`}>
        <Cloud className="w-3 h-3" />
        <span className="text-xs">无天气数据</span>
      </div>
    );
  }

  // 查找对应日期的天气数据
  const dayWeather = weatherData.forecast.find(f => f.date === date);
  
  if (!dayWeather) {
    return (
      <div className={`flex items-center space-x-1 text-gray-400 ${className}`}>
        <Cloud className="w-3 h-3" />
        <span className="text-xs">无天气数据</span>
      </div>
    );
  }

  const description = dayWeather.weather || dayWeather.description || '晴朗';
  const tempMax = dayWeather.temp_max;
  const tempMin = dayWeather.temp_min;

  return (
    <div className={`flex items-center space-x-2 bg-white/60 backdrop-blur-sm rounded-lg px-2 py-1 border border-white/30 ${className}`}>
      {getWeatherIcon(description)}
      <div className="text-xs">
        <div className="font-medium text-gray-700">{description}</div>
        {(tempMax || tempMin) && (
          <div className="text-gray-600">
            {tempMin && tempMax ? `${Math.round(tempMin)}°-${Math.round(tempMax)}°C` : 
             tempMax ? `${Math.round(tempMax)}°C` : 
             tempMin ? `${Math.round(tempMin)}°C` : ''}
          </div>
        )}
      </div>
    </div>
  );
};

export default { WeatherOverview, DayWeather };