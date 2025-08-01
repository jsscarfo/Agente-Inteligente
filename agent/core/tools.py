"""
🛠️ Herramientas del Agente Inteligente

Este módulo proporciona herramientas especializadas que el agente puede utilizar
para realizar tareas específicas como cálculos, análisis de texto, procesamiento
de datos, y otras operaciones útiles.
"""

import asyncio
import re
import json
import math
import statistics
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

from .connectors import DataRequest, DataResponse, DataSource, get_connector_manager


class ToolType(str, Enum):
    """Tipos de herramientas"""
    CALCULATOR = "calculator"
    TEXT_ANALYZER = "text_analyzer"
    DATA_PROCESSOR = "data_processor"
    FILE_HANDLER = "file_handler"
    WEB_SCRAPER = "web_scraper"
    TRANSLATOR = "translator"
    SCHEDULER = "scheduler"
    EMAIL_SENDER = "email_sender"


@dataclass
class ToolRequest:
    """Solicitud de herramienta"""
    tool_type: ToolType
    operation: str
    parameters: Dict[str, Any]
    timeout: int = 30


@dataclass
class ToolResponse:
    """Respuesta de herramienta"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseTool:
    """Herramienta base"""
    
    def __init__(self):
        self.name = "base_tool"
        self.description = "Herramienta base"
        self.version = "1.0.0"
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Ejecutar la herramienta"""
        raise NotImplementedError("Subclases deben implementar execute()")
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de entrada"""
        return True


class CalculatorTool(BaseTool):
    """Herramienta de cálculos matemáticos"""
    
    def __init__(self):
        super().__init__()
        self.name = "calculator"
        self.description = "Realiza cálculos matemáticos complejos"
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Ejecutar cálculos matemáticos"""
        start_time = datetime.now()
        
        try:
            operation = parameters.get("operation", "")
            values = parameters.get("values", [])
            
            if not operation or not values:
                return ToolResponse(
                    success=False,
                    error="Se requiere operación y valores"
                )
            
            result = None
            
            if operation == "add":
                result = sum(float(v) for v in values)
            elif operation == "subtract":
                if len(values) < 2:
                    return ToolResponse(success=False, error="Se requieren al menos 2 valores")
                result = float(values[0]) - sum(float(v) for v in values[1:])
            elif operation == "multiply":
                result = math.prod(float(v) for v in values)
            elif operation == "divide":
                if len(values) < 2:
                    return ToolResponse(success=False, error="Se requieren al menos 2 valores")
                result = float(values[0]) / float(values[1])
            elif operation == "power":
                if len(values) != 2:
                    return ToolResponse(success=False, error="Se requieren exactamente 2 valores")
                result = float(values[0]) ** float(values[1])
            elif operation == "sqrt":
                if len(values) != 1:
                    return ToolResponse(success=False, error="Se requiere exactamente 1 valor")
                result = math.sqrt(float(values[0]))
            elif operation == "log":
                if len(values) != 2:
                    return ToolResponse(success=False, error="Se requieren exactamente 2 valores")
                result = math.log(float(values[0]), float(values[1]))
            elif operation == "sin":
                if len(values) != 1:
                    return ToolResponse(success=False, error="Se requiere exactamente 1 valor")
                result = math.sin(float(values[0]))
            elif operation == "cos":
                if len(values) != 1:
                    return ToolResponse(success=False, error="Se requiere exactamente 1 valor")
                result = math.cos(float(values[0]))
            elif operation == "tan":
                if len(values) != 1:
                    return ToolResponse(success=False, error="Se requiere exactamente 1 valor")
                result = math.tan(float(values[0]))
            elif operation == "average":
                result = statistics.mean(float(v) for v in values)
            elif operation == "median":
                result = statistics.median(float(v) for v in values)
            elif operation == "std":
                result = statistics.stdev(float(v) for v in values)
            elif operation == "max":
                result = max(float(v) for v in values)
            elif operation == "min":
                result = min(float(v) for v in values)
            else:
                return ToolResponse(
                    success=False,
                    error=f"Operación no soportada: {operation}"
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "operation": operation,
                    "input_values": values,
                    "result_type": type(result).__name__
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                error=f"Error en cálculo: {str(e)}"
            )


class TextAnalyzerTool(BaseTool):
    """Herramienta de análisis de texto"""
    
    def __init__(self):
        super().__init__()
        self.name = "text_analyzer"
        self.description = "Analiza texto y extrae información útil"
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Ejecutar análisis de texto"""
        start_time = datetime.now()
        
        try:
            text = parameters.get("text", "")
            analysis_type = parameters.get("analysis_type", "basic")
            
            if not text:
                return ToolResponse(
                    success=False,
                    error="Se requiere texto para analizar"
                )
            
            result = {}
            
            if analysis_type == "basic" or analysis_type == "all":
                # Análisis básico
                result["basic"] = self._basic_analysis(text)
            
            if analysis_type == "sentiment" or analysis_type == "all":
                # Análisis de sentimiento (simplificado)
                result["sentiment"] = self._sentiment_analysis(text)
            
            if analysis_type == "keywords" or analysis_type == "all":
                # Extracción de palabras clave
                result["keywords"] = self._extract_keywords(text)
            
            if analysis_type == "summary" or analysis_type == "all":
                # Resumen del texto
                result["summary"] = self._generate_summary(text)
            
            if analysis_type == "entities" or analysis_type == "all":
                # Extracción de entidades
                result["entities"] = self._extract_entities(text)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "analysis_type": analysis_type,
                    "text_length": len(text),
                    "languages_detected": self._detect_languages(text)
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                error=f"Error en análisis de texto: {str(e)}"
            )
    
    def _basic_analysis(self, text: str) -> Dict[str, Any]:
        """Análisis básico del texto"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "average_sentence_length": len(words) / len(sentences) if sentences else 0,
            "unique_words": len(set(words)),
            "vocabulary_diversity": len(set(words)) / len(words) if words else 0
        }
    
    def _sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Análisis de sentimiento simplificado"""
        positive_words = ["bueno", "excelente", "fantástico", "maravilloso", "genial", "perfecto", "amazing", "great", "wonderful"]
        negative_words = ["malo", "terrible", "horrible", "pésimo", "awful", "bad", "terrible", "horrible"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        return {
            "positive_words": positive_count,
            "negative_words": negative_count,
            "sentiment_score": sentiment_score,
            "sentiment_label": "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral"
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extraer palabras clave"""
        # Palabras comunes a excluir
        stop_words = {"el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le", "da", "su", "por", "son", "con", "para", "al", "del", "los", "las", "una", "como", "pero", "sus", "me", "hasta", "hay", "donde", "han", "quien", "están", "estado", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Ordenar por frecuencia y devolver las top 10
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return [word for word, freq in keywords]
    
    def _generate_summary(self, text: str) -> str:
        """Generar resumen del texto"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            return text
        
        # Algoritmo simple: tomar las primeras 3 oraciones
        summary_sentences = sentences[:3]
        return ". ".join(summary_sentences) + "."
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extraer entidades del texto"""
        entities = {
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text),
            "phone_numbers": re.findall(r'\+?[\d\s\-\(\)]+', text),
            "dates": re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text),
            "numbers": re.findall(r'\b\d+(?:\.\d+)?\b', text)
        }
        
        return entities
    
    def _detect_languages(self, text: str) -> List[str]:
        """Detectar idiomas en el texto"""
        languages = []
        
        # Detección simple basada en palabras comunes
        spanish_words = ["el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no"]
        english_words = ["the", "and", "of", "to", "a", "in", "is", "it", "you", "that", "he"]
        
        text_lower = text.lower()
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if spanish_count > english_count:
            languages.append("es")
        if english_count > spanish_count:
            languages.append("en")
        
        return languages


class DataProcessorTool(BaseTool):
    """Herramienta de procesamiento de datos"""
    
    def __init__(self):
        super().__init__()
        self.name = "data_processor"
        self.description = "Procesa y analiza datos estructurados"
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Ejecutar procesamiento de datos"""
        start_time = datetime.now()
        
        try:
            data = parameters.get("data", [])
            operation = parameters.get("operation", "")
            
            if not data:
                return ToolResponse(
                    success=False,
                    error="Se requieren datos para procesar"
                )
            
            result = {}
            
            if operation == "statistics" or operation == "all":
                result["statistics"] = self._calculate_statistics(data)
            
            if operation == "filter" or operation == "all":
                filter_criteria = parameters.get("filter_criteria", {})
                result["filtered_data"] = self._filter_data(data, filter_criteria)
            
            if operation == "sort" or operation == "all":
                sort_key = parameters.get("sort_key", "")
                sort_order = parameters.get("sort_order", "asc")
                result["sorted_data"] = self._sort_data(data, sort_key, sort_order)
            
            if operation == "group" or operation == "all":
                group_key = parameters.get("group_key", "")
                result["grouped_data"] = self._group_data(data, group_key)
            
            if operation == "aggregate" or operation == "all":
                aggregate_config = parameters.get("aggregate_config", {})
                result["aggregated_data"] = self._aggregate_data(data, aggregate_config)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "operation": operation,
                    "data_size": len(data),
                    "data_type": type(data).__name__
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                error=f"Error en procesamiento de datos: {str(e)}"
            )
    
    def _calculate_statistics(self, data: List[Any]) -> Dict[str, Any]:
        """Calcular estadísticas de los datos"""
        if not data:
            return {}
        
        # Convertir a números si es posible
        numeric_data = []
        for item in data:
            try:
                if isinstance(item, (int, float)):
                    numeric_data.append(item)
                elif isinstance(item, str):
                    numeric_data.append(float(item))
                elif isinstance(item, dict):
                    # Intentar extraer valores numéricos
                    for value in item.values():
                        try:
                            numeric_data.append(float(value))
                        except:
                            pass
            except:
                pass
        
        if not numeric_data:
            return {"message": "No se encontraron datos numéricos"}
        
        return {
            "count": len(numeric_data),
            "sum": sum(numeric_data),
            "mean": statistics.mean(numeric_data),
            "median": statistics.median(numeric_data),
            "min": min(numeric_data),
            "max": max(numeric_data),
            "std": statistics.stdev(numeric_data) if len(numeric_data) > 1 else 0,
            "variance": statistics.variance(numeric_data) if len(numeric_data) > 1 else 0
        }
    
    def _filter_data(self, data: List[Dict], criteria: Dict) -> List[Dict]:
        """Filtrar datos según criterios"""
        filtered_data = []
        
        for item in data:
            if isinstance(item, dict):
                matches = True
                for key, value in criteria.items():
                    if key in item:
                        if isinstance(value, dict):
                            # Criterios de comparación
                            if "equals" in value and item[key] != value["equals"]:
                                matches = False
                            elif "contains" in value and value["contains"] not in str(item[key]):
                                matches = False
                            elif "greater_than" in value and item[key] <= value["greater_than"]:
                                matches = False
                            elif "less_than" in value and item[key] >= value["less_than"]:
                                matches = False
                        else:
                            # Comparación directa
                            if item[key] != value:
                                matches = False
                    else:
                        matches = False
                        break
                
                if matches:
                    filtered_data.append(item)
        
        return filtered_data
    
    def _sort_data(self, data: List[Dict], key: str, order: str = "asc") -> List[Dict]:
        """Ordenar datos"""
        if not key:
            return data
        
        reverse = order.lower() == "desc"
        
        try:
            return sorted(data, key=lambda x: x.get(key, 0), reverse=reverse)
        except:
            # Si falla la ordenación numérica, intentar ordenación alfabética
            return sorted(data, key=lambda x: str(x.get(key, "")), reverse=reverse)
    
    def _group_data(self, data: List[Dict], key: str) -> Dict[str, List[Dict]]:
        """Agrupar datos por clave"""
        if not key:
            return {}
        
        grouped = {}
        
        for item in data:
            if isinstance(item, dict) and key in item:
                group_value = str(item[key])
                if group_value not in grouped:
                    grouped[group_value] = []
                grouped[group_value].append(item)
        
        return grouped
    
    def _aggregate_data(self, data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Agregar datos según configuración"""
        if not config:
            return {}
        
        result = {}
        
        for field, operations in config.items():
            values = []
            for item in data:
                if isinstance(item, dict) and field in item:
                    try:
                        values.append(float(item[field]))
                    except:
                        pass
            
            if values:
                field_result = {}
                for operation in operations:
                    if operation == "sum":
                        field_result["sum"] = sum(values)
                    elif operation == "avg":
                        field_result["avg"] = statistics.mean(values)
                    elif operation == "min":
                        field_result["min"] = min(values)
                    elif operation == "max":
                        field_result["max"] = max(values)
                    elif operation == "count":
                        field_result["count"] = len(values)
                
                result[field] = field_result
        
        return result


class FileHandlerTool(BaseTool):
    """Herramienta de manejo de archivos"""
    
    def __init__(self):
        super().__init__()
        self.name = "file_handler"
        self.description = "Maneja operaciones de archivos"
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Ejecutar operaciones de archivos"""
        start_time = datetime.now()
        
        try:
            operation = parameters.get("operation", "")
            file_path = parameters.get("file_path", "")
            content = parameters.get("content", "")
            
            if not operation:
                return ToolResponse(
                    success=False,
                    error="Se requiere operación"
                )
            
            result = {}
            
            if operation == "read":
                result = await self._read_file(file_path)
            elif operation == "write":
                result = await self._write_file(file_path, content)
            elif operation == "append":
                result = await self._append_file(file_path, content)
            elif operation == "delete":
                result = await self._delete_file(file_path)
            elif operation == "list":
                directory = parameters.get("directory", ".")
                result = await self._list_files(directory)
            elif operation == "info":
                result = await self._get_file_info(file_path)
            else:
                return ToolResponse(
                    success=False,
                    error=f"Operación no soportada: {operation}"
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResponse(
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "operation": operation,
                    "file_path": file_path
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                error=f"Error en operación de archivo: {str(e)}"
            )
    
    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Leer archivo"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"Archivo no encontrado: {file_path}"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines()),
                "encoding": "utf-8"
            }
        except Exception as e:
            return {"error": f"Error leyendo archivo: {str(e)}"}
    
    async def _write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Escribir archivo"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "bytes_written": len(content.encode('utf-8')),
                "file_path": str(path.absolute())
            }
        except Exception as e:
            return {"error": f"Error escribiendo archivo: {str(e)}"}
    
    async def _append_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Añadir contenido a archivo"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "bytes_appended": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {"error": f"Error añadiendo al archivo: {str(e)}"}
    
    async def _delete_file(self, file_path: str) -> Dict[str, Any]:
        """Eliminar archivo"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"Archivo no encontrado: {file_path}"}
            
            path.unlink()
            return {"success": True}
        except Exception as e:
            return {"error": f"Error eliminando archivo: {str(e)}"}
    
    async def _list_files(self, directory: str) -> Dict[str, Any]:
        """Listar archivos en directorio"""
        try:
            path = Path(directory)
            if not path.exists():
                return {"error": f"Directorio no encontrado: {directory}"}
            
            files = []
            for item in path.iterdir():
                file_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                files.append(file_info)
            
            return {
                "directory": str(path.absolute()),
                "files": files,
                "total_files": len([f for f in files if f["type"] == "file"]),
                "total_directories": len([f for f in files if f["type"] == "directory"])
            }
        except Exception as e:
            return {"error": f"Error listando archivos: {str(e)}"}
    
    async def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Obtener información del archivo"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"Archivo no encontrado: {file_path}"}
            
            stat = path.stat()
            
            return {
                "name": path.name,
                "path": str(path.absolute()),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": path.is_file(),
                "is_directory": path.is_dir(),
                "extension": path.suffix
            }
        except Exception as e:
            return {"error": f"Error obteniendo información: {str(e)}"}


class ToolManager:
    """Gestor de herramientas"""
    
    def __init__(self):
        self.tools = {}
        self.is_initialized = False
    
    async def initialize(self):
        """Inicializar todas las herramientas"""
        try:
            # Registrar herramientas
            self.tools[ToolType.CALCULATOR] = CalculatorTool()
            self.tools[ToolType.TEXT_ANALYZER] = TextAnalyzerTool()
            self.tools[ToolType.DATA_PROCESSOR] = DataProcessorTool()
            self.tools[ToolType.FILE_HANDLER] = FileHandlerTool()
            
            self.is_initialized = True
            
        except Exception as e:
            raise Exception(f"Error inicializando herramientas: {e}")
    
    async def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """Ejecutar una herramienta específica"""
        if not self.is_initialized:
            await self.initialize()
        
        tool = self.tools.get(request.tool_type)
        if not tool:
            return ToolResponse(
                success=False,
                error=f"Herramienta no disponible: {request.tool_type}"
            )
        
        try:
            return await tool.execute(request.parameters)
        except Exception as e:
            return ToolResponse(
                success=False,
                error=f"Error ejecutando herramienta: {str(e)}"
            )
    
    def get_available_tools(self) -> List[ToolType]:
        """Obtener herramientas disponibles"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_type: ToolType) -> Dict[str, Any]:
        """Obtener información de una herramienta"""
        tool = self.tools.get(tool_type)
        if not tool:
            return {}
        
        return {
            "name": tool.name,
            "description": tool.description,
            "version": tool.version,
            "type": tool_type
        }


# Instancia global del gestor de herramientas
_tool_manager = None


def get_tool_manager() -> ToolManager:
    """Obtener instancia global del gestor de herramientas"""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager 