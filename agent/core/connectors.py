"""
🔌 Conectores de Datos Externos del Agente Inteligente

Este módulo proporciona conectores para diferentes APIs y fuentes de datos
que el agente puede utilizar para obtener información actualizada.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

from .config import get_config


class DataSource(str, Enum):
    """Tipos de fuentes de datos"""
    WEATHER = "weather"
    NEWS = "news"
    FINANCE = "finance"
    SEARCH = "search"
    TRANSLATION = "translation"
    CALENDAR = "calendar"
    EMAIL = "email"


@dataclass
class DataRequest:
    """Solicitud de datos"""
    source: DataSource
    query: str
    parameters: Optional[Dict[str, Any]] = None
    timeout: int = 30


@dataclass
class DataResponse:
    """Respuesta de datos"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseConnector:
    """Conector base para APIs"""
    
    def __init__(self, config):
        self.config = config
        self.session = None
        self.base_url = ""
        self.api_key = ""
        self.timeout = 30
    
    async def initialize(self):
        """Inicializar el conector"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Cerrar el conector"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, url: str, method: str = "GET", 
                          params: Optional[Dict] = None, 
                          headers: Optional[Dict] = None,
                          data: Optional[Dict] = None) -> Dict[str, Any]:
        """Realizar petición HTTP"""
        try:
            async with self.session.request(
                method, url, params=params, headers=headers, json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}: {response.reason}"}
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}


class WeatherConnector(BaseConnector):
    """Conector para APIs de clima"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.weather_api_key or config.openweather_api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_current_weather(self, city: str, country_code: str = "") -> DataResponse:
        """Obtener clima actual"""
        try:
            await self.initialize()
            
            location = f"{city},{country_code}" if country_code else city
            url = f"{self.base_url}/weather"
            
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "lang": "es"
            }
            
            result = await self._make_request(url, params=params)
            
            if "error" in result:
                return DataResponse(
                    success=False,
                    error=result["error"],
                    source="OpenWeatherMap"
                )
            
            # Procesar respuesta
            weather_data = {
                "city": result.get("name", city),
                "country": result.get("sys", {}).get("country", ""),
                "temperature": result.get("main", {}).get("temp"),
                "feels_like": result.get("main", {}).get("feels_like"),
                "humidity": result.get("main", {}).get("humidity"),
                "pressure": result.get("main", {}).get("pressure"),
                "description": result.get("weather", [{}])[0].get("description", ""),
                "icon": result.get("weather", [{}])[0].get("icon", ""),
                "wind_speed": result.get("wind", {}).get("speed"),
                "wind_direction": result.get("wind", {}).get("deg"),
                "visibility": result.get("visibility"),
                "sunrise": result.get("sys", {}).get("sunrise"),
                "sunset": result.get("sys", {}).get("sunset"),
                "timestamp": datetime.now().isoformat()
            }
            
            return DataResponse(
                success=True,
                data=weather_data,
                source="OpenWeatherMap",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error obteniendo clima: {str(e)}",
                source="OpenWeatherMap"
            )
    
    async def get_forecast(self, city: str, days: int = 5) -> DataResponse:
        """Obtener pronóstico del clima"""
        try:
            await self.initialize()
            
            url = f"{self.base_url}/forecast"
            
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "es",
                "cnt": days * 8  # 8 mediciones por día
            }
            
            result = await self._make_request(url, params=params)
            
            if "error" in result:
                return DataResponse(
                    success=False,
                    error=result["error"],
                    source="OpenWeatherMap"
                )
            
            # Procesar pronóstico
            forecast_data = {
                "city": result.get("city", {}).get("name", city),
                "forecasts": []
            }
            
            for item in result.get("list", []):
                forecast = {
                    "datetime": item.get("dt_txt"),
                    "temperature": item.get("main", {}).get("temp"),
                    "feels_like": item.get("main", {}).get("feels_like"),
                    "humidity": item.get("main", {}).get("humidity"),
                    "description": item.get("weather", [{}])[0].get("description", ""),
                    "icon": item.get("weather", [{}])[0].get("icon", ""),
                    "wind_speed": item.get("wind", {}).get("speed"),
                    "precipitation": item.get("pop", 0)  # Probabilidad de precipitación
                }
                forecast_data["forecasts"].append(forecast)
            
            return DataResponse(
                success=True,
                data=forecast_data,
                source="OpenWeatherMap",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error obteniendo pronóstico: {str(e)}",
                source="OpenWeatherMap"
            )


class NewsConnector(BaseConnector):
    """Conector para APIs de noticias"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.news_api_key or config.gnews_api_key
        self.base_url = "https://newsapi.org/v2"
    
    async def get_news(self, query: str, language: str = "es", 
                      sort_by: str = "publishedAt", page_size: int = 10) -> DataResponse:
        """Obtener noticias"""
        try:
            await self.initialize()
            
            url = f"{self.base_url}/everything"
            
            params = {
                "q": query,
                "apiKey": self.api_key,
                "language": language,
                "sortBy": sort_by,
                "pageSize": page_size
            }
            
            result = await self._make_request(url, params=params)
            
            if "error" in result:
                return DataResponse(
                    success=False,
                    error=result["error"],
                    source="NewsAPI"
                )
            
            # Procesar noticias
            news_data = {
                "total_results": result.get("totalResults", 0),
                "articles": []
            }
            
            for article in result.get("articles", []):
                news_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "author": article.get("author", ""),
                    "published_at": article.get("publishedAt", ""),
                    "relevance_score": 0.0  # Se puede calcular basado en la consulta
                }
                news_data["articles"].append(news_article)
            
            return DataResponse(
                success=True,
                data=news_data,
                source="NewsAPI",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error obteniendo noticias: {str(e)}",
                source="NewsAPI"
            )
    
    async def get_top_headlines(self, country: str = "es", category: str = "general") -> DataResponse:
        """Obtener titulares principales"""
        try:
            await self.initialize()
            
            url = f"{self.base_url}/top-headlines"
            
            params = {
                "country": country,
                "category": category,
                "apiKey": self.api_key,
                "pageSize": 20
            }
            
            result = await self._make_request(url, params=params)
            
            if "error" in result:
                return DataResponse(
                    success=False,
                    error=result["error"],
                    source="NewsAPI"
                )
            
            # Procesar titulares
            headlines_data = {
                "country": country,
                "category": category,
                "total_results": result.get("totalResults", 0),
                "articles": []
            }
            
            for article in result.get("articles", []):
                headline = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "published_at": article.get("publishedAt", "")
                }
                headlines_data["articles"].append(headline)
            
            return DataResponse(
                success=True,
                data=headlines_data,
                source="NewsAPI",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error obteniendo titulares: {str(e)}",
                source="NewsAPI"
            )


class FinanceConnector(BaseConnector):
    """Conector para APIs financieras"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_stock_price(self, symbol: str) -> DataResponse:
        """Obtener precio de acción"""
        try:
            await self.initialize()
            
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            result = await self._make_request(self.base_url, params=params)
            
            if "error" in result:
                return DataResponse(
                    success=False,
                    error=result["error"],
                    source="AlphaVantage"
                )
            
            quote = result.get("Global Quote", {})
            
            if not quote:
                return DataResponse(
                    success=False,
                    error="No se encontraron datos para el símbolo",
                    source="AlphaVantage"
                )
            
            # Procesar datos de la acción
            stock_data = {
                "symbol": quote.get("01. symbol", symbol),
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "volume": int(quote.get("06. volume", 0)),
                "previous_close": float(quote.get("08. previous close", 0)),
                "open": float(quote.get("02. open", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "timestamp": datetime.now().isoformat()
            }
            
            return DataResponse(
                success=True,
                data=stock_data,
                source="AlphaVantage",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error obteniendo precio de acción: {str(e)}",
                source="AlphaVantage"
            )
    
    async def get_crypto_price(self, symbol: str = "BTC") -> DataResponse:
        """Obtener precio de criptomoneda"""
        try:
            await self.initialize()
            
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": symbol,
                "to_currency": "USD",
                "apikey": self.api_key
            }
            
            result = await self._make_request(self.base_url, params=params)
            
            if "error" in result:
                return DataResponse(
                    success=False,
                    error=result["error"],
                    source="AlphaVantage"
                )
            
            exchange_rate = result.get("Realtime Currency Exchange Rate", {})
            
            if not exchange_rate:
                return DataResponse(
                    success=False,
                    error="No se encontraron datos para la criptomoneda",
                    source="AlphaVantage"
                )
            
            # Procesar datos de criptomoneda
            crypto_data = {
                "symbol": exchange_rate.get("1. From_Currency Code", symbol),
                "name": exchange_rate.get("2. From_Currency Name", ""),
                "price_usd": float(exchange_rate.get("5. Exchange Rate", 0)),
                "last_updated": exchange_rate.get("6. Last Refreshed", ""),
                "timezone": exchange_rate.get("7. Time Zone", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            return DataResponse(
                success=True,
                data=crypto_data,
                source="AlphaVantage",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error obteniendo precio de criptomoneda: {str(e)}",
                source="AlphaVantage"
            )


class SearchConnector(BaseConnector):
    """Conector para búsquedas web"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.google_search_api_key or config.serper_api_key
        self.base_url = "https://serpapi.com/search"
    
    async def search_web(self, query: str, num_results: int = 10) -> DataResponse:
        """Realizar búsqueda web"""
        try:
            await self.initialize()
            
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "gl": "es",  # Geolocalización
                "hl": "es"   # Idioma
            }
            
            result = await self._make_request(self.base_url, params=params)
            
            if "error" in result:
                return DataResponse(
                    success=False,
                    error=result["error"],
                    source="SerpAPI"
                )
            
            # Procesar resultados de búsqueda
            search_data = {
                "query": query,
                "total_results": result.get("search_information", {}).get("total_results", 0),
                "results": []
            }
            
            for item in result.get("organic_results", []):
                search_result = {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "position": item.get("position", 0),
                    "source": item.get("source", ""),
                    "relevance_score": 0.0
                }
                search_data["results"].append(search_result)
            
            return DataResponse(
                success=True,
                data=search_data,
                source="SerpAPI",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error realizando búsqueda: {str(e)}",
                source="SerpAPI"
            )


class DataConnectorManager:
    """Gestor de conectores de datos"""
    
    def __init__(self):
        self.config = get_config()
        self.connectors = {}
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar todos los conectores"""
        try:
            # Inicializar conectores disponibles
            if self.config.weather_api_key or self.config.openweather_api_key:
                self.connectors[DataSource.WEATHER] = WeatherConnector(self.config)
            
            if self.config.news_api_key or self.config.gnews_api_key:
                self.connectors[DataSource.NEWS] = NewsConnector(self.config)
            
            if self.config.alpha_vantage_api_key:
                self.connectors[DataSource.FINANCE] = FinanceConnector(self.config)
            
            if self.config.google_search_api_key or self.config.serper_api_key:
                self.connectors[DataSource.SEARCH] = SearchConnector(self.config)
            
            # Inicializar sesiones
            for connector in self.connectors.values():
                await connector.initialize()
            
            self.is_initialized = True
            
        except Exception as e:
            raise Exception(f"Error inicializando conectores: {e}")
    
    async def close(self):
        """Cerrar todos los conectores"""
        for connector in self.connectors.values():
            await connector.close()
        self.connectors.clear()
        self.is_initialized = False
    
    async def get_data(self, request: DataRequest) -> DataResponse:
        """Obtener datos de una fuente específica"""
        if not self.is_initialized:
            await self.initialize()
        
        connector = self.connectors.get(request.source)
        if not connector:
            return DataResponse(
                success=False,
                error=f"Conector no disponible para {request.source}",
                source=str(request.source)
            )
        
        try:
            if request.source == DataSource.WEATHER:
                if "forecast" in request.query.lower():
                    return await connector.get_forecast(
                        request.parameters.get("city", ""),
                        request.parameters.get("days", 5)
                    )
                else:
                    return await connector.get_current_weather(
                        request.parameters.get("city", ""),
                        request.parameters.get("country_code", "")
                    )
            
            elif request.source == DataSource.NEWS:
                if "headlines" in request.query.lower():
                    return await connector.get_top_headlines(
                        request.parameters.get("country", "es"),
                        request.parameters.get("category", "general")
                    )
                else:
                    return await connector.get_news(
                        request.query,
                        request.parameters.get("language", "es"),
                        request.parameters.get("sort_by", "publishedAt"),
                        request.parameters.get("page_size", 10)
                    )
            
            elif request.source == DataSource.FINANCE:
                if "crypto" in request.query.lower() or "bitcoin" in request.query.lower():
                    return await connector.get_crypto_price(
                        request.parameters.get("symbol", "BTC")
                    )
                else:
                    return await connector.get_stock_price(
                        request.parameters.get("symbol", "")
                    )
            
            elif request.source == DataSource.SEARCH:
                return await connector.search_web(
                    request.query,
                    request.parameters.get("num_results", 10)
                )
            
            else:
                return DataResponse(
                    success=False,
                    error=f"Fuente de datos no soportada: {request.source}",
                    source=str(request.source)
                )
                
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Error obteniendo datos: {str(e)}",
                source=str(request.source)
            )
    
    def get_available_sources(self) -> List[DataSource]:
        """Obtener fuentes de datos disponibles"""
        return list(self.connectors.keys())
    
    async def get_multiple_data(self, requests: List[DataRequest]) -> List[DataResponse]:
        """Obtener datos de múltiples fuentes en paralelo"""
        tasks = [self.get_data(request) for request in requests]
        return await asyncio.gather(*tasks)


# Instancia global del gestor de conectores
_connector_manager = None


def get_connector_manager() -> DataConnectorManager:
    """Obtener instancia global del gestor de conectores"""
    global _connector_manager
    if _connector_manager is None:
        _connector_manager = DataConnectorManager()
    return _connector_manager 