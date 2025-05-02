import mysql.connector
from mysql.connector import pooling
from functools import lru_cache
import time
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager
import threading
from datetime import datetime, timedelta

# Configuración del pool de conexiones
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "mi_contraseña123",
    "database": "inventario_facturacion",
    "pool_name": "mypool",
    "pool_size": 5
}

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
        self.cache = {}
        self.cache_timeout = {}
        self.default_timeout = 300  # 5 minutos

    @contextmanager
    def get_connection(self):
        connection = self.connection_pool.get_connection()
        try:
            yield connection
        finally:
            connection.close()

    def _is_cache_valid(self, cache_key: str) -> bool:
        if cache_key not in self.cache or cache_key not in self.cache_timeout:
            return False
        return datetime.now() < self.cache_timeout[cache_key]

    def _set_cache(self, cache_key: str, data: Any, timeout: int = None):
        self.cache[cache_key] = data
        self.cache_timeout[cache_key] = datetime.now() + timedelta(seconds=timeout or self.default_timeout)

    def _clear_expired_cache(self):
        now = datetime.now()
        expired_keys = [k for k, v in self.cache_timeout.items() if now > v]
        for k in expired_keys:
            del self.cache[k]
            del self.cache_timeout[k]

    @lru_cache(maxsize=128)
    def get_producto_by_id(self, producto_id: int) -> Optional[Dict]:
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, pr.nombre as proveedor_nombre 
                FROM productos p 
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.proveedor_id 
                WHERE p.producto_id = %s
            """, (producto_id,))
            return cursor.fetchone()

    def get_productos(self, use_cache: bool = True) -> List[Dict]:
        cache_key = "productos_list"
        
        if use_cache and self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, pr.nombre as proveedor_nombre 
                FROM productos p 
                LEFT JOIN proveedores pr ON p.proveedor_id = pr.proveedor_id
            """)
            productos = cursor.fetchall()
            
            if use_cache:
                self._set_cache(cache_key, productos)
            
            return productos

    def update_producto(self, producto_id: int, datos: Dict):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            query = """
                UPDATE productos 
                SET nombre = %s, categoria = %s, precio = %s, stock = %s, 
                    proveedor_id = %s, descripcion = %s 
                WHERE producto_id = %s
            """
            cursor.execute(query, (
                datos['nombre'], datos['categoria'], datos['precio'],
                datos['stock'], datos['proveedor_id'], datos['descripcion'],
                producto_id
            ))
            connection.commit()
            
            # Invalidar caché relacionado
            self.get_producto_by_id.cache_clear()
            self.cache.pop("productos_list", None)

    def execute_batch(self, query: str, params: List[Tuple]):
        """Ejecuta múltiples operaciones en lote"""
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.executemany(query, params)
            connection.commit()

    def get_ventas_dashboard(self) -> Dict[str, Any]:
        """Obtiene estadísticas para el dashboard con una sola consulta optimizada"""
        cache_key = "dashboard_stats"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM productos) as total_productos,
                    (SELECT SUM(stock) FROM productos) as total_stock,
                    (SELECT COUNT(*) FROM pedidos) as total_ventas,
                    (SELECT SUM(total) FROM pedidos) as total_ingresos,
                    (SELECT COUNT(*) FROM productos WHERE stock < 5) as productos_bajo_stock
                FROM dual
            """)
            stats = cursor.fetchone()
            
            # Obtener ventas por día para el gráfico
            cursor.execute("""
                SELECT DATE(fecha) as fecha, COUNT(*) as num_ventas, SUM(total) as total_ventas
                FROM pedidos 
                WHERE fecha >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
                GROUP BY DATE(fecha)
                ORDER BY fecha DESC
            """)
            ventas_por_dia = cursor.fetchall()
            
            resultado = {
                "stats": stats,
                "ventas_por_dia": ventas_por_dia
            }
            
            self._set_cache(cache_key, resultado, timeout=300)  # 5 minutos
            return resultado

    def __del__(self):
        """Limpieza al destruir la instancia"""
        self._clear_expired_cache() 