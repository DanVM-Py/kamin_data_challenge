# SQL Analytics Infrastructure
import pandas as pd
import duckdb
from pathlib import Path
from typing import Dict, Optional
import logging

class SQLAnalytics:
    def __init__(self, processed_data_path: Path, output_path: Path):
        self.processed_path = processed_data_path
        self.output_path = output_path
        self.output_path.mkdir(exist_ok=True)
        
        # Path para consultas SQL
        self.queries_path = Path(__file__).parent.parent / 'queries' / 'DML'
        
        # Inicializar DuckDB in-memory
        self.conn = duckdb.connect(':memory:')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🚀 SQLAnalytics inicializado")
        self.logger.info(f"📁 Input: {self.processed_path}")
        self.logger.info(f"📁 Output: {self.output_path}")
        self.logger.info(f"📄 Queries: {self.queries_path}")
    
    def load_csvs_to_sql(self):
        """CSV → DF → SQL Tables"""
        self.logger.info("📥 Cargando CSVs a tablas SQL...")
        
        csv_files = {
            'clients': 'clients.csv',
            'events': 'events.csv', 
            'retry_logs': 'retry_logs.csv'
        }
        
        for table_name, csv_file in csv_files.items():
            csv_path = self.processed_path / csv_file
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                self.df_to_sql(df, table_name)
                self.logger.info(f"✅ {table_name}: {len(df)} rows cargadas")
            else:
                self.logger.warning(f"⚠️ {csv_file} no encontrado")
    
    def df_to_sql(self, df: pd.DataFrame, table_name: str):
        """DF → SQL Table"""
        self.conn.register(table_name, df)
        self.logger.debug(f"📊 Tabla '{table_name}' registrada en SQL")
    
    def _load_sql_query(self, sql_filename: str) -> str:
        """Cargar consulta SQL desde archivo"""
        sql_file = self.queries_path / sql_filename
        
        if not sql_file.exists():
            raise FileNotFoundError(f"❌ Archivo SQL no encontrado: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            query = f.read()
        
        self.logger.debug(f"📄 Query cargada desde: {sql_filename}")
        return query
    
    def sql_to_df(self, query: str) -> pd.DataFrame:
        """SQL Query → DF"""
        try:
            df = self.conn.execute(query).df()
            self.logger.debug(f"🔍 Query ejecutado: {len(df)} rows retornadas")
            return df
        except Exception as e:
            self.logger.error(f"❌ Error en query SQL: {e}")
            raise
    
    def df_to_csv(self, df: pd.DataFrame, filename: str):
        """DF → CSV"""
        output_path = self.output_path / filename
        df.to_csv(output_path, index=False)
        
        size_mb = output_path.stat().st_size / (1024 * 1024)
        self.logger.info(f"💾 {filename}: {len(df)} rows exportadas ({size_mb:.2f} MB)")
    
    def create_analytics_table(self, table_type: str) -> bool:
        """
        Crear tabla analítica de forma parametrizada con manejo de errores
        
        Args:
            table_type (str): Tipo de tabla a crear ('client' o 'event')
            
        Returns:
            bool: True si se creó exitosamente, False si hubo error
        """
        
        # Mapeo de configuraciones por tipo de tabla
        table_configs = {
            'client': {
                'sql_file': 'client_summary.sql',
                'output_file': 'client_summary.csv',
                'description': 'resumen de clientes'
            },
            'event': {
                'sql_file': 'event_time_series.sql', 
                'output_file': 'event_time_series.csv',
                'description': 'series temporales de eventos'
            }
        }
        
        # Validar tipo de tabla
        if table_type not in table_configs:
            self.logger.error(f"❌ Tipo de tabla '{table_type}' no válido. Opciones: {list(table_configs.keys())}")
            return False
            
        config = table_configs[table_type]
        
        try:
            self.logger.info(f"🔨 Creando tabla de {config['description']}...")
            
            # Cargar query SQL
            query = self._load_sql_query(config['sql_file'])
            self.logger.debug(f"📄 Query cargada desde {config['sql_file']}")
            
            # Ejecutar query y convertir a DataFrame
            df = self.sql_to_df(query)
            self.logger.info(f"✅ Query ejecutada: {len(df)} rows generadas")
            
            # Exportar a CSV
            self.df_to_csv(df, config['output_file'])
            self.logger.info(f"💾 Tabla {config['output_file']} creada exitosamente")
            
            return True
            
        except FileNotFoundError as e:
            self.logger.error(f"❌ Archivo SQL no encontrado: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error creando tabla {table_type}: {str(e)}")
            self.logger.debug(f"📋 Detalles del error: {type(e).__name__}")
            return False

    
    def show_table_info(self):
        """Mostrar información de las tablas cargadas"""
        self.logger.info("📋 Información de tablas SQL:")
        
        tables = ['clients', 'events', 'retry_logs']
        for table in tables:
            try:
                info = self.conn.execute(f"SELECT COUNT(1) as rows FROM {table}").fetchone()
                columns = self.conn.execute(f"DESCRIBE {table}").df()
                
                print(f"\n📊 Tabla: {table}")
                print(f"   Rows: {info[0]:,}")
                print(f"   Columns: {len(columns)}")
                print(f"   Schema: {', '.join(columns['column_name'].tolist())}")
                
            except Exception as e:
                print(f"❌ Error accediendo tabla {table}: {e}")

    
    def generate_analytics_tables(self) -> dict:
        """
        Generar todas las tablas analíticas con reporte de resultados
        
        Returns:
            dict: Reporte de éxito/fallo de cada tabla generada
        """
        self.logger.info("🎯 Generando tablas analíticas...")
        print("=" * 50)
        
        # 1. Cargar datos base
        self.load_csvs_to_sql()
        
        # 2. Mostrar info de tablas
        self.show_table_info()
        
        # 3. Crear tablas analíticas con reporte de resultados
        results = {}
        tables_to_create = ['client', 'event']
        
        print(f"\n🔨 Creando {len(tables_to_create)} tablas analíticas...")
        print("-" * 30)
        
        for table_type in tables_to_create:
            success = self.create_analytics_table(table_type)
            results[table_type] = success
            
            # Mostrar resultado inmediato
            status_emoji = "✅" if success else "❌"
            table_name = f"{table_type}_summary.csv" if table_type == 'client' else f"{table_type}_time_series.csv"
            print(f"{status_emoji} {table_name}: {'ÉXITO' if success else 'FALLO'}")
        
        # 4. Reporte final
        successful_tables = sum(results.values())
        total_tables = len(results)
        
        print(f"\n📊 REPORTE FINAL:")
        print(f"   ✅ Exitosas: {successful_tables}/{total_tables}")
        print(f"   ❌ Fallidas: {total_tables - successful_tables}/{total_tables}")
        
        if successful_tables == total_tables:
            self.logger.info("🎉 ¡Todas las tablas generadas exitosamente!")
        else:
            self.logger.warning(f"⚠️ {total_tables - successful_tables} tabla(s) fallaron")
        
        return results
    
    def close(self):
        """Cerrar conexión DuckDB"""
        self.conn.close()
        self.logger.info("🔌 Conexión DuckDB cerrada")


def main():
    """Función principal"""
    PROCESSED_DATA = Path('/app/data/processed')
    ANALYTICS_OUTPUT = Path('/app/data/analytics')
    
    analytics = SQLAnalytics(PROCESSED_DATA, ANALYTICS_OUTPUT)
    
    try:
        results = analytics.generate_analytics_tables()
        
        print(f"\n🎯 Tablas generadas en: {ANALYTICS_OUTPUT}")
        print("=" * 50)
        for file in sorted(ANALYTICS_OUTPUT.glob('*.csv')):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"📄 {file.name:<25} ({size_mb:.2f} MB)")
            
    finally:
        analytics.close()


if __name__ == "__main__":
    main() 