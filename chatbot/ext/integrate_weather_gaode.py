from dateutil import parser as date_parser
from datetime import date
import forecastio
import time
from geocoder.api import get


gaode_api_key = '38e6b376eac44085a8e72f6ef5e93fb0'
forecast_api_key = "3b1a0ead7333234fe0b428ab4058c4cf"


def get_weather(address, day):
    """
    :param str address: 所需要查询天气的城市
    :param str day: 需要查询天气的日期
    :return:
    """
    # 核查日期
    day = int(time.mktime(date_parser.parse(day).date().timetuple()))
    today = int(time.mktime(date.today().timetuple()))
    if day < today or day >= (today + 8 * 86400):
        return '只能查询8天内的天气情况'

    location = get(address, provider='gaode', method='geocode', key=gaode_api_key)

    # 通过经纬度获取天气信息
    forecast = forecastio.load_forecast(forecast_api_key, location.lat, location.lng)
    all_daily_weather = forecast.daily().data
    daily_weather = None
    for weather in all_daily_weather:
        if weather.d.get('time') == day:
            daily_weather = weather
            break

    if not daily_weather:
        return '无法查询到该日期的天气情况'

    return str({
        '详细地址': location.address,
        '最低温度': round(daily_weather.temperatureMin),
        '最高温度': round(daily_weather.temperatureMax),
        # '总结': daily_weather.summary,
        '降雨概率': '{}%'.format(int(daily_weather.precipProbability * 100)),
        '日期': time.strftime('%Y-%m-%d', time.localtime(daily_weather.d.get('time')))
    })


if __name__ == '__main__':
    for i in range(10000):
        print(get_weather('秦淮河', '20190820'))
        print(get_weather('夫子庙', '20190820'))
        print(get_weather('南京中山陵', '20190820'))
        print(get_weather('玄武湖', '20190820'))
        print(get_weather('台江区', '20190820'))
        print(get_weather('福州', '20190820'))
        print(get_weather('南京', '20190820'))


