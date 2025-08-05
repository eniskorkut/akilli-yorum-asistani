"""
FlaskApplication.py - Basit Flask API

Bu dosya, RAG sorgu sistemi için basit bir Flask API oluşturur.
FastAPI'nin karmaşıklığından kaçınarak temel işlevselliği sağlar.
"""

from flask import Flask, request, jsonify
import time
import psutil
import os
from datetime import datetime

from DI import configure_container
from Logger import Logger
from Config import Config


class FlaskApplication:
    """
    Basit Flask API uygulaması
    
    Bu sınıf, temel API endpoint'lerini sağlar ve
    mevcut Application Layer'ı kullanır.
    """
    
    def __init__(self):
        """Uygulamayı başlatır"""
        self.app = Flask(__name__)
        self.start_time = time.time()
        self._setup_routes()
        Logger.info("Flask uygulaması başlatıldı")
    
    def _setup_routes(self):
        """Route'ları ayarlar"""
        
        @self.app.route('/', methods=['GET'])
        def root():
            """Ana sayfa"""
            return jsonify({
                "message": "Akıllı Yorum Asistanı API'ye Hoş Geldiniz",
                "version": "1.0.0",
                "status": "running",
                "endpoints": {
                    "health": "/api/v1/health/",
                    "query": "/api/v1/query/",
                    "batch_query": "/api/v1/query/batch"
                }
            })
        
        @self.app.route('/api/v1/health/', methods=['GET'])
        def health_check():
            """Sağlık kontrolü"""
            try:
                uptime = time.time() - self.start_time
                memory_usage = psutil.virtual_memory().percent
                cpu_usage = psutil.cpu_percent(interval=1)
                
                return jsonify({
                    "status": "healthy",
                    "timestamp": time.time(),
                    "version": "1.0.0",
                    "uptime": uptime,
                    "memory_usage": memory_usage,
                    "cpu_usage": cpu_usage
                })
            except Exception as e:
                Logger.error(f"Sağlık kontrolü hatası: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v1/query/', methods=['POST'])
        def query_product():
            """Tekil sorgu endpoint'i"""
            try:
                start_time = time.time()
                
                # Request data'sını al
                data = request.get_json()
                if not data:
                    return jsonify({"error": "JSON data gerekli"}), 400
                
                question = data.get('question')
                product_url = data.get('product_url')
                max_reviews = data.get('max_reviews')
                use_mocks = data.get('use_mocks', False)
                
                if not question:
                    return jsonify({"error": "question alanı gerekli"}), 400
                
                Logger.info(f"Tekil sorgu isteği alındı: {question}")
                
                # DI Container'ı konfigüre et
                container = configure_container(use_mocks=use_mocks)
                app_service = container.get_query_application_service()
                
                # Sorgu parametrelerini hazırla
                kwargs = {}
                if product_url:
                    kwargs['product_url'] = product_url
                if max_reviews:
                    kwargs['max_reviews'] = max_reviews
                if use_mocks:
                    kwargs['use_mocks'] = True
                
                # Application Service ile sorgu yap
                result = app_service.query_product(question, **kwargs)
                
                processing_time = time.time() - start_time
                
                if result.get('success'):
                    response = {
                        "success": True,
                        "answer": result.get('answer'),
                        "question": result.get('question'),
                        "total_reviews": result.get('total_reviews', 0),
                        "used_reviews": result.get('used_reviews', 0),
                        "processing_time": result.get('processing_time', processing_time),
                        "timestamp": result.get('timestamp'),
                        "metadata": result.get('metadata', {})
                    }
                    
                    Logger.info(f"Tekil sorgu başarıyla tamamlandı: {processing_time:.2f}s")
                    return jsonify(response)
                else:
                    error = result.get('error', {})
                    Logger.error(f"Tekil sorgu hatası: {error}")
                    return jsonify({"success": False, "error": error}), 400
                    
            except Exception as e:
                Logger.error(f"Tekil sorgu beklenmeyen hata: {e}")
                return jsonify({
                    "success": False,
                    "error": {
                        "error_code": "INTERNAL_ERROR",
                        "message": "Beklenmeyen bir hata oluştu",
                        "details": str(e)
                    }
                }), 500
        
        @self.app.route('/api/v1/query/batch', methods=['POST'])
        def batch_query_products():
            """Toplu sorgu endpoint'i"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "JSON data gerekli"}), 400
                
                queries = data.get('queries', [])
                if not queries:
                    return jsonify({"error": "queries listesi gerekli"}), 400
                
                Logger.info(f"Toplu sorgu isteği alındı: {len(queries)} sorgu")
                
                # DI Container'ı konfigüre et
                use_mocks = data.get('use_mocks', False)
                container = configure_container(use_mocks=use_mocks)
                app_service = container.get_query_application_service()
                
                results = []
                for query_data in queries:
                    question = query_data.get('question')
                    product_url = query_data.get('product_url')
                    max_reviews = query_data.get('max_reviews')
                    
                    if not question:
                        results.append({
                            "success": False,
                            "error": "question alanı gerekli"
                        })
                        continue
                    
                    # Sorgu parametrelerini hazırla
                    kwargs = {}
                    if product_url:
                        kwargs['product_url'] = product_url
                    if max_reviews:
                        kwargs['max_reviews'] = max_reviews
                    if use_mocks:
                        kwargs['use_mocks'] = True
                    
                    # Sorgu yap
                    result = app_service.query_product(question, **kwargs)
                    results.append(result)
                
                Logger.info(f"Toplu sorgu tamamlandı: {len(results)} sonuç")
                return jsonify({
                    "success": True,
                    "results": results,
                    "total_queries": len(queries),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                Logger.error(f"Toplu sorgu beklenmeyen hata: {e}")
                return jsonify({
                    "success": False,
                    "error": {
                        "error_code": "INTERNAL_ERROR",
                        "message": "Beklenmeyen bir hata oluştu",
                        "details": str(e)
                    }
                }), 500
    
    def run(self, host='0.0.0.0', port=8000, debug=False):
        """Uygulamayı çalıştırır"""
        Logger.info(f"Flask uygulaması başlatılıyor: {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# Global application instance
flask_app = FlaskApplication()


def get_flask_app():
    """Flask uygulaması instance'ını döndürür"""
    return flask_app.app


if __name__ == "__main__":
    # Konfigürasyonu doğrula
    try:
        Config.validate()
        Logger.info("Konfigürasyon doğrulandı")
    except Exception as e:
        Logger.critical(f"Konfigürasyon hatası: {e}")
        exit(1)
    
    # Uygulamayı başlat
    flask_app.run(debug=False) 